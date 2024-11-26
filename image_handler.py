import requests
import json
from PIL import Image, ImageDraw, ImageFont, ImageOps, ImageEnhance
import io
import os
import base64
import random
from typing import Tuple, Optional, List, Dict
import re
from bs4 import BeautifulSoup
from functools import lru_cache
import hashlib
import time
from duckduckgo_search import DDGS
try:
    from rembg import remove
    REMBG_AVAILABLE = True
except ImportError:
    REMBG_AVAILABLE = False
    print("Warning: rembg package not available. Background removal will be disabled.")
import numpy as np

class ImageHandler:
    def __init__(self, grok_api_key: str):
        self.grok_api_key = grok_api_key
        self.headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.grok_api_key}"
        }
        self.session = requests.Session()
        self._setup_cache_dir()
        self.MAX_SIZE = 700  # Maximum dimension for any image
        self.MIN_SIZE = 300  # Minimum dimension for any image

    def _setup_cache_dir(self):
        """Setup cache directory for storing processed images."""
        self.cache_dir = os.path.join(os.path.dirname(__file__), 'cache')
        os.makedirs(self.cache_dir, exist_ok=True)

    @lru_cache(maxsize=100)
    def _get_cached_image_path(self, url: str) -> str:
        """Get cached image path using URL hash."""
        url_hash = hashlib.md5(url.encode()).hexdigest()
        return os.path.join(self.cache_dir, f"{url_hash}.jpg")

    def search_images(self, query: str, num_images: int = 3) -> list:
        """Search for images using DuckDuckGo."""
        try:
            print(f"Searching for images with query: {query}")
            with DDGS() as ddgs:
                images = list(ddgs.images(
                    query,
                    max_results=num_images * 2,  # Get extra images in case some fail
                    type='photo'
                ))

            # Filter and validate images
            valid_urls = []
            for img in images:
                if img['image'].startswith('http') and any(
                    img['image'].lower().endswith(ext) 
                    for ext in ['.jpg', '.jpeg', '.png']
                ):
                    valid_urls.append(img['image'])
                if len(valid_urls) >= num_images:
                    break

            return valid_urls[:num_images]

        except Exception as e:
            print(f"Error searching images: {str(e)}")
            return []

    def remove_background(self, img: Image.Image) -> Image.Image:
        """Remove background from image using rembg."""
        if not REMBG_AVAILABLE:
            print("Warning: Background removal requested but rembg is not available.")
            return img
            
        try:
            # Convert to RGB if image is RGBA
            if img.mode == 'RGBA':
                img = img.convert('RGB')
            
            # Remove background
            output = remove(img)
            return Image.open(io.BytesIO(output))
        except Exception as e:
            print(f"Error removing background: {str(e)}")
            return img

    def resize_image(self, img: Image.Image, target_size: Tuple[int, int]) -> Image.Image:
        """Resize image while maintaining aspect ratio within bounds."""
        # Calculate target size while maintaining aspect ratio
        aspect = img.width / img.height
        if aspect > 1:
            # Wider than tall
            new_width = min(target_size[0], self.MAX_SIZE)
            new_height = int(new_width / aspect)
            if new_height < self.MIN_SIZE:
                new_height = self.MIN_SIZE
                new_width = int(new_height * aspect)
        else:
            # Taller than wide
            new_height = min(target_size[1], self.MAX_SIZE)
            new_width = int(new_height * aspect)
            if new_width < self.MIN_SIZE:
                new_width = self.MIN_SIZE
                new_height = int(new_width / aspect)

        return img.resize((new_width, new_height), Image.Resampling.LANCZOS)

    def create_collage(self, image_urls: List[str], texts: List[str], remove_bg: bool = False) -> Optional[bytes]:
        """Create a collage from multiple images with text overlays."""
        try:
            # Download and process images
            images = []
            for url in image_urls:
                try:
                    cache_path = self._get_cached_image_path(url)
                    
                    if os.path.exists(cache_path):
                        img = Image.open(cache_path)
                    else:
                        response = self.session.get(url, timeout=10)
                        response.raise_for_status()
                        img = Image.open(io.BytesIO(response.content))
                        img = ImageOps.exif_transpose(img)
                        img = img.convert('RGBA' if remove_bg else 'RGB')
                        
                        # Remove background if requested
                        if remove_bg:
                            img = self.remove_background(img)
                        
                        img.save(cache_path, 'PNG' if remove_bg else 'JPEG', quality=95)
                    
                    images.append(img)
                except Exception as e:
                    print(f"Error processing image {url}: {str(e)}")
                    continue

            if not images:
                return None

            # Calculate collage dimensions based on content
            num_images = len(images)
            padding = 20
            
            if num_images == 1:
                # Single image with text
                base_width = 600
                base_height = 600
                img = self.resize_image(images[0], (base_width - 2*padding, base_height - 2*padding))
                collage_width = img.width + 2*padding
                collage_height = img.height + 2*padding + 100  # Extra space for text
                
                collage = Image.new('RGBA' if remove_bg else 'RGB', 
                                  (collage_width, collage_height), 
                                  (255, 255, 255, 0) if remove_bg else 'white')
                
                # Center image
                x_offset = (collage_width - img.width) // 2
                y_offset = padding
                if remove_bg:
                    collage.paste(img, (x_offset, y_offset), img)
                else:
                    collage.paste(img, (x_offset, y_offset))
                
                # Add text
                if texts:
                    self.add_text_overlay(collage, texts[0], (collage_width//2, collage_height-60))
            
            else:
                # Multiple images
                max_width = 1000
                max_height = 600
                
                # Calculate grid layout
                if num_images == 2:
                    cols = 2
                    rows = 1
                else:
                    cols = 3
                    rows = (num_images + 2) // 3
                
                cell_width = (max_width - (cols+1)*padding) // cols
                cell_height = (max_height - (rows+1)*padding) // rows
                
                collage_width = max_width
                collage_height = max_height
                
                collage = Image.new('RGBA' if remove_bg else 'RGB', 
                                  (collage_width, collage_height),
                                  (255, 255, 255, 0) if remove_bg else 'white')
                
                # Place images in grid
                for idx, img in enumerate(images):
                    row = idx // cols
                    col = idx % cols
                    
                    img = self.resize_image(img, (cell_width, cell_height))
                    x = padding + col * (cell_width + padding)
                    y = padding + row * (cell_height + padding)
                    
                    if remove_bg:
                        collage.paste(img, (x, y), img)
                    else:
                        collage.paste(img, (x, y))
                    
                    # Add text
                    if idx < len(texts):
                        text_y = y + cell_height - 40
                        self.add_text_overlay(collage, texts[idx], 
                                           (x + cell_width//2, text_y))

            # Convert to bytes
            img_byte_arr = io.BytesIO()
            collage.save(img_byte_arr, format='PNG', optimize=True)
            img_byte_arr.seek(0)
            return img_byte_arr.getvalue()

        except Exception as e:
            print(f"Error creating collage: {str(e)}")
            return None

    def add_text_overlay(self, img: Image.Image, text: str, position: Tuple[int, int]):
        """Add text overlay with better positioning and wrapping."""
        draw = ImageDraw.Draw(img)
        
        # Try multiple font options with dynamic sizing
        font_options = ['arial.ttf', 'Arial.ttf', 'DejaVuSans.ttf']
        font_size = 40
        font = None
        
        for font_name in font_options:
            try:
                font = ImageFont.truetype(font_name, font_size)
                break
            except:
                continue
        
        if not font:
            font = ImageFont.load_default()

        # Word wrap text
        words = text.split()
        lines = []
        current_line = []
        max_width = img.width * 0.8  # 80% of image width
        
        for word in words:
            current_line.append(word)
            test_line = ' '.join(current_line)
            bbox = draw.textbbox((0, 0), test_line, font=font)
            if bbox[2] - bbox[0] > max_width:
                if len(current_line) == 1:
                    lines.append(current_line[0])
                    current_line = []
                else:
                    current_line.pop()
                    lines.append(' '.join(current_line))
                    current_line = [word]
        
        if current_line:
            lines.append(' '.join(current_line))

        # Draw text lines
        line_height = font_size + 5
        total_height = len(lines) * line_height
        start_y = position[1] - total_height // 2

        for i, line in enumerate(lines):
            bbox = draw.textbbox((0, 0), line, font=font)
            text_width = bbox[2] - bbox[0]
            x = position[0] - text_width // 2
            y = start_y + i * line_height
            
            # Draw shadow
            shadow_offset = 2
            draw.text((x + shadow_offset, y + shadow_offset), 
                     line, font=font, fill="black", alpha=128)
            
            # Draw border
            border_size = 3
            for adj in range(-border_size, border_size+1):
                for opp in range(-border_size, border_size+1):
                    draw.text((x + adj, y + opp), 
                            line, font=font, fill="black")
            
            # Draw main text
            draw.text((x, y), line, font=font, fill="white")

    def create_meme(self, image_data: Dict, composition: Dict) -> Optional[bytes]:
        """Create a meme based on Groq's composition instructions."""
        try:
            # Download and process images
            processed_images = {}
            for img_id, img_info in image_data.items():
                try:
                    cache_path = self._get_cached_image_path(img_info["url"])
                    
                    if os.path.exists(cache_path):
                        img = Image.open(cache_path)
                    else:
                        response = self.session.get(img_info["url"], timeout=10)
                        response.raise_for_status()
                        img = Image.open(io.BytesIO(response.content))
                        img = ImageOps.exif_transpose(img)
                        img = img.convert('RGBA' if composition["remove_background"] else 'RGB')
                        
                        # Remove background if requested
                        if composition["remove_background"]:
                            img = self.remove_background(img)
                        
                        img.save(cache_path, 'PNG' if composition["remove_background"] else 'JPEG', quality=95)
                    
                    processed_images[img_id] = img
                except Exception as e:
                    print(f"Error processing image {img_info['url']}: {str(e)}")
                    continue

            if not processed_images:
                return None

            # Create canvas based on composition
            target_width = composition["target_resolution"]["width"]
            target_height = composition["target_resolution"]["height"]
            canvas = Image.new('RGBA' if composition["remove_background"] else 'RGB',
                             (target_width, target_height),
                             (255, 255, 255, 0) if composition["remove_background"] else 'white')

            # Apply layout based on composition type
            if composition["composition_type"] == "single":
                # Single image layout
                img = list(processed_images.values())[0]
                img = self.resize_image(img, (target_width, target_height))
                x = (target_width - img.width) // 2
                y = (target_height - img.height) // 2
                if composition["remove_background"]:
                    canvas.paste(img, (x, y), img)
                else:
                    canvas.paste(img, (x, y))
            else:
                # Collage layout
                layout = composition["layout"]
                spacing = layout["spacing"]
                
                if layout["type"] == "grid":
                    cols = 2 if len(processed_images) == 2 else 3
                    rows = (len(processed_images) + cols - 1) // cols
                    cell_width = (target_width - (cols + 1) * spacing) // cols
                    cell_height = (target_height - (rows + 1) * spacing) // rows
                    
                    for idx, img in enumerate(processed_images.values()):
                        row = idx // cols
                        col = idx % cols
                        
                        img = self.resize_image(img, (cell_width, cell_height))
                        x = spacing + col * (cell_width + spacing)
                        y = spacing + row * (cell_height + spacing)
                        if composition["remove_background"]:
                            canvas.paste(img, (x, y), img)
                        else:
                            canvas.paste(img, (x, y))
                
                elif layout["type"] in ["vertical", "horizontal"]:
                    is_vertical = layout["type"] == "vertical"
                    count = len(processed_images)
                    if is_vertical:
                        cell_width = target_width - 2 * spacing
                        cell_height = (target_height - (count + 1) * spacing) // count
                    else:
                        cell_width = (target_width - (count + 1) * spacing) // count
                        cell_height = target_height - 2 * spacing
                    
                    for idx, img in enumerate(processed_images.values()):
                        img = self.resize_image(img, (cell_width, cell_height))
                        if is_vertical:
                            x = spacing
                            y = spacing + idx * (cell_height + spacing)
                        else:
                            x = spacing + idx * (cell_width + spacing)
                            y = spacing
                        if composition["remove_background"]:
                            canvas.paste(img, (x, y), img)
                        else:
                            canvas.paste(img, (x, y))

            # Add text overlays
            for text_info in composition["text_placement"]:
                self.add_text_overlay(
                    canvas,
                    text_info["text"],
                    (text_info["position"]["x"], text_info["position"]["y"]),
                    max_width=text_info["max_width"]
                )

            # Convert to bytes
            img_byte_arr = io.BytesIO()
            canvas.save(img_byte_arr, format='PNG', optimize=True)
            img_byte_arr.seek(0)
            return img_byte_arr.getvalue()

        except Exception as e:
            print(f"Error creating meme: {str(e)}")
            return None
