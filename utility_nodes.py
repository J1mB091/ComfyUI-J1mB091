"""Utility nodes for ComfyUI."""

from typing import Any, Dict, Optional, Tuple
import os
import json
from PIL import Image
from PIL.PngImagePlugin import PngInfo
import numpy as np
import torch

# Import ComfyUI modules
import folder_paths
from comfy.cli_args import args


class SeedGenerator:
    """Generate a seed number for your sampling and image naming."""

    @classmethod
    def INPUT_TYPES(cls) -> Dict[str, Dict[str, Any]]:
        return {
            "required": {
                "seed": ("INT", {"default": 0, "min": 0, "max": 18446744073709551615, "tooltip": "Seed number for generation"}),
            }
        }

    RETURN_TYPES = ("INT",)
    RETURN_NAMES = ("seed",)
    FUNCTION = "generate_seed"
    CATEGORY = "J1mB091/Utility"

    def generate_seed(self, seed: int) -> Tuple[int]:
        """
        Pass through or generate a seed number.
        
        Args:
            seed: Seed number for generation
            
        Returns:
            Tuple[int]: The seed value for samplers and save nodes
        """
        return (seed,)


class SaveImageWithSeed:
    """Save images with seed naming - counter comes first, then seed."""

    def __init__(self):
        self.output_dir = folder_paths.get_output_directory()
        self.type = "output"
        self.compress_level = 4

    @classmethod
    def INPUT_TYPES(cls) -> Dict[str, Dict[str, Any]]:
        return {
            "required": {
                "images": ("IMAGE", {"tooltip": "Images to save"}),
                "filename_prefix": ("STRING", {"default": "ComfyUI", "tooltip": "Base filename prefix"}),
            },
            "optional": {
                "seed": ("INT", {"forceInput": True, "tooltip": "Seed number from another node"}),
            },
            "hidden": {
                "prompt": "PROMPT", "extra_pnginfo": "EXTRA_PNGINFO"
            }
        }

    RETURN_TYPES = ()
    OUTPUT_NODE = True
    FUNCTION = "save"
    CATEGORY = "J1mB091/Utility"

    def save(self, images, filename_prefix: str, seed: Optional[int] = None, prompt=None, extra_pnginfo=None):
        """
        Save images with optional seed in filename.

        Args:
            images: Image batch to save
            filename_prefix: Base filename
            seed: Optional seed number from input
            prompt: Workflow prompt for metadata
            extra_pnginfo: Extra PNG info for metadata

        Returns:
            Empty tuple for ComfyUI compatibility
        """
        return self._save_images_impl(images, filename_prefix, seed, prompt, extra_pnginfo)
    def _save_images_impl(self, images, filename_prefix: str, seed: Optional[int] = None, prompt=None, extra_pnginfo=None):
        """
        Save images with optional seed in filename using ComfyUI's proper save logic.

        Args:
            images: Image batch to save
            filename_prefix: Base filename
            seed: Optional seed number from input (if not provided, omitted from filename)
            prompt: Workflow prompt for metadata
            extra_pnginfo: Extra PNG info for metadata

        Returns:
            Dict with saved image info for ComfyUI preview
        """
        # Get the base path info from ComfyUI's function
        full_output_folder, filename, base_counter, subfolder, filename_prefix = folder_paths.get_save_image_path(filename_prefix, self.output_dir, images[0].shape[1], images[0].shape[0])

        # Now find the highest counter among all existing files (with and without seeds)
        try:
            existing_files = os.listdir(full_output_folder)
            # Look for files matching our prefix pattern
            counters = []
            for f in existing_files:
                if f.startswith(filename + "_") and f.endswith(".png"):
                    # Extract counter from patterns like: filename_XXXXX_.png or filename_XXXXX_seed_.png
                    parts = f.replace('.png', '').split('_')
                    if len(parts) >= 2:
                        # Try to get the counter (second part for no seed, second part for with seed)
                        try:
                            counter_part = parts[1]  # This should be the 5-digit number
                            if len(counter_part) == 5 and counter_part.isdigit():
                                counters.append(int(counter_part))
                        except (IndexError, ValueError):
                            continue

            if counters:
                counter = max(counters) + 1
            else:
                counter = base_counter
        except (FileNotFoundError, OSError):
            counter = base_counter

        results = []

        for (batch_number, image) in enumerate(images):
            # Convert tensor to PIL Image properly for ComfyUI
            i = 255. * image.cpu().numpy()
            img = Image.fromarray(np.clip(i, 0, 255).astype(np.uint8))

            # Add metadata if not disabled
            metadata = None
            if not args.disable_metadata:
                metadata = PngInfo()
                if prompt is not None:
                    metadata.add_text("prompt", json.dumps(prompt))
                if extra_pnginfo is not None:
                    for x in extra_pnginfo:
                        metadata.add_text(x, json.dumps(extra_pnginfo[x]))

            # Generate filename with proper ComfyUI format
            filename_with_batch_num = filename.replace("%batch_num%", str(batch_number))

            # Add seed to filename if provided
            if seed is not None:
                file = f"{filename_with_batch_num}_{counter:05}_{seed}_.png"
            else:
                file = f"{filename_with_batch_num}_{counter:05}_.png"

            img.save(os.path.join(full_output_folder, file), pnginfo=metadata, compress_level=self.compress_level)

            results.append({
                "filename": file,
                "subfolder": subfolder,
                "type": self.type
            })

            counter += 1

        return {"ui": {"images": results}}
