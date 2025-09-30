# ComfyUI Custom Nodes 🎨

A collection of custom nodes for ComfyUI focused on image resolution management, video frame handling, and workflow utilities.

## ✨ Features

### 📐 Resolution Management
- **Image Dimensions**: Extract and manipulate image dimensions
- **Aspect Ratio**: Calculate and match aspect ratios automatically
- **Resolution Selector**: Smart resolution presets with SDXL/FLUX support

### 🎥 Video Frame Handling
- **Extract Last Frame**: Get the final frame from a batch sequence
- **Image Batch Combiner**: Join image batches while preserving dimensions

### 🌱 Workflow Utilities
- **Seed Generator**: Generate and pass seed values for reproducible results
- **Save Image with Seed**: Save images with automatic seed-based naming and proper counter logic

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

### Workflow Utilities 🌱💾

All utility nodes are located in the **J1mB091/Utility** category.

#### **J1mB091's Seed Generator 🌱**
Generates a seed number for reproducible sampling and image naming.

**Input:**
- **`seed`** (required) - Seed number for generation (0 to 18,446,744,073,709,551,615)

**Output:**
- **`seed`** - The seed value for samplers and save nodes

**Use Case:**
- Generate consistent seeds for reproducible results
- Pass seed values to samplers and save nodes for organized file naming

#### **J1mB091's Save Image 💾**
Saves images with optional seed-based naming and proper sequential counter logic.

**Features:**
- Automatic sequential counter that increments across all saves
- Optional seed integration in filename
- Proper ComfyUI preview support
- PNG metadata embedding (prompt and workflow info)
- Counter works regardless of seed changes or absence

**Inputs:**
- **`images`** (required) - Images to save
- **`filename_prefix`** (required) - Base filename prefix
- **`seed`** (optional) - Seed number from Seed Generator node

**Output:**
- Saves images to ComfyUI output directory with proper naming

**Filename Format:**
- With seed: `prefix_XXXXX_seed_.png` (e.g., `ComfyUI_00001_12345_.png`)
- Without seed: `prefix_XXXXX_.png` (e.g., `ComfyUI_00001_.png`)

**Counter Behavior:**
- Always increments sequentially (00001, 00002, 00003, etc.)
- Works across different seed values and save operations
- Prevents filename conflicts automatically



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

### Reproducible Seed Workflow
```
J1mB091's Seed Generator → KSampler (seed input) → J1mB091's Save Image (seed input)
```

### Organized Image Saving with Seeds
```
Latent Image → KSampler → J1mB091's Save Image
                              ↑
                              J1mB091's Seed Generator
```

**Result:** Images saved as `ComfyUI_00001_12345_.png`, `ComfyUI_00002_12345_.png`, etc.

## 🔧 Technical Details

## 🔧 Technical Details

### Dependencies
- Python 3.8+
- PyTorch 2.0.0+
- typing-extensions 4.5.0+
- ComfyUI latest version

### File Structure
```
ComfyUI-J1mB091/
├── __init__.py                         # Node registration
├── resolution_nodes.py                 # Resolution utilities
├── video_nodes.py                     # Video processing
├── utility_nodes.py                   # Workflow utilities (seed & save)
├── js/
│   └── conditional_widget_visibility.js # UI enhancements
├── .vscode/
│   └── settings.json                  # VS Code configuration
├── requirements.txt                   # Dependencies
├── README.md                          # This file
└── LICENSE                           # GPL-3.0 License
```

### Node Categories
1. **Resolution Nodes** (`J1mB091/Resolution`):
   - `AspectRatioFromImage` - Calculate aspect ratio
   - `ImageDimensions` - Get image dimensions
   - `NamedAspectRatioMatcher` - Match standard ratios
   - `ResolutionSelector` - Smart resolution presets

2. **Video Nodes** (`J1mB091/Video`):
   - `ExtractLastFrame` - Get final frame from batch
   - `ImageBatchCombiner` - Join image sequences

3. **Utility Nodes** (`J1mB091/Utility`):
   - `SeedGenerator` - Generate seed values
   - `SaveImageWithSeed` - Save with seed naming

## 🤝 Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/improvement`)
3. Commit changes (`git commit -am 'Add feature'`)
4. Push to branch (`git push origin feature/improvement`)
5. Open a Pull Request

## 📄 License

GPL-3.0 - see LICENSE file for details

The GPL-3.0 license ensures that:
- ✅ You can freely use, modify, and distribute this software
- ✅ Any modifications you make must also be licensed under GPL-3.0
- ✅ You must include the original copyright and license notices
- ✅ You must provide access to the source code when distributing

---

**Created by J1mB091** - Making ComfyUI workflows more efficient! 🎨✨
