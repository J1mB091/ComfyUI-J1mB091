import torch
import numpy as np
from typing import Any, Tuple, Optional


from typing import Any, Optional, Tuple, Union, Dict, TYPE_CHECKING
import logging

logger = logging.getLogger(__name__)

if TYPE_CHECKING:
    import torch
    from torch import Tensor
else:
    try:
        import torch
        from torch import Tensor
    except ImportError:
        print("Error: PyTorch is not installed. Please install PyTorch to use this module.")
        raise

class VideoBaseNode:
    """Base class for video processing nodes."""
    
    @staticmethod
    def ensure_tensor(images: Any) -> "Tensor":
        """
        Ensure input is a tensor and on CPU.
        
        Args:
            images: Input image batch
            
        Returns:
            torch.Tensor: Image batch as tensor
            
        Raises:
            ValueError: If input cannot be converted to tensor
        """
        try:
            # Check if already a tensor
            if torch.is_tensor(images):
                return images.cpu()
            
            # Try getting CPU version if available
            if hasattr(images, 'cpu'):
                images = images.cpu()
                
            # Convert to tensor if not already
            if not torch.is_tensor(images):
                images = torch.tensor(images)
                
            return images.cpu()
        except Exception as e:
            logger.error(f"Failed to convert input to tensor: {e}")
            raise ValueError(f"Could not convert input to tensor: {e}")

    @staticmethod 
    def create_empty_batch(shape: Optional[Tuple[int, ...]] = None) -> "Tensor":
        """
        Create an empty image batch with given shape or default.
        
        Args:
            shape: Optional shape for the empty batch
            
        Returns:
            torch.Tensor: Empty image batch (0, H, W, C)
            
        Raises:
            RuntimeError: If empty batch creation fails
        """
        try:
            if shape is None or len(shape) < 2:
                # Default shape for image batch (0, H, W, C)
                return torch.zeros((0, 512, 512, 3))
            # Use provided shape but keep batch dimension as 0
            return torch.zeros((0, *shape[1:]))
        except Exception as e:
            logger.error(f"Failed to create empty batch: {e}")
            raise RuntimeError(f"Could not create empty batch: {e}")


# ComfyUI Nodes
class ExtractLastFrame(VideoBaseNode):
    """Extract the last frame from an image batch."""

    @classmethod
    def INPUT_TYPES(cls) -> Dict[str, Any]:
        """Define the input types and tooltips."""
        return {
            "required": {
                "images": ("IMAGE", {"tooltip": "Input image batch to extract last frame from"}),
            }
        }

    RETURN_TYPES = ("IMAGE",)
    RETURN_NAMES = ("last_frame",)
    FUNCTION = "extract_last_frame"
    CATEGORY = "J1mB091/Video"

    def extract_last_frame(self, images: Any) -> Tuple["Tensor"]:
        """
        Extract the last frame from an image batch.

        Args:
            images: Input image batch (tensor)

        Returns:
            Tuple[Tensor]: Last frame as single image tensor
            
        Raises:
            ValueError: If input cannot be converted to tensor
        """
        try:
            # Ensure input is a tensor
            images = self.ensure_tensor(images)
            
            # Extract last frame if batch is not empty
            if images.shape[0] > 0:
                last_frame = images[-1:]  # Keep as batch with 1 image
                return (last_frame,)
            
            # Return empty batch with same dimensions if input is empty
            return (self.create_empty_batch(images.shape),)

        except Exception as e:
            logger.error(f"Error extracting last frame: {e}")
            return (self.create_empty_batch(),)

