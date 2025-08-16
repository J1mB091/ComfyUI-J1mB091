from .named_aspect_ratio_matcher import NamedAspectRatioMatcher
from .aspect_ratio_from_image import AspectRatioFromImage
from .wan_resolution_selector import WanResolutionSelector
from .image_dimensions import ImageDimensions

# Import any future nodes here
# from .new_node import NewNode

# Expose frontend assets under the `js/` directory
WEB_DIRECTORY = "js"

NODE_CLASS_MAPPINGS = {
    "NamedAspectRatioMatcher": NamedAspectRatioMatcher,
    "AspectRatioFromImage": AspectRatioFromImage,
    "WanResolutionSelector": WanResolutionSelector,
    "ImageDimensions": ImageDimensions,
    # Add new nodes here
    # "NewNode": NewNode,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "NamedAspectRatioMatcher": "Match Named Aspect Ratio",
    "AspectRatioFromImage": "Aspect Ratio From Image",
    "WanResolutionSelector": "WAN Resolution Selector",
    "ImageDimensions": "Image Dimensions",
    # Add new node display names here
    # "NewNode": "My New Node 🎯",
}