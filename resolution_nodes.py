import math
from typing import Any, Tuple, Optional
import torch
import numpy as np
from PIL import Image


# Predefined known ratios with human-friendly labels
KNOWN_RATIOS = {
    "1:1": "Perfect Square",
    "2:3": "Classic Portrait",
    "3:4": "Golden Ratio",
    "3:5": "Elegant Vertical",
    "4:5": "Artistic Frame",
    "5:7": "Balanced Portrait",
    "5:8": "Tall Portrait",
    "7:9": "Modern Portrait",
    "9:16": "Slim Vertical",
    "9:19": "Tall Slim",
    "9:21": "Ultra Tall",
    "9:32": "Skyline",
    "3:2": "Golden Landscape",
    "4:3": "Classic Landscape",
    "5:3": "Wide Horizon",
    "5:4": "Balanced Frame",
    "7:5": "Elegant Landscape",
    "8:5": "Cinematic View",
    "16:9": "Panorama",
    "19:9": "Cinematic Ultrawide",
    "21:9": "Epic Ultrawide",
    "32:9": "Extreme Ultrawide"
}


def extract_image_dimensions(image: Any) -> Tuple[int, int]:
    """
    Shared utility function to extract width and height from various image formats.
    Returns (height, width) tuple.
    """
    shape = getattr(image, "shape", None)
    if shape is None:
        raise ValueError("Unsupported image type: missing shape attribute")

    if len(shape) == 4:  # [batch, height, width, channels]
        height, width = shape[1], shape[2]
    elif len(shape) == 3:  # [height, width, channels] or [batch, height, width]
        height, width = shape[0], shape[1]
    elif len(shape) == 2:  # [height, width]
        height, width = shape[0], shape[1]
    else:
        raise ValueError(f"Unexpected image shape {shape}")

    if height <= 0 or width <= 0:
        raise ValueError(f"Invalid image dimensions: {width}x{height}")

    return int(height), int(width)


def tensor_to_pil_image(image: Any) -> Image.Image:
    """
    Convert various image formats (tensor, numpy array) to PIL Image.
    Returns None if conversion fails.
    """
    try:
        if image is None:
            return None

        # Handle tensor input
        if hasattr(image, 'cpu'):
            if isinstance(image, torch.Tensor):
                image = image.cpu().numpy()

        # Handle different shapes
        if len(image.shape) == 4:  # [batch, height, width, channels]
            image = image[0]  # Take first image
        elif len(image.shape) == 3:  # [height, width, channels]
            pass  # Already in correct format
        else:
            return None

        # Convert to uint8 and create PIL Image
        if image.dtype != np.uint8:
            image = (image * 255).astype(np.uint8)

        return Image.fromarray(image)

    except Exception as e:
        print(f"Error converting tensor to PIL Image: {e}")
        return None


def pil_image_to_tensor(image: Image.Image) -> Any:
    """
    Convert PIL Image to tensor format compatible with ComfyUI.
    Returns tensor in [batch, height, width, channels] format.
    """
    try:
        if image is None:
            return None

        # Convert PIL Image to numpy array
        img_array = np.array(image)

        # Convert to tensor format [batch, height, width, channels]
        if len(img_array.shape) == 3:  # [height, width, channels]
            img_tensor = torch.from_numpy(img_array).float() / 255.0
            img_tensor = img_tensor.unsqueeze(0)  # Add batch dimension
            return img_tensor

        return None

    except Exception as e:
        print(f"Error converting PIL Image to tensor: {e}")
        return None


class AspectRatioFromImage:
    """
    Extract aspect ratio from an image in 'width:height' format.
    """
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "image": ("IMAGE", {"tooltip": "Input image"}),
            }
        }

    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("aspect_ratio",)
    FUNCTION = "get_aspect_ratio"
    CATEGORY = "J1mB091/Resolution"

    def get_aspect_ratio(self, image: Any) -> tuple[str]:
        height, width = extract_image_dimensions(image)
        gcd = math.gcd(int(width), int(height)) or 1
        w = int(width) // gcd
        h = int(height) // gcd
        return (f"{w}:{h}",)


class ImageDimensions:
    """
    Extract width and height dimensions from an image.
    """
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "image": ("IMAGE", {"tooltip": "Input image"}),
            }
        }

    RETURN_TYPES = ("INT", "INT")
    RETURN_NAMES = ("width", "height")
    FUNCTION = "dimensions"
    CATEGORY = "J1mB091/Resolution"

    def dimensions(self, image: Any) -> Tuple[int, int]:
        height, width = extract_image_dimensions(image)
        return int(width), int(height)


