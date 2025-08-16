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

class NamedAspectRatioMatcher:
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
    CATEGORY = "J1mB091"

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