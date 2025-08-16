# ComfyUI-J1mB091 Custom Nodes 🎨

A collection of useful custom nodes for ComfyUI, focusing on resolution utilities and advanced XY plotting capabilities.

## 📦 Installation

1. Clone or download this repository
2. Place it in your `ComfyUI/custom_nodes/` directory
3. Restart ComfyUI

## 🎯 Nodes Overview

### Resolution Utilities 📐📏🎯🖥️

All resolution nodes are located in the **J1mB091/Resolution** category.

#### **Aspect Ratio From Image 📐**
Extracts the aspect ratio from an input image and returns it in `width:height` format.

- **Input**: `IMAGE` - Any image tensor
- **Output**: `STRING` - Aspect ratio (e.g., "16:9", "4:3")

#### **Image Dimensions 📏**
Extracts the exact width and height dimensions from an input image.

- **Input**: `IMAGE` - Any image tensor  
- **Output**: `INT, INT` - Width and height values

#### **Match Named Aspect Ratio 🎯**
Finds the closest named aspect ratio from a predefined list of common ratios.

- **Input**: `STRING` - Aspect ratio in "width:height" format
- **Output**: `STRING` - Closest named ratio with description

**Supported ratios include:**
- Square: `1:1` (Perfect Square)
- Portrait: `2:3`, `3:4`, `4:5`, `5:7`, `9:16`, etc.
- Landscape: `3:2`, `4:3`, `16:9`, `21:9`, etc.

#### **WAN Resolution Selector 🖥️**
Intelligent resolution selector optimized for WAN models with smart aspect ratio detection.

**Modes:**
- **Auto**: Automatically selects resolution based on input image or aspect ratio override
- **Manual**: Direct width/height input (must be divisible by 32)

**Features:**
- Quality presets: 480p, 720p
- Aspect ratio overrides: 1:1, 4:3, 16:9, 3:4, 9:16
- Automatic portrait/landscape detection
- WAN-optimized resolutions (32-pixel aligned)

### XY Plotting 📊

#### **KSampler XY Plot 📊**
Advanced KSampler with built-in XY plotting capabilities for parameter testing and comparison.

**Features:**
- Create comparison grids across multiple parameters
- Customizable font size, color, and border
- Supports all standard KSampler parameters
- Generates annotated plot images showing parameter values

**Inputs:**
- Standard KSampler inputs (model, seed, steps, cfg, etc.)
- `adv_xyPlot` - Advanced XY plot configuration
- Plot styling options (font size, color, border)

**Output:**
- `IMAGE` - Annotated comparison grid

## 🎛️ Frontend Features

### Conditional Widget Visibility
The included JavaScript extension provides dynamic widget visibility based on user selections:

- **WAN Resolution Selector**: Shows/hides relevant widgets based on mode selection
- **Extensible**: Easy to add support for other nodes with conditional logic

## 🚀 Usage Examples

### Basic Resolution Workflow
```
Image → Aspect Ratio From Image → Match Named Aspect Ratio
```

### WAN Model Optimization
```
Image → WAN Resolution Selector (auto mode) → KSampler
```

### Parameter Testing
```
KSampler XY Plot → Advanced XY Plot Config → Generate Comparison Grid
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
├── xy_plot_nodes.py                     # XY plotting functionality
└── js/
    └── conditional_widget_visibility.js  # Frontend enhancements
```

## 🤝 Contributing

Feel free to submit issues, feature requests, or pull requests to improve this node pack!

---

**Created by J1mB091** - Making ComfyUI workflows more efficient! 🎨✨