class ImageBatchCombiner(VideoBaseNode):
    """Combine two image batches in sequence."""

    @classmethod
    def INPUT_TYPES(cls) -> Dict[str, Any]:
        """Define input types for the node."""
        return {
            "required": {
                "first_images": ("IMAGE", {
                    "tooltip": "First images in sequence (required, placed before last). All images must have same dimensions."
                }),
                "last_images": ("IMAGE", {
                    "tooltip": "Last images in sequence (required, placed after first). All images must have same dimensions."
                }),
            }
        }

    RETURN_TYPES = ("IMAGE",)
    RETURN_NAMES = ("combined_batch",)
    FUNCTION = "combine_batches"
    CATEGORY = "J1mB091/Video"

    def combine_batches(self, first_images: Any, last_images: Any) -> Tuple["Tensor"]:
        """
        Combine two image batches in sequence.

        Args:
            first_images: First batch of images (tensor)
            last_images: Second batch of images (tensor)

        Returns:
            Tuple[Tensor]: Combined image batch

        Raises:
            ValueError: If tensors have mismatched dimensions or conversion fails
        """
        try:
            # Convert inputs to tensors
            first_images = self.ensure_tensor(first_images)
            last_images = self.ensure_tensor(last_images)
            
            # Move to CPU for consistent operations
            first_images = first_images.cpu()
            last_images = last_images.cpu()
            
            # Validate dimensions match
            if first_images.shape[1:] != last_images.shape[1:]:
                logger.error("Image dimension mismatch - batches must have same H, W, C dimensions")
                return (self.create_empty_batch(),)
            
            # Handle empty inputs
            if first_images.shape[0] == 0 and last_images.shape[0] == 0:
                return (self.create_empty_batch(),)
            
            # Create combined batch
            combined = torch.cat([first_images, last_images], dim=0)
            return (combined,)

        except Exception as e:
            logger.error(f"Error combining image batches: {e}")
            return (self.create_empty_batch(),)


class ImageBatchCombiner:
    """
    Combine two image batches for WAN video merging.
    Images from 'first_images' are placed before 'last_images' in the final sequence.
    The last image from 'first_images' is automatically excluded to prevent duplication.
    Can optionally ignore first_images to use only last_images.
    Note: All images in both batches must have the same dimensions for proper concatenation.
    Useful for combining prefix frames with main video sequences.
    """

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "first_images": ("IMAGE", {"tooltip": "First images in sequence (required, placed before last). All images must have same dimensions."}),
                "last_images": ("IMAGE", {"tooltip": "Last images in sequence (required). All images must have same dimensions."}),
                "ignore_first_images": ("BOOLEAN", {"default": False, "tooltip": "If true, ignores first_images and returns only last_images"}),
            }
        }

    RETURN_TYPES = ("IMAGE",)
    RETURN_NAMES = ("combined_images",)
    FUNCTION = "combine_batches"
    CATEGORY = "J1mB091/Video"

    def combine_batches(self, first_images: Any, last_images: Any, ignore_first_images: bool) -> Tuple[Any]:
        """
        Combine two image batches where first images come before last images.
        The last image from first_images is automatically excluded to prevent duplication.

        Args:
            first_images: First images in sequence (tensor, required, placed before last)
            last_images: Last images in sequence (tensor, required)
            ignore_first_images: If true, ignores first_images and returns only last_images

        Returns:
            Combined image batch as tensor
        """
        try:
            # Ensure both inputs are tensors
            if not isinstance(first_images, torch.Tensor):
                if hasattr(first_images, 'cpu'):
                    first_images = first_images.cpu()
                first_images = torch.tensor(first_images)

            if not isinstance(last_images, torch.Tensor):
                if hasattr(last_images, 'cpu'):
                    last_images = last_images.cpu()
                last_images = torch.tensor(last_images)

            # Move to CPU for operations
            first_images = first_images.cpu()
            last_images = last_images.cpu()

            # Handle combined_images based on ignore_first_images flag
            if ignore_first_images:
                # Use only last_images for combined output
                combined = last_images
            else:
                # Combine first_images (without last frame) + last_images
                if first_images.shape[0] > 1:
                    first_images_trimmed = first_images[:-1]  # Remove last image
                    combined = torch.cat([first_images_trimmed, last_images], dim=0)
                elif first_images.shape[0] == 1:
                    # Only one image in first_images, so combined is just last_images (since we would remove the only image)
                    combined = last_images
                else:
                    # No images in first_images, so combined is just last_images
                    combined = last_images

            return (combined,)

        except Exception as e:
            print(f"Error combining image batches: {e}")
            # Return safe defaults if combination fails
            return (last_images,)
