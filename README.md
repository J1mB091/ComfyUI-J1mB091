# ComfyUI-J1mB091 Custom Nodes 🎨

A collection of useful custom nodes for ComfyUI, focusing on resolution utilities and image batch manipulation.

## 📦 Installation

1. Clone or download this repository
2. Place it in your `ComfyUI/custom_nodes/` directory
3. Restart ComfyUI

## 🎯 Nodes Overview

### Resolution Utilities 📐📏🎯🖥️

All resolution nodes are located in the **J1mB091/Resolution** category.

#### **J1mB091's Aspect Ratio From Image 📐**
Extracts the aspect ratio from an input image and returns it in `width:height` format.

- **Input**: `IMAGE` - Any image tensor
- **Output**: `STRING` - Aspect ratio (e.g., "16:9", "4:3")

#### **J1mB091's Image Dimensions 📏**
Extracts the exact width and height dimensions from an input image.

- **Input**: `IMAGE` - Any image tensor
- **Output**: `INT, INT` - Width and height values

#### **J1mB091's Match Named Aspect Ratio 🎯**
Finds the closest named aspect ratio from a predefined list of common ratios.

- **Input**: `STRING` - Aspect ratio in "width:height" format
- **Output**: `STRING` - Closest named ratio with description

**Supported ratios include:**
- Square: `1:1` (Perfect Square)
- Portrait: `2:3`, `3:4`, `4:5`, `5:7`, `9:16`, etc.
- Landscape: `3:2`, `4:3`, `16:9`, `21:9`, etc.

#### **J1mB091's Resolution Selector 🖥️**
Universal resolution selector supporting both WAN and FLUX models with smart aspect ratio detection and conditional widget visibility.

**Models:**
- **WAN**: Uses quality presets with aspect ratio override (legacy support)
- **FLUX**: Uses specific resolution presets for optimal FLUX performance

**Modes:**
- **Auto**: Automatically selects resolution based on model type, input image, or aspect ratio settings
- **Manual**: Direct width/height input (must be divisible by 16)

**WAN Features:**
- Quality presets: 480p, 720p
- Aspect ratio overrides: 1:1, 4:3, 16:9, 3:4, 9:16
- Automatic portrait/landscape detection
- WAN-optimized resolutions (16-pixel aligned)

**FLUX Features:**
- Specific resolution presets optimized for FLUX
- 17 predefined aspect ratios from 9:21 to 21:9
- Direct resolution selection for optimal performance

### Video Sequence Manipulation 🎬

All video and sequence manipulation nodes are located in the **J1mB091/Video** category.

#### **J1mB091's Extract Last Frame 📸**
Extracts the last frame from an image batch, useful for preserving transition frames.

**Input:**
- **`images`** (required) - Input image batch to extract last frame from

**Output:**
- **`last_frame`** - The final image from the input batch

**Use Case:**
- Extract transition frames before combining video sequences
- Preserve the last frame of a prefix video for later use

#### **J1mB091's Image Batch Combiner 🔗**
Combines two image batches for WAN video merging with automatic duplicate prevention.

**Features:**
- Combines first_images before last_images in the final sequence
- Automatically excludes the last image from first_images to prevent duplication
- Optional toggle to ignore first_images completely
- Perfect for combining prefix frames with main video sequences

**Inputs:**
- **`first_images`** (required) - Prefix images placed before last_images
- **`last_images`** (required) - Main images in sequence
- **`ignore_first_images`** (required) - Boolean toggle to ignore first_images

**Output:**
- **`combined_images`** - Combined image batch

**Behavior:**
- When `ignore_first_images = False`: Combines (first_images[:-1] + last_images)
- When `ignore_first_images = True`: Returns only last_images
- Useful for dynamic video workflows where you need to include/exclude intro frames



## 🎛️ Frontend Features

### Conditional Widget Visibility
The included JavaScript extension provides dynamic widget visibility based on user selections:

- **J1mB091's Resolution Selector**: Shows/hides relevant widgets based on mode and model selection
- **Smart Logic**: Automatically shows WAN-specific options (quality, aspect_ratio_override) or FLUX-specific options (aspect_ratio presets)
- **Extensible**: Easy to add support for other nodes with conditional logic

## 🚀 Usage Examples

### Basic Resolution Workflow
```
Image → J1mB091's Aspect Ratio From Image → J1mB091's Match Named Aspect Ratio
```

### Universal Resolution Selection (WAN & FLUX)
```
Image → J1mB091's Resolution Selector (auto mode) → KSampler
```



### Extract Transition Frame
```
Prefix Video Frames → J1mB091's Extract Last Frame → Transition Frame
```

### Video Sequence Merging
```
Prefix Frames → J1mB091's Image Batch Combiner (last_images) → Main Video Frames → Combined Sequence
```

## 🔧 Technical Details

### Dependencies
This node pack uses only standard ComfyUI dependencies:
- `torch` - Tensor operations
- `numpy` - Array operations  
- `Pillow` - Image processing
- Built-in Python modules (`math`, `typing`)

### File Structure
```
ComfyUI-J1mB091/
├── __init__.py                           # Node registration
├── resolution_nodes.py                   # Resolution utilities
├── video_nodes.py                       # Video sequence manipulation
└── js/
    └── conditional_widget_visibility.js  # Frontend enhancements
```

## 🤝 Contributing

Feel free to submit issues, feature requests, or pull requests to improve this node pack!

## 📄 License

This project is licensed under the GNU General Public License v3.0 (GPL-3.0) - see the [LICENSE](LICENSE) file for details.

The GPL-3.0 license ensures that:
- ✅ You can freely use, modify, and distribute this software
- ✅ Any modifications you make must also be licensed under GPL-3.0
- ✅ You must include the original copyright and license notices
- ✅ You must provide access to the source code when distributing

---

**Created by J1mB091** - Making ComfyUI workflows more efficient! 🎨✨
