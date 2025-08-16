from typing import Any, Tuple


class ImageDimensions:
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
	CATEGORY = "J1mB091"

	def dimensions(self, image: Any) -> Tuple[int, int]:
		height, width = self._extract_image_dimensions(image)
		return int(width), int(height)

	def _extract_image_dimensions(self, image: Any) -> Tuple[int, int]:
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


