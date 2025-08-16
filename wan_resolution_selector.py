from typing import Any, Optional, Tuple


class WanResolutionSelector:
    """
    Selects WAN-supported output resolutions based on either the input image
    or manual width/height. Supports portrait and landscape by swapping
    dimensions when needed.

    Modes:
    - auto: If an image is provided, choose based on the image's aspect ratio (or override).
            If no image is provided, require a non-off aspect_ratio_override and use quality + override.
    - manual: Return the provided width/height (must be divisible by 32)
    """

    # Configuration constants
    DIMENSION_ALIGNMENT = 32
    MIN_DIMENSION = 32
    MAX_DIMENSION = 8192
    ASPECT_RATIO_TOLERANCE = 0.05  # 5% tolerance for near-square detection

    # WAN base presets by quality and target aspect ratio (landscape keys)
    PRESETS = {
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

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "mode": (["auto", "manual"], {"default": "auto", "tooltip": "Auto from image or override; or manual size"}),
                "quality": (["480p", "720p"], {"default": "720p", "tooltip": "Preset quality tier"}),
                "aspect_ratio_override": (["off", "1:1", "4:3", "16:9", "3:4", "9:16"], {"default": "off", "tooltip": "Force a specific aspect ratio in auto mode"}),
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
    CATEGORY = "J1mB091"

    def select_resolution(
        self,
        mode: str,
        quality: str,
        aspect_ratio_override: str,
        manual_width: int,
        manual_height: int,
        image: Optional[Any] = None,
    ) -> Tuple[int, int]:
        # Manual mode: return provided dimensions; aspect ratio override is ignored here
        if mode == "manual":
            if manual_width % self.DIMENSION_ALIGNMENT != 0 or manual_height % self.DIMENSION_ALIGNMENT != 0:
                raise ValueError(f"manual_width and manual_height must be divisible by {self.DIMENSION_ALIGNMENT}")
            if not (self.MIN_DIMENSION <= manual_width <= self.MAX_DIMENSION) or not (
                self.MIN_DIMENSION <= manual_height <= self.MAX_DIMENSION
            ):
                raise ValueError(
                    f"manual_width and manual_height must be within [{self.MIN_DIMENSION}, {self.MAX_DIMENSION}]"
                )
            return (manual_width, manual_height)

        # Auto mode
        if mode == "auto":
            # If an image is provided, behave like previous image mode
            if image is not None:
                image_height, image_width = self._extract_image_dimensions(image)
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

            # No image provided: require a non-off aspect_ratio_override and use quality + override
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

        # Unknown mode
        raise ValueError(f"Unsupported mode: {mode}")

    def _extract_image_dimensions(self, image: Any) -> Tuple[int, int]:
        # Extract (height, width) from common ComfyUI tensor shapes.
        # Typical shape: [batch, height, width, channels]; can be [height, width, channels] or [height, width].
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
            return self.PRESETS[quality][ratio_key]
        except KeyError:
            raise ValueError(f"Unsupported combination: quality={quality}, ratio={ratio_key}")


