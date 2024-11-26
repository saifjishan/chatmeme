from PIL import Image, ImageDraw, ImageFont
import io
import os
from typing import List, Dict, Optional, Tuple
from duckduckgo_search import DDGS
import requests
from functools import lru_cache

class ImageHandler:
    def __init__(self):
        self.ddgs = DDGS()
        self.cache_dir = "cache"
        self._setup_cache_dir()
        
    def _setup_cache_dir(self):
        """Setup cache directory for storing processed images."""
        if not os.path.exists(self.cache_dir):
            os.makedirs(self.cache_dir)

    @lru_cache(maxsize=100)
    def search_images(self, query: str, num_images: int = 1) -> List[str]:
        """Search for images using DuckDuckGo."""
        try:
            results = list(self.ddgs.images(
                query,
                max_results=num_images,
                type="photo"
            ))
            return [result["image"] for result in results] if results else []
        except Exception as e:
            print(f"Error searching images: {str(e)}")
            return []

    def download_image(self, url: str) -> Optional[Image.Image]:
        """Download and open an image from URL."""
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            return Image.open(io.BytesIO(response.content))
        except Exception as e:
            print(f"Error downloading image: {str(e)}")
            return None

    def add_text_to_image(self, image: Image.Image, text: str, position: str = "bottom") -> Image.Image:
        """Add text to image at specified position."""
        try:
            # Create a copy of the image
            img = image.copy()
            draw = ImageDraw.Draw(img)
            
            # Calculate font size based on image size
            font_size = int(min(img.size) * 0.08)  # 8% of smallest dimension
            try:
                font = ImageFont.truetype("arial.ttf", font_size)
            except:
                font = ImageFont.load_default()

            # Calculate text size and position
            text_width, text_height = draw.textsize(text, font=font)
            image_width, image_height = img.size
            
            # Position text
            if position == "top":
                x = (image_width - text_width) // 2
                y = text_height // 2
            else:  # bottom
                x = (image_width - text_width) // 2
                y = image_height - text_height * 1.5

            # Add text shadow for better visibility
            shadow_offset = max(1, font_size // 20)
            draw.text((x + shadow_offset, y + shadow_offset), text, font=font, fill="black")
            draw.text((x, y), text, font=font, fill="white")

            return img
        except Exception as e:
            print(f"Error adding text to image: {str(e)}")
            return image

    def create_meme(self, search_query: str, caption: str) -> Optional[bytes]:
        """Create a meme from search query and caption."""
        try:
            # Search for image
            image_urls = self.search_images(search_query)
            if not image_urls:
                return None

            # Download first image
            image = self.download_image(image_urls[0])
            if not image:
                return None

            # Resize image if too large
            max_size = (800, 800)
            if image.size[0] > max_size[0] or image.size[1] > max_size[1]:
                image.thumbnail(max_size, Image.LANCZOS)

            # Add caption
            meme = self.add_text_to_image(image, caption)

            # Convert to bytes
            img_byte_arr = io.BytesIO()
            meme.save(img_byte_arr, format='PNG')
            img_byte_arr.seek(0)
            return img_byte_arr.getvalue()

        except Exception as e:
            print(f"Error creating meme: {str(e)}")
            return None
