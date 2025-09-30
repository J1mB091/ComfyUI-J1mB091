"""Resolution utility nodes for ComfyUI."""

import math
from typing import Any, Dict, List, Optional, Tuple, Union, TypeVar, cast, TYPE_CHECKING
import logging
from pathlib import Path

import numpy as np
from numpy.typing import NDArray
import numpy.typing as npt
import torch
from torch import Tensor
from PIL import Image

logger = logging.getLogger(__name__)

# Type variables for tensor operations
T = TypeVar('T', Tensor, NDArray[np.float32])
ImageType = Union[Tensor, NDArray[np.float32], Image.Image]

# Predefined known ratios with human-friendly labels
KNOWN_RATIOS: Dict[str, str] = {
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


class ImageProcessingBase:
    """Base class for image processing nodes with common utility methods."""
    
    @classmethod
    def extract_image_dimensions(cls, image: Any) -> Tuple[int, int]:
        """
        Extract width and height from various image formats.
        Returns (height, width) tuple.
        
        Args:
            image: Input image in any supported format
            
        Returns:
            Tuple[int, int]: Height and width as integers (512, 512) on error
        """
        try:
            if image is None:
                logger.warning("Received None image, using default dimensions")
                return 512, 512

            # Handle PIL Image
            if isinstance(image, Image.Image):
                width, height = image.size
                return int(height), int(width)

            # Get shape from ndarray or tensor
            shape = getattr(image, "shape", None)
            if shape is None:
                raise ValueError("Cannot get dimensions: no shape attribute")

            # Extract dimensions based on shape length
            if len(shape) == 4:  # [batch, height, width, channels]
                height, width = int(shape[1]), int(shape[2])
            elif len(shape) == 3:  # [height, width, channels]
                height, width = int(shape[0]), int(shape[1])
            elif len(shape) == 2:  # [height, width]
                height, width = int(shape[0]), int(shape[1])
            else:
                raise ValueError(f"Invalid shape for image: {shape}")

            # Validate dimensions
            if height <= 0 or width <= 0:
                raise ValueError(f"Invalid dimensions: {width}x{height}")

            return height, width

        except Exception as e:
            logger.error(f"Error getting dimensions: {e}")
            return 512, 512

    @classmethod
    def ensure_tensor(cls, image: Any) -> Optional[Tensor]:
        """
        Convert various image formats to tensor.
        
        Args:
            image: Input in any supported format
            
        Returns:
            Optional[Tensor]: Image tensor or None if conversion fails
        """
        try:
            if image is None:
                return None

            # Handle PIL Image
            if isinstance(image, Image.Image):
                img_array = np.array(image)
                return torch.from_numpy(img_array).float().div(255.0)

            # Handle tensor
            if isinstance(image, Tensor):
                return image.detach().cpu()

            # Handle numpy array
            if isinstance(image, np.ndarray):
                return torch.from_numpy(image.astype(np.float32))

            raise TypeError(f"Cannot convert type {type(image)} to tensor")

        except Exception as e:
            logger.error(f"Error converting to tensor: {e}")
            return None

    @classmethod 
    def tensor_to_pil_image(cls, image: Union[Tensor, NDArray]) -> Optional[Image.Image]:
        """
        Convert tensor/array to PIL Image.
        
        Args:
            image: Input tensor/array
            
        Returns:
            Optional[Image.Image]: PIL Image or None if conversion fails
        """
        try:
            if image is None:
                return None

            np_img: np.ndarray

            if torch.is_tensor(image):  # type: ignore[arg-type]
                t = cast(Tensor, image).detach().cpu()
                if t.dtype.is_floating_point:
                    t = t.clamp(0, 1).mul(255).to(torch.uint8)
                else:
                    t = t.to(torch.uint8)
                np_img = t.numpy()
            else:
                arr = cast(Union[np.ndarray, Any], image)
                if not isinstance(arr, np.ndarray):
                    raise TypeError("Input must be a torch.Tensor or numpy.ndarray")
                np_img = arr

            # Reduce batch dimension if present
            if np_img.ndim == 4:
                np_img = np_img[0]
            if np_img.ndim != 3:
                raise ValueError(f"Invalid shape: {getattr(np_img, 'shape', '?')}")

            if np_img.dtype != np.uint8:
                np_img = np.clip(np_img, 0, 255).astype(np.uint8)

            return Image.fromarray(np_img)

        except Exception as e:
            logger.error(f"Error converting to PIL: {e}")
            return None

    @staticmethod
    def pil_image_to_tensor(image: Optional[Image.Image]) -> Any:
        """
        Convert PIL Image to tensor format compatible with ComfyUI.
        
        Args:
            image: PIL Image to convert
            
        Returns:
            Any: Tensor in [batch, height, width, channels] format or None if conversion fails
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


class AspectRatioFromImage(ImageProcessingBase):
    """Extract aspect ratio from an image in 'width:height' format."""

    @classmethod
    def INPUT_TYPES(cls) -> dict[str, dict[str, Any]]:
        return {
            "required": {
                "image": ("IMAGE", {"tooltip": "Input image to extract aspect ratio from"}),
            }
        }

    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("aspect_ratio",)
    FUNCTION = "get_aspect_ratio"
    CATEGORY = "J1mB091/Resolution"

    def get_aspect_ratio(self, image: Any) -> tuple[str]:
        """
        Extract and normalize the aspect ratio from an image.
        
        Args:
            image: Input image in any supported format
            
        Returns:
            tuple[str]: Normalized aspect ratio in 'width:height' format
        """
        try:
            height, width = self.extract_image_dimensions(image)
            gcd = math.gcd(int(width), int(height)) or 1
            w = int(width) // gcd
            h = int(height) // gcd
            return (f"{w}:{h}",)
        except Exception as e:
            print(f"Error extracting aspect ratio: {e}")
            return ("1:1",)  # Safe default


class ImageDimensions(ImageProcessingBase):
    """Extract width and height dimensions from an image."""

    @classmethod
    def INPUT_TYPES(cls) -> dict[str, dict[str, Any]]:
        return {
            "required": {
                "image": ("IMAGE", {"tooltip": "Input image to extract dimensions from"}),
            }
        }

    RETURN_TYPES = ("INT", "INT")
    RETURN_NAMES = ("width", "height")
    FUNCTION = "dimensions"
    CATEGORY = "J1mB091/Resolution"

    def dimensions(self, image: Any) -> Tuple[int, int]:
        """
        Extract width and height from an image.
        
        Args:
            image: Input image in any supported format
            
        Returns:
            Tuple[int, int]: Width and height as integers
        """
        try:
            height, width = self.extract_image_dimensions(image)
            return int(width), int(height)
        except Exception as e:
            print(f"Error extracting dimensions: {e}")
            return (512, 512)  # Safe default


class NamedAspectRatioMatcher(ImageProcessingBase):
    """
    Find the closest named aspect ratio from a predefined list of common ratios.
    """
    @classmethod
    def INPUT_TYPES(cls) -> Dict[str, Dict[str, Any]]:
        return {
            "required": {
                "input_ratio": ("STRING", {"default": "16:9", "tooltip": "Input ratio in 'width:height' format"})
            }
        }

    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("closest_named_ratio",)
    FUNCTION = "match_ratio"
    CATEGORY = "J1mB091/Resolution"

    def match_ratio(self, input_ratio: str) -> Tuple[str]:
        """
        Find the closest named aspect ratio with its label.

        Args:
            input_ratio: String in 'width:height' format (e.g. "16:9")

        Returns:
            Tuple[str]: Closest ratio with label or "1:1" on error

        Example:
            >>> node.match_ratio("16:9")
            ("16:9 (Panorama)",)
        """
        try:
            # Validate input
            if not input_ratio or ":" not in input_ratio:
                logger.warning(f"Invalid ratio format: {input_ratio}")
                return ("1:1 (Perfect Square)",)

            # Parse ratio safely
            try:
                width, height = map(float, input_ratio.split(":"))
                if width <= 0 or height <= 0:
                    raise ValueError("Width and height must be positive")
            except (ValueError, TypeError) as e:
                logger.error(f"Error parsing ratio numbers: {e}")
                return ("1:1 (Perfect Square)",)

            # Calculate target ratio
            target_ratio = width / height
            closest_ratio = "1:1"
            closest_label = "Perfect Square"
            min_diff = float('inf')

            # Find closest named ratio
            for ratio_str, label in KNOWN_RATIOS.items():
                w, h = map(float, ratio_str.split(":"))
                current_ratio = w / h
                diff = abs(current_ratio - target_ratio)

                if diff < min_diff:
                    min_diff = diff
                    closest_ratio = ratio_str
                    closest_label = label

            # Format result with ratio and label
            return (f"{closest_ratio} ({closest_label})",)

        except Exception as e:
            logger.error(f"Error matching aspect ratio: {e}")
            return ("1:1 (Perfect Square)",)  # Safe default


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

    # FLUX Kontext specific resolution presets
    FLUX_KONTEXT_PRESETS = {
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

    # General FLUX presets (must stay in sync with js/resolution_selector.js)
    FLUX_PRESETS = {
        "576×2048  (9:32)": (576, 2048),
        "640×1472  (9:21)": (640, 1472),
        "704×1472  (9:19)": (704, 1472),
        "768×1344  (9:16)": (768, 1344),
        "896×1152  (7:9)": (896, 1152),
        "832×1280  (5:8)": (832, 1280),
        "832×1152  (5:7)": (832, 1152),
        "896×1152  (4:5)": (896, 1152),
        "768×1280  (3:5)": (768, 1280),
        "896×1152  (3:4)": (896, 1152),
        "832×1280  (2:3)": (832, 1280),
        "1024×1024  (1:1)": (1024, 1024),
        "1280×832  (3:2)": (1280, 832),
        "1152×896  (4:3)": (1152, 896),
        "1280×768  (5:3)": (1280, 768),
        "1152×896  (5:4)": (1152, 896),
        "1152×832  (7:5)": (1152, 832),
        "1280×832  (8:5)": (1280, 832),
        "1152×896  (9:7)": (1152, 896),
        "1344×768  (16:9)": (1344, 768),
        "1472×704  (19:9)": (1472, 704),
        "1472×640  (21:9)": (1472, 640),
        "2048×576  (32:9)": (2048, 576),
    }

    # SDXL optimized resolution presets
    SDXL_PRESETS = {
        "640×1536  (5:12)": (640, 1536),
        "768×1344  (4:7)": (768, 1344),
        "832×1216  (2:3)": (832, 1216),
        "896×1152  (7:9)": (896, 1152),
        "1024×1024  (1:1)": (1024, 1024),
        "1152×896  (9:7)": (1152, 896),
        "1216×832  (3:2)": (1216, 832),
        "1344×768  (7:4)": (1344, 768),
        "1536×640  (12:5)": (1536, 640),
    }

    # Make resolution sets available to JavaScript
    @classmethod
    def _get_model_resolutions(cls, model_type: str) -> list[str]:
        if model_type == "FLUX":
            return list(cls.FLUX_PRESETS.keys())
        elif model_type == "FLUX Kontext":
            return list(cls.FLUX_KONTEXT_PRESETS.keys())
        elif model_type == "SDXL":
            return list(cls.SDXL_PRESETS.keys())
        return []

    @classmethod
    def INPUT_TYPES(cls) -> dict[str, dict[str, Any]]:
        default_resolution = "1024×1024  (1:1)"
        
        # Initialize with FLUX resolutions as default
        initial_resolutions = list(cls.FLUX_PRESETS.keys())
        
        return {
            "required": {
                "mode": (["auto", "manual"], {"default": "auto", "tooltip": "Auto from image or override; or manual size"}),
                "model": (["WAN", "FLUX", "FLUX Kontext", "SDXL"], {"default": "WAN", "tooltip": "Model type: WAN uses quality presets, others use specific resolution presets"}),
                "quality": (["480p", "720p"], {"default": "480p", "tooltip": "Preset quality tier (WAN only)"}),
                "aspect_ratio_override": (["off", "1:1", "4:3", "16:9", "3:4", "9:16"], {"default": "off", "tooltip": "Force a specific aspect ratio in auto mode (WAN only)"}),
                "aspect_ratio": (initial_resolutions, {"default": default_resolution, "tooltip": "Resolution preset for the selected model"}),
                "manual_width": ("INT", {"default": 832, "min": cls.MIN_DIMENSION, "max": cls.MAX_DIMENSION, "step": cls.DIMENSION_ALIGNMENT, "tooltip": f"Manual width (multiples of {cls.DIMENSION_ALIGNMENT})"}),
                "manual_height": ("INT", {"default": 480, "min": cls.MIN_DIMENSION, "max": cls.MAX_DIMENSION, "step": cls.DIMENSION_ALIGNMENT, "tooltip": f"Manual height (multiples of {cls.DIMENSION_ALIGNMENT})"}),
            },
            "optional": {
                "image": ("IMAGE", {"tooltip": "Optional input image"}),
            }
        }

    @classmethod
    def VALIDATE_INPUTS(cls, mode: str, model: str, quality: str, aspect_ratio_override: str, aspect_ratio: str, manual_width: int, manual_height: int, **kwargs) -> bool | str:
        if mode == "manual" or model == "WAN":
            return True
            
        valid_resolutions = cls._get_model_resolutions(model)
        if not valid_resolutions:
            return True
            
        if aspect_ratio not in valid_resolutions:
            return f"Selected resolution '{aspect_ratio}' is not valid for {model} model"

        return True

        return {
            "manual_width": ("INT", {"default": 832, "min": cls.MIN_DIMENSION, "max": cls.MAX_DIMENSION, "step": cls.DIMENSION_ALIGNMENT, "tooltip": f"Manual width (multiples of {cls.DIMENSION_ALIGNMENT})"}),
            "manual_height": ("INT", {"default": 480, "min": cls.MIN_DIMENSION, "max": cls.MAX_DIMENSION, "step": cls.DIMENSION_ALIGNMENT, "tooltip": f"Manual height (multiples of {cls.DIMENSION_ALIGNMENT})"}),
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
            if model in ["FLUX", "FLUX Kontext", "SDXL"]:
                return self._handle_flux_mode(aspect_ratio, model)
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

    def _handle_flux_mode(self, aspect_ratio: str, model: str) -> Tuple[int, int]:
        """Handle FLUX/SDXL/FLUX Kontext model resolution selection"""
        if model == "SDXL":
            presets = self.SDXL_PRESETS
        elif model == "FLUX Kontext":
            presets = self.FLUX_KONTEXT_PRESETS
        else:  # FLUX
            presets = self.FLUX_PRESETS
            
        if aspect_ratio not in presets:
            raise ValueError(f"Invalid {model} aspect ratio: {aspect_ratio}")
        return presets[aspect_ratio]

    def _handle_wan_mode(self, image: Any, quality: str, aspect_ratio_override: str) -> Tuple[int, int]:
        """Handle WAN model resolution selection"""
        if image is not None:
            return self._handle_wan_with_image(image, quality, aspect_ratio_override)
        else:
            return self._handle_wan_without_image(quality, aspect_ratio_override)

    def _handle_wan_with_image(self, image: Any, quality: str, aspect_ratio_override: str) -> Tuple[int, int]:
        """
        Handle WAN mode when an image is provided.

        Args:
            image: Input image
            quality: Quality preset ("480p" or "720p")
            aspect_ratio_override: Override ratio ("off", "1:1", "4:3", etc.)

        Returns:
            Tuple[int, int]: Selected width and height
        """
        try:
            # Extract dimensions using base class helper
            processor = ImageProcessingBase()
            image_height, image_width = processor.extract_image_dimensions(image)

            # Choose target ratio and orientation
            ratio_key, forced_orientation = self._resolve_ratio_key(
                aspect_ratio_override,
                int(image_width),
                int(image_height)
            )

            # Map portrait ratios to landscape for preset lookup
            base_ratio_key = {"3:4": "4:3", "9:16": "16:9"}.get(ratio_key, ratio_key)
            base_width, base_height = self._select_base_resolution(quality, base_ratio_key)

            # Determine final orientation
            orientation = forced_orientation
            if not orientation and ratio_key != "1:1":
                orientation = "landscape" if image_width >= image_height else "portrait"

            # Swap dimensions for portrait if needed
            if orientation == "portrait" and ratio_key != "1:1":
                base_width, base_height = base_height, base_width

            return base_width, base_height

        except Exception as e:
            logger.error(f"Error handling WAN mode: {e}")
            # Return safe defaults based on quality
            defaults = {
                "480p": (512, 512),
                "720p": (768, 768)
            }
            return defaults.get(quality, (512, 512))

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
        """
        Determine the target aspect ratio and orientation.
        
        Args:
            override_key: Ratio override ("off", "1:1", "4:3", etc.)
            width: Image width or 1 if no image
            height: Image height or 1 if no image
            
        Returns:
            Tuple[str, Optional[str]]: (ratio_key, orientation)
            ratio_key: "1:1", "4:3", "16:9", etc.
            orientation: "portrait", "landscape", or None
        """
        # Handle explicit overrides
        if override_key in {"16:9", "4:3", "1:1"}:
            return override_key, (None if override_key == "1:1" else "landscape")
        if override_key in {"3:4", "9:16"}:
            return override_key, "portrait"

        # Compute normalized ratio from dimensions
        try:
            longer = max(width, height)
            shorter = min(width, height)
            if shorter == 0:
                return "1:1", None

            aspect = longer / shorter

            # Close to square
            if abs(aspect - 1.0) <= self.ASPECT_RATIO_TOLERANCE:
                return "1:1", None

            # Find closest standard ratio
            candidates = {
                "16:9": 16 / 9,
                "4:3": 4 / 3,
            }

            closest_key = "16:9"  # Default to widescreen
            smallest_diff = float("inf")

            for key, value in candidates.items():
                diff = abs(aspect - value)
                if diff < smallest_diff:
                    smallest_diff = diff
                    closest_key = key

            # Orientation will be inferred from image
            return closest_key, None

        except Exception as e:
            logger.error(f"Error resolving ratio: {e}")
            return "1:1", None  # Safe default

    def _select_base_resolution(self, quality: str, ratio_key: str) -> Tuple[int, int]:
        # Portrait orientation is applied later by swapping width/height when needed.
        try:
            return self.WAN_PRESETS[quality][ratio_key]
        except KeyError:
            raise ValueError(f"Unsupported combination: quality={quality}, ratio={ratio_key}")


