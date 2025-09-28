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
    """Combine two image batches for WAN/Video merging.

    Features:
    - Concatenate first_images (excluding its last frame) with last_images to avoid duplication
    - Optional flag to ignore first_images entirely
    - Validates dimension compatibility
    - Safe fallbacks on error
    """

    @classmethod
    def INPUT_TYPES(cls) -> Dict[str, Any]:
        return {
            "required": {
                "first_images": ("IMAGE", {"tooltip": "First images in sequence (placed before last_images). Must match dimensions."}),
                "last_images": ("IMAGE", {"tooltip": "Last images in sequence. Must match dimensions."}),
                "ignore_first_images": ("BOOLEAN", {"default": False, "tooltip": "If true, only use last_images"}),
            }
        }

    RETURN_TYPES = ("IMAGE",)
    RETURN_NAMES = ("combined_images",)
    FUNCTION = "combine_batches"
    CATEGORY = "J1mB091/Video"

    def combine_batches(self, first_images: Any, last_images: Any, ignore_first_images: bool) -> Tuple["Tensor"]:
        try:
            first_t = self.ensure_tensor(first_images)
            last_t = self.ensure_tensor(last_images)

            if first_t.shape[1:] != last_t.shape[1:]:  # type: ignore[union-attr]
                logger.error("Image dimension mismatch - batches must share H,W,C")
                return (self.create_empty_batch(),)

            if ignore_first_images:
                return (last_t,)

            # Exclude last frame of first batch to avoid duplication
            if first_t.shape[0] > 1:  # type: ignore[index]
                first_trimmed = first_t[:-1]
                combined = torch.cat([first_trimmed, last_t], dim=0)
            else:
                combined = last_t

            return (combined,)
        except Exception as e:
            logger.error(f"Error combining image batches: {e}")
            return (self.create_empty_batch(),)
