import math
import torch
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from typing import List, Any
from .resolution_nodes import tensor_to_pil_image, pil_image_to_tensor


class KSamplerXYPlot:
    """
    KSampler with built-in XY plotting capabilities for parameter testing.
    Supports plotting multiple parameters across X and Y axes to create comparison grids.
    """

    # Default font settings
    DEFAULT_FONT_SIZE = 30
    MIN_FONT_SIZE = 8
    MAX_FONT_SIZE = 100
    DEFAULT_GRID_SPACING = 0

    # Font color options
    FONT_COLOR_WHITE = "white"
    FONT_COLOR_BLACK = "black"

    # Font file names to try
    FONT_FILES = ["calibri.ttf", "arial.ttf"]

    # Border settings
    BORDER_WIDTH = 2

    # Plot parameter names
    COMMON_PARAMETERS = ['steps', 'cfg', 'denoise', 'seed', 'sampler_name', 'scheduler']
    @classmethod
    def INPUT_TYPES(s):
        import comfy.samplers
        return {
            "required": {
                "model": ("MODEL",),
                "seed": ("INT", {"default": 0, "min": 0, "max": 0xffffffffffffffff, "control_after_generate": True}),
                "steps": ("INT", {"default": 20, "min": 1, "max": 10000}),
                "cfg": ("FLOAT", {"default": 8.0, "min": 0.0, "max": 100.0, "step": 0.1, "round": 0.01}),
                "sampler_name": (comfy.samplers.KSampler.SAMPLERS,),
                "scheduler": (comfy.samplers.KSampler.SCHEDULERS,),
                "positive": ("CONDITIONING",),
                "negative": ("CONDITIONING",),
                "latent_image": ("LATENT",),
                "vae": ("VAE",),
                "denoise": ("FLOAT", {"default": 1.0, "min": 0.0, "max": 1.0, "step": 0.01}),
                "adv_xyPlot": ("ADV_XYPLOT",),
                "plot_font_size": ("INT", {"default": KSamplerXYPlot.DEFAULT_FONT_SIZE, "min": KSamplerXYPlot.MIN_FONT_SIZE, "max": KSamplerXYPlot.MAX_FONT_SIZE, "step": 1}),
                "plot_font_color": ([KSamplerXYPlot.FONT_COLOR_WHITE, KSamplerXYPlot.FONT_COLOR_BLACK], {"default": KSamplerXYPlot.FONT_COLOR_WHITE}),
                "plot_font_border": ("BOOLEAN", {"default": True}),
            },
            "hidden": {
                "prompt": "PROMPT",
                "extra_pnginfo": "EXTRA_PNGINFO",
                "my_unique_id": "UNIQUE_ID",
            },
        }

    RETURN_TYPES = ("IMAGE",)
    RETURN_NAMES = ("xy_plot_image",)
    FUNCTION = "sample"
    CATEGORY = "J1mB091/XY Plot"
    OUTPUT_NODE = True

    def sample(self, model, vae, seed, steps, cfg, sampler_name, scheduler, positive, negative, latent_image, denoise, 
               adv_xyPlot, plot_font_size, plot_font_color, plot_font_border, prompt=None, extra_pnginfo=None, my_unique_id=None):
        
        # XY Plot sampling using advanced XY plot data
        return self._xy_plot_sample(model, seed, steps, cfg, sampler_name, scheduler, positive, negative, latent_image, denoise,
                                   adv_xyPlot, vae, plot_font_size, plot_font_color, plot_font_border, prompt, extra_pnginfo, my_unique_id)
    
    def _single_sample(self, model, seed, steps, cfg, sampler_name, scheduler, positive, negative, latent_image, denoise, vae):
        """Perform a single sampling operation"""
        import comfy.sample
        import comfy.utils
        import latent_preview
        
        # Extract the latent tensor from the dictionary
        latent_tensor = latent_image["samples"]
        latent_tensor = comfy.sample.fix_empty_latent_channels(model, latent_tensor)
        
        # Get batch indices from the original latent dictionary
        batch_inds = latent_image.get("batch_index", None)
        noise = comfy.sample.prepare_noise(latent_tensor, seed, batch_inds)
        
        noise_mask = None
        if "noise_mask" in latent_image:
            noise_mask = latent_image["noise_mask"]
        
        callback = latent_preview.prepare_callback(model, steps)
        disable_pbar = not comfy.utils.PROGRESS_BAR_ENABLED
        
        samples = comfy.sample.sample(model, noise, steps, cfg, sampler_name, scheduler, positive, negative, latent_tensor,
                                     denoise=denoise, noise_mask=noise_mask, callback=callback, disable_pbar=disable_pbar, seed=seed)
        
        out = {"samples": samples}
        
        # Decode image if VAE is provided
        image = None
        if vae is not None:
            decoded_tensor = vae.decode(samples)
            image = tensor_to_pil_image(decoded_tensor)
        
        return (out, image)
    
    def _xy_plot_sample(self, model, seed, steps, cfg, sampler_name, scheduler, positive, negative, latent_image, denoise,
                       adv_xyPlot, vae, plot_font_size, plot_font_color, plot_font_border, prompt, extra_pnginfo, my_unique_id):
        """Perform XY plot sampling using advanced XY plot data"""
        
        # Extract plot data from advanced XY plot format
        x_plot_data = adv_xyPlot.get("x_plot", None)
        y_plot_data = adv_xyPlot.get("y_plot", None)
        plot_grid_spacing = adv_xyPlot.get("grid_spacing", 0)
        
        # Convert ttN plot format to our parameter format
        x_values, x_axis_param = self._extract_plot_values(x_plot_data, "X")
        y_values, y_axis_param = self._extract_plot_values(y_plot_data, "Y") if y_plot_data else ([None], None)

        # Log the values being processed
        print(f"KSamplerXYPlot: X axis ({x_axis_param}): {x_values}")
        print(f"KSamplerXYPlot: Y axis ({y_axis_param}): {y_values}")

        if not x_values or x_values == [None]:
            # Fallback to single sample if no valid values
            result = self._single_sample(model, seed, steps, cfg, sampler_name, scheduler, positive, negative, latent_image, denoise, vae)
            return (result[1],)

        # Create parameter grid
        grid_images = []
        grid_latents = []

        for y_idx, y_val in enumerate(y_values):
            row_images = []
            row_latents = []

            for x_idx, x_val in enumerate(x_values):
                # Create parameter dict for this grid position
                params = {
                    "seed": seed,
                    "steps": steps,
                    "cfg": cfg,
                    "denoise": denoise
                }
                
                # Update with axis values
                params[x_axis_param] = x_val
                if y_axis_param and y_val is not None:
                    params[y_axis_param] = y_val
                
                # Log current sampling progress
                print(f"KSamplerXYPlot: Sampling grid position ({x_idx+1}/{len(x_values)}, {y_idx+1}/{len(y_values)}) - {x_axis_param}={x_val}" + (f", {y_axis_param}={y_val}" if y_axis_param and y_val is not None else ""))
                
                # Sample with these parameters - use grid-specific values where available
                grid_sampler_name = params.get("sampler_name", sampler_name)
                grid_scheduler = params.get("scheduler", scheduler)
                
                result = self._single_sample(model, params["seed"], params["steps"], params["cfg"], 
                                           grid_sampler_name, grid_scheduler, positive, negative, latent_image, 
                                           params["denoise"], vae)
                
                row_latents.append(result[0])
                row_images.append(result[1])
            
            grid_images.append(row_images)
            grid_latents.append(row_latents)
        
        # Create XY plot grid image
        plot_image = self._create_xy_plot_grid(grid_images, x_values, y_values, x_axis_param, y_axis_param, plot_grid_spacing, plot_font_size, plot_font_color, plot_font_border)
        
        # Return only the plot image
        return (plot_image,)
    
    def _extract_plot_values(self, plot_data, axis_name):
        """
        Extract parameter values from ttN advanced XY plot format.
        Converts complex node manipulation format to simple parameter lists.
        """
        if not plot_data:
            return [None], None

        if not isinstance(plot_data, dict):
            print(f"Warning: Invalid plot_data format for {axis_name} axis, expected dict, got {type(plot_data)}")
            return [None], None

        try:
            # ttN plot data is a dictionary where keys are plot points
            # and values contain node manipulation instructions
            values = []
            param_name = "unknown"
            
            for plot_key, plot_info in plot_data.items():
                if plot_key == 'label':
                    continue
                    
                # Extract label for the plot point (this becomes our value)
                label = plot_info.get('label', plot_key)
                
                # Try to extract parameter name from the first node manipulation
                # This is a simplified extraction - ttN format is more complex
                if param_name == "unknown":
                    # Look for common parameter patterns in the plot info
                    for node_id, node_data in plot_info.items():
                        if node_id == 'label':
                            continue
                        if isinstance(node_data, dict):
                            for param, value in node_data.items():
                                if param in self.COMMON_PARAMETERS:
                                    param_name = param
                                    break
                            if param_name != "unknown":
                                break
                
                # Add the label as a value (we'll try to parse it appropriately)
                values.append(label)
            
            # If we couldn't determine the parameter name, use a generic one
            if param_name == "unknown":
                param_name = f"{axis_name.lower()}_param"
            
            # Try to parse values intelligently
            parsed_values = self._parse_extracted_values(values, param_name)
            
            print(f"Extracted {axis_name} axis: param='{param_name}', values={parsed_values}")
            return parsed_values, param_name
            
        except Exception as e:
            print(f"Error extracting {axis_name} plot values: {e}")
            print(f"Plot data structure: {plot_data}")
            # Fallback: create simple numeric values
            fallback_values = list(range(1, len(plot_data) + 1)) if plot_data else [1]
            return fallback_values, f"{axis_name.lower()}_axis"
    
    def _parse_extracted_values(self, values, param_name):
        """Parse extracted values using the same logic as XYPlotParams"""
        try:
            # Try to parse as numbers first
            if all(self._is_numeric(v) for v in values):
                if all(self._is_integer(v) for v in values):
                    return [int(v) for v in values]
                else:
                    return [float(v) for v in values]
            else:
                # Keep as strings
                return [str(v) for v in values]
        except:
            return [str(v) for v in values]
    
    def _is_numeric(self, value):
        """Check if a value can be converted to a number"""
        try:
            float(str(value))
            return True
        except:
            return False
    
    def _is_integer(self, value):
        """Check if a value can be converted to an integer"""
        try:
            int(str(value))
            return str(value).replace('.', '').replace('-', '').isdigit()
        except:
            return False
    
    def _create_xy_plot_grid(self, grid_images: List[List[Any]], x_values: List[Any], y_values: List[Any],
                            x_param: str, y_param: str, plot_grid_spacing: int, plot_font_size: int, plot_font_color: str, plot_font_border: bool) -> Any:
        """Create a grid image from the sampled images"""

        if not grid_images or not grid_images[0]:
            print("Warning: No grid images provided to create_xy_plot_grid")
            return None

        if not x_values or not y_values:
            print("Warning: Empty x_values or y_values provided to create_xy_plot_grid")
            return None
        
        # Get dimensions from first image
        first_img = grid_images[0][0]
        if hasattr(first_img, 'size'):
            img_width, img_height = first_img.size
        elif hasattr(first_img, 'shape'):
            # Handle tensor/numpy array
            if len(first_img.shape) == 3:  # [height, width, channels]
                img_height, img_width = first_img.shape[:2]
            elif len(first_img.shape) == 4:  # [batch, height, width, channels]
                img_height, img_width = first_img.shape[1:3]
            else:
                return None
        else:
            return None
        
        # Calculate grid dimensions
        grid_width = len(x_values)
        grid_height = len(y_values) if y_values[0] is not None else 1
        
        # Create grid image
        total_width = grid_width * img_width + (grid_width - 1) * plot_grid_spacing
        total_height = grid_height * img_height + (grid_height - 1) * plot_grid_spacing
        
        grid_image = Image.new('RGB', (total_width, total_height), (0, 0, 0))
        draw = ImageDraw.Draw(grid_image)
        
        # Try to load a font for labels
        font = None
        for font_file in self.FONT_FILES:
            try:
                font = ImageFont.truetype(font_file, plot_font_size)
                break
            except:
                continue

        if font is None:
            try:
                font = ImageFont.load_default()
            except:
                font = None
        
        # Place images in grid
        for y_idx, y_val in enumerate(y_values):
            for x_idx, x_val in enumerate(x_values):
                if y_idx < len(grid_images) and x_idx < len(grid_images[y_idx]):
                    img = grid_images[y_idx][x_idx]
                    if img is not None:
                        x_pos = x_idx * (img_width + plot_grid_spacing)
                        y_pos = y_idx * (img_height + plot_grid_spacing)
                        
                        # Convert tensor to PIL Image if needed
                        img = tensor_to_pil_image(img)
                        
                        if img is not None:
                            grid_image.paste(img, (x_pos, y_pos))
                            
                            # Add parameter labels with configurable colors and border
                            if font:
                                if y_param and y_val is not None:
                                    label = f"{x_param}: {x_val}\n{y_param}: {y_val}"
                                else:
                                    label = f"{x_param}: {x_val}"
                                
                                # Set font and border colors based on user choice
                                if plot_font_color == self.FONT_COLOR_WHITE:
                                    text_color = (255, 255, 255)
                                    border_color = (0, 0, 0)  # Black border for white text
                                else:  # black
                                    text_color = (0, 0, 0)
                                    border_color = (255, 255, 255)  # White border for black text

                                text_x, text_y = x_pos + 5, y_pos + 5

                                # Draw border if enabled
                                if plot_font_border:
                                    for dx in range(-self.BORDER_WIDTH, self.BORDER_WIDTH + 1):
                                        for dy in range(-self.BORDER_WIDTH, self.BORDER_WIDTH + 1):
                                            if dx != 0 or dy != 0:  # Skip center position
                                                draw.text((text_x + dx, text_y + dy), label, fill=border_color, font=font)
                                
                                # Draw main text on top
                                draw.text((text_x, text_y), label, fill=text_color, font=font)
        
        # Convert PIL Image to tensor format for ComfyUI
        return pil_image_to_tensor(grid_image)

