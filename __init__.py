from .resolution_nodes import AspectRatioFromImage, ImageDimensions, NamedAspectRatioMatcher, ResolutionSelector
from .video_nodes import ExtractLastFrame, ImageBatchCombiner

# Import any future nodes here
# from .new_node import NewNode

# Expose frontend assets under the `js/` directory
WEB_DIRECTORY = "js"

NODE_CLASS_MAPPINGS = {
    "AspectRatioFromImage": AspectRatioFromImage,
    "ImageDimensions": ImageDimensions,
    "NamedAspectRatioMatcher": NamedAspectRatioMatcher,
    "ResolutionSelector": ResolutionSelector,
    "ExtractLastFrame": ExtractLastFrame,
    "ImageBatchCombiner": ImageBatchCombiner,
    # Add new nodes here
    # "NewNode": NewNode,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "AspectRatioFromImage": "J1mB091's Aspect Ratio From Image 📐",
    "ImageDimensions": "J1mB091's Image Dimensions 📏",
    "NamedAspectRatioMatcher": "J1mB091's Match Named Aspect Ratio 🎯",
    "ResolutionSelector": "J1mB091's Resolution Selector 🖥️",
    "ExtractLastFrame": "J1mB091's Extract Last Frame 📸",
    "ImageBatchCombiner": "J1mB091's Image Batch Combiner 🔗",
    # Add new node display names here
    # "NewNode": "J1mB091's My New Node 🎯",
}