class NamedAspectRatioMatcher:
    """
    Find the closest named aspect ratio from a predefined list of common ratios.
    """
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "input_ratio": ("STRING", {"default": "2.39:1"}),
            }
        }

    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("closest_named_ratio",)
    FUNCTION = "match_ratio"
    CATEGORY = "J1mB091/Resolution"

    def match_ratio(self, input_ratio: str) -> tuple[str]:
        if ':' not in input_ratio:
            raise ValueError("Invalid input. Format should be 'width:height'")

        width, height = map(float, input_ratio.split(':'))
        if height == 0:
            raise ValueError("Height cannot be zero")

        target = width / height

        closest = None
        smallest_diff = float('inf')

        for ratio_str, label in KNOWN_RATIOS.items():
            w, h = map(float, ratio_str.split(':'))
            current_ratio = w / h
            diff = abs(current_ratio - target)

            if diff < smallest_diff:
                smallest_diff = diff
                closest = f"{ratio_str} ({label})"

        return (closest,)


class ResolutionSelector:
    """
    Universal resolution selector for WAN and FLUX models. Selects output resolutions
    based on either the input image or manual width/height. Supports portrait and
    landscape orientations.

    Modes:
    - auto: If an image is provided, choose based on the image's aspect ratio (or override).
            If no image is provided, require a non-off aspect_ratio_override and use quality + override.
    - manual: Return the provided width/height (must be divisible by 16)

    Models:
    - WAN: Uses quality presets with aspect ratio override
    - FLUX: Uses specific resolution presets from the aspect_ratio selection
    """

    # Configuration constants
    DIMENSION_ALIGNMENT = 16
    MIN_DIMENSION = 16
    MAX_DIMENSION = 8192
    ASPECT_RATIO_TOLERANCE = 0.05  # 5% tolerance for near-square detection

    # WAN base presets by quality and target aspect ratio (landscape keys)
    WAN_PRESETS = {
        "480p": {
            "1:1": (512, 512),
            "4:3": (640, 480),
            "16:9": (832, 480),
        },
        "720p": {
            "1:1": (768, 768),
            "4:3": (960, 720),
            "16:9": (1280, 720),
        },
    }

    # FLUX specific resolution presets
    FLUX_PRESETS = {
        "672×1568  (9:21)": (672, 1568),
        "688×1504  (9:19.5)": (688, 1504),
        "720×1456  (9:18)": (720, 1456),
        "752×1392  (9:17)": (752, 1392),
        "800×1328  (5:8)": (800, 1328),
        "832×1248  (2:3)": (832, 1248),
        "880×1184  (3:4)": (880, 1184),
        "944×1104  (4:5)": (944, 1104),
        "1024×1024  (1:1)": (1024, 1024),
        "1104×944  (5:4)": (1104, 944),
        "1184×880  (4:3)": (1184, 880),
        "1248×832  (3:2)": (1248, 832),
        "1328×800  (8:5)": (1328, 800),
        "1392×752  (17:9)": (1392, 752),
        "1456×720  (18:9)": (1456, 720),
        "1504×688  (19.5:9)": (1504, 688),
        "1568×672  (21:9)": (1568, 672),
    }

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "mode": (["auto", "manual"], {"default": "auto", "tooltip": "Auto from image or override; or manual size"}),
                "model": (["WAN", "FLUX"], {"default": "WAN", "tooltip": "Model type: WAN uses quality presets, FLUX uses specific resolution presets"}),
                "quality": (["480p", "720p"], {"default": "480p", "tooltip": "Preset quality tier (WAN only)"}),
                "aspect_ratio_override": (["off", "1:1", "4:3", "16:9", "3:4", "9:16"], {"default": "off", "tooltip": "Force a specific aspect ratio in auto mode (WAN only)"}),
                "aspect_ratio": (list(cls.FLUX_PRESETS.keys()), {"default": "1024×1024  (1:1)", "tooltip": "Specific resolution preset (FLUX only)"}),
                "manual_width": ("INT", {"default": 832, "min": cls.MIN_DIMENSION, "max": cls.MAX_DIMENSION, "step": cls.DIMENSION_ALIGNMENT, "tooltip": f"Manual width (multiples of {cls.DIMENSION_ALIGNMENT})"}),
                "manual_height": ("INT", {"default": 480, "min": cls.MIN_DIMENSION, "max": cls.MAX_DIMENSION, "step": cls.DIMENSION_ALIGNMENT, "tooltip": f"Manual height (multiples of {cls.DIMENSION_ALIGNMENT})"}),
            },
            "optional": {
                "image": ("IMAGE", {"tooltip": "Optional input image"}),
            },
        }

    RETURN_TYPES = ("INT", "INT")
    RETURN_NAMES = ("width", "height")
    FUNCTION = "select_resolution"
    CATEGORY = "J1mB091/Resolution"

    def select_resolution(
        self,
        mode: str,
        model: str,
        quality: str,
        aspect_ratio_override: str,
        aspect_ratio: str,
        manual_width: int,
        manual_height: int,
        image: Any = None,
    ) -> Tuple[int, int]:
        # Manual mode: return provided dimensions; all other parameters are ignored here
        if mode == "manual":
            return self._handle_manual_mode(manual_width, manual_height)

        # Auto mode
        if mode == "auto":
            if model == "FLUX":
                return self._handle_flux_mode(aspect_ratio)
            else:
                return self._handle_wan_mode(image, quality, aspect_ratio_override)

        # Unknown mode
        raise ValueError(f"Unsupported mode: {mode}")

    def _handle_manual_mode(self, manual_width: int, manual_height: int) -> Tuple[int, int]:
        """Handle manual resolution mode with validation"""
        if manual_width % self.DIMENSION_ALIGNMENT != 0 or manual_height % self.DIMENSION_ALIGNMENT != 0:
            raise ValueError(f"manual_width and manual_height must be divisible by {self.DIMENSION_ALIGNMENT}")
        if not (self.MIN_DIMENSION <= manual_width <= self.MAX_DIMENSION) or not (
            self.MIN_DIMENSION <= manual_height <= self.MAX_DIMENSION
        ):
            raise ValueError(
                f"manual_width and manual_height must be within [{self.MIN_DIMENSION}, {self.MAX_DIMENSION}]"
            )
        return (manual_width, manual_height)

    def _handle_flux_mode(self, aspect_ratio: str) -> Tuple[int, int]:
        """Handle FLUX model resolution selection"""
        if aspect_ratio not in self.FLUX_PRESETS:
            raise ValueError(f"Invalid FLUX aspect ratio: {aspect_ratio}")
        return self.FLUX_PRESETS[aspect_ratio]

    def _handle_wan_mode(self, image: Any, quality: str, aspect_ratio_override: str) -> Tuple[int, int]:
        """Handle WAN model resolution selection"""
        if image is not None:
            return self._handle_wan_with_image(image, quality, aspect_ratio_override)
        else:
            return self._handle_wan_without_image(quality, aspect_ratio_override)

    def _handle_wan_with_image(self, image: Any, quality: str, aspect_ratio_override: str) -> Tuple[int, int]:
        """Handle WAN mode when an image is provided"""
        image_height, image_width = extract_image_dimensions(image)
        # Choose target aspect ratio and possible forced orientation based on override
        ratio_key, forced_orientation = self._resolve_ratio_key(aspect_ratio_override, image_width, image_height)

        # Our presets are defined for landscape keys; map portrait keys to their landscape equivalents
        base_ratio_key = {"3:4": "4:3", "9:16": "16:9"}.get(ratio_key, ratio_key)
        base_width, base_height = self._select_base_resolution(quality, base_ratio_key)

        # Decide final orientation: obey forced orientation if provided; otherwise infer from image
        orientation = forced_orientation or ("landscape" if image_width >= image_height else "portrait")

        # For portrait (non-square), swap dimensions to keep the requested ratio orientation
        if orientation == "portrait" and ratio_key != "1:1":
            base_width, base_height = base_height, base_width

        return (base_width, base_height)

    def _handle_wan_without_image(self, quality: str, aspect_ratio_override: str) -> Tuple[int, int]:
        """Handle WAN mode when no image is provided"""
        if aspect_ratio_override == "off":
            raise ValueError("In auto mode without an image, aspect_ratio_override must be set (not 'off')")

        # Determine ratio and orientation purely from the override
        ratio_key, forced_orientation = self._resolve_ratio_key(aspect_ratio_override, 1, 1)
        base_ratio_key = {"3:4": "4:3", "9:16": "16:9"}.get(ratio_key, ratio_key)
        base_width, base_height = self._select_base_resolution(quality, base_ratio_key)

        # Apply portrait orientation when override is a portrait ratio
        if forced_orientation == "portrait" and ratio_key != "1:1":
            base_width, base_height = base_height, base_width

        return (base_width, base_height)

    def _resolve_ratio_key(self, override_key: str, width: int, height: int) -> Tuple[str, Optional[str]]:
        # Respect explicit override when provided
        if override_key in {"16:9", "4:3", "1:1"}:
            return override_key, (None if override_key == "1:1" else "landscape")
        if override_key in {"3:4", "9:16"}:
            return override_key, "portrait"

        # Otherwise, compute a normalized aspect ratio (>= 1) so portrait/landscape
        # both compare fairly against canonical landscape ratios.
        longer = max(width, height)
        shorter = min(width, height)
        if shorter == 0:
            return "1:1", None
        aspect = longer / shorter

        # Prefer 1:1 only when sufficiently close to square
        if abs(aspect - 1.0) <= self.ASPECT_RATIO_TOLERANCE:
            return "1:1", None

        candidates = {
            "16:9": 16 / 9,
            "4:3": 4 / 3,
        }

        closest_key = None
        smallest_diff = float("inf")
        for key, value in candidates.items():
            diff = abs(aspect - value)
            if diff < smallest_diff:
                smallest_diff = diff
                closest_key = key
        # Orientation not forced when override is off; it will be inferred from the image
        return closest_key, None

    def _select_base_resolution(self, quality: str, ratio_key: str) -> Tuple[int, int]:
        # Portrait orientation is applied later by swapping width/height when needed.
        try:
            return self.WAN_PRESETS[quality][ratio_key]
        except KeyError:
            raise ValueError(f"Unsupported combination: quality={quality}, ratio={ratio_key}")


