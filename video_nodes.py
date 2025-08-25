import torch
import numpy as np
from typing import Any, Tuple, Optional


class ExtractLastFrame:
    """
    Extract the last frame from an image batch.
    Returns the final image from the input batch, useful for preserving transition frames.
    """

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "images": ("IMAGE", {"tooltip": "Input image batch to extract last frame from"}),
            }
        }

    RETURN_TYPES = ("IMAGE",)
    RETURN_NAMES = ("last_frame",)
    FUNCTION = "extract_last_frame"
    CATEGORY = "J1mB091/Video"

    def extract_last_frame(self, images: Any) -> Tuple[Any]:
        """
        Extract the last frame from an image batch.

        Args:
            images: Input image batch (tensor)

        Returns:
            Last frame as single image tensor
        """
        try:
            # Ensure input is a tensor
            if not isinstance(images, torch.Tensor):
                if hasattr(images, 'cpu'):
                    images = images.cpu()
                images = torch.tensor(images)

            # Move to CPU for operations
            images = images.cpu()

            # Extract the last frame
            if images.shape[0] > 0:
                last_frame = images[-1:]  # Keep as batch with 1 image
                return (last_frame,)
            else:
                # Return empty tensor if no images
                return (torch.empty(0, *images.shape[1:], dtype=images.dtype),)

        except Exception as e:
            print(f"Error extracting last frame: {e}")
            # Return empty tensor on error
            return (torch.empty(0, 512, 512, 3, dtype=torch.float32),)


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
