from .resolution_nodes import AspectRatioFromImage, ImageDimensions, NamedAspectRatioMatcher, WanResolutionSelector
from .xy_plot_nodes import KSamplerXYPlot

# Import any future nodes here
# from .new_node import NewNode

# Expose frontend assets under the `js/` directory
WEB_DIRECTORY = "js"

NODE_CLASS_MAPPINGS = {
    "AspectRatioFromImage": AspectRatioFromImage,
    "ImageDimensions": ImageDimensions,
    "NamedAspectRatioMatcher": NamedAspectRatioMatcher,
    "WanResolutionSelector": WanResolutionSelector,
    "KSamplerXYPlot": KSamplerXYPlot,
    # Add new nodes here
    # "NewNode": NewNode,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "AspectRatioFromImage": "Aspect Ratio From Image 📐",
    "ImageDimensions": "Image Dimensions 📏",
    "NamedAspectRatioMatcher": "Match Named Aspect Ratio 🎯",
    "WanResolutionSelector": "WAN Resolution Selector 🖥️",
    "KSamplerXYPlot": "KSampler XY Plot 📊",
    # Add new node display names here
    # "NewNode": "My New Node 🎯",
}