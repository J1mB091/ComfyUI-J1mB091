"""
J1mB091's ComfyUI Custom Nodes.

This module provides custom nodes for image resolution handling, video frame manipulation,
and workflow utilities in ComfyUI. The nodes are designed to streamline common operations
like aspect ratio calculations, resolution selection, seed management, and organized file saving.
"""

from typing import Dict, Type, Any
from .resolution_nodes import (
    AspectRatioFromImage,
    ImageDimensions, 
    NamedAspectRatioMatcher,
    ResolutionSelector
)
from .video_nodes import ExtractLastFrame, ImageBatchCombiner
from .utility_nodes import SeedGenerator, SaveImageWithSeed

# Expose frontend assets under the `js/` directory
WEB_DIRECTORY = "js"

NODE_CLASS_MAPPINGS: Dict[str, Type[Any]] = {
    "J1mB091AspectRatioFromImage": AspectRatioFromImage,
    "J1mB091ImageDimensions": ImageDimensions,
    "J1mB091NamedAspectRatioMatcher": NamedAspectRatioMatcher,
    "J1mB091ResolutionSelector": ResolutionSelector,
    "J1mB091ExtractLastFrame": ExtractLastFrame,
    "J1mB091ImageBatchCombiner": ImageBatchCombiner,
    "J1mB091SeedGenerator": SeedGenerator,
    "J1mB091SaveImageWithSeed": SaveImageWithSeed,
    # Add new nodes here using the format:
    # "NodeClassName": NodeClass,
}

# Display names for nodes in the ComfyUI interface
NODE_DISPLAY_NAME_MAPPINGS: Dict[str, str] = {
    "J1mB091AspectRatioFromImage": "J1mB091's Aspect Ratio From Image 📐",
    "J1mB091ImageDimensions": "J1mB091's Image Dimensions 📏",
    "J1mB091NamedAspectRatioMatcher": "J1mB091's Match Named Aspect Ratio 🎯",
    "J1mB091ResolutionSelector": "J1mB091's Resolution Selector 🖥️",
    "J1mB091ExtractLastFrame": "J1mB091's Extract Last Frame 📸",
    "J1mB091ImageBatchCombiner": "J1mB091's Image Batch Combiner 🔗",
    "J1mB091SeedGenerator": "J1mB091's Seed Generator 🌱",
    "J1mB091SaveImageWithSeed": "J1mB091's Save Image 💾",
    # Add new node display names here using the format:
    # "NodeClassName": "J1mB091's Node Display Name 🎯",
}