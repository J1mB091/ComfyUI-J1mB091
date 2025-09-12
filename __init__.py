"""
J1mB091's ComfyUI Custom Nodes.

This module provides custom nodes for image resolution handling and video frame manipulation
in ComfyUI. The nodes are designed to streamline common operations like aspect ratio
calculations, resolution selection, and frame extraction.
"""

from typing import Dict, Type, Any
from .resolution_nodes import (
    AspectRatioFromImage,
    ImageDimensions, 
    NamedAspectRatioMatcher,
    ResolutionSelector
)
from .video_nodes import ExtractLastFrame, ImageBatchCombiner

# Expose frontend assets under the `js/` directory
WEB_DIRECTORY = "js"

NODE_CLASS_MAPPINGS: Dict[str, Type[Any]] = {
    "AspectRatioFromImage": AspectRatioFromImage,
    "ImageDimensions": ImageDimensions,
    "NamedAspectRatioMatcher": NamedAspectRatioMatcher,
    "ResolutionSelector": ResolutionSelector,
    "ExtractLastFrame": ExtractLastFrame,
    "ImageBatchCombiner": ImageBatchCombiner,
    # Add new nodes here using the format:
    # "NodeClassName": NodeClass,
}

# Display names for nodes in the ComfyUI interface
NODE_DISPLAY_NAME_MAPPINGS: Dict[str, str] = {
    "AspectRatioFromImage": "J1mB091's Aspect Ratio From Image 📐",
    "ImageDimensions": "J1mB091's Image Dimensions 📏",
    "NamedAspectRatioMatcher": "J1mB091's Match Named Aspect Ratio 🎯",
    "ResolutionSelector": "J1mB091's Resolution Selector 🖥️",
    "ExtractLastFrame": "J1mB091's Extract Last Frame 📸",
    "ImageBatchCombiner": "J1mB091's Image Batch Combiner 🔗",
    # Add new node display names here using the format:
    # "NodeClassName": "J1mB091's Node Display Name 🎯",
}