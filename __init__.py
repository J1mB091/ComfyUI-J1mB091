from .resolution_nodes import AspectRatioFromImage, ImageDimensions, NamedAspectRatioMatcher, ResolutionSelector
from .xy_plot_nodes import KSamplerXYPlot

# Import any future nodes here
# from .new_node import NewNode

# Expose frontend assets under the `js/` directory
WEB_DIRECTORY = "js"

NODE_CLASS_MAPPINGS = {
    "AspectRatioFromImage": AspectRatioFromImage,
    "ImageDimensions": ImageDimensions,
    "NamedAspectRatioMatcher": NamedAspectRatioMatcher,
    "ResolutionSelector": ResolutionSelector,
    "KSamplerXYPlot": KSamplerXYPlot,
    # Add new nodes here
    # "NewNode": NewNode,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "AspectRatioFromImage": "J1mB091's Aspect Ratio From Image 📐",
    "ImageDimensions": "J1mB091's Image Dimensions 📏",
    "NamedAspectRatioMatcher": "J1mB091's Match Named Aspect Ratio 🎯",
    "ResolutionSelector": "J1mB091's Resolution Selector 🖥️",
    "KSamplerXYPlot": "J1mB091's KSampler XY Plot 📊",
    # Add new node display names here
    # "NewNode": "J1mB091's My New Node 🎯",
}