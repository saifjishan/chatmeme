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

class ImageHandler:
    def __init__(self, scraper_api_key: str, grok_api_key: str):
        self.scraper_api_key = scraper_api_key
        self.grok_api_key = grok_api_key
        self.headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.grok_api_key}"
        }
        self.session = requests.Session()
        self._setup_cache_dir()

    def _setup_cache_dir(self):
        """Setup cache directory for storing processed images."""
        self.cache_dir = os.path.join(os.path.dirname(__file__), 'cache')
        os.makedirs(self.cache_dir, exist_ok=True)

    @lru_cache(maxsize=100)
    def _get_cached_image_path(self, url: str) -> str:
        """Get cached image path using URL hash."""
        url_hash = hashlib.md5(url.encode()).hexdigest()
        return os.path.join(self.cache_dir, f"{url_hash}.jpg")

    def search_images(self, query: str, num_images: int = 3, retries: int = 3) -> list:
        """Search for images using ScraperAPI with retry mechanism."""
        encoded_query = requests.utils.quote(query)
        search_url = f"https://www.google.com/search?q={encoded_query}&tbm=isch"
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        payload = {
            'api_key': self.scraper_api_key,
            'url': search_url,
            'render': True,
            'keep_headers': True
        }
        
        for attempt in range(retries):
            try:
                print(f"Searching for images with query: {query} (Attempt {attempt + 1}/{retries})")
                response = self.session.get('https://api.scraperapi.com/', params=payload, headers=headers)
                response.raise_for_status()
                
                soup = BeautifulSoup(response.text, 'html.parser')
                image_urls = []
                
                # Find image URLs with better quality filtering
                for img in soup.find_all('img'):
                    src = img.get('src', '')
                    if (src.startswith('http') and 
                        any(src.lower().endswith(ext) for ext in ['.jpg', '.jpeg', '.png']) and
                        'thumb' not in src.lower() and
                        'icon' not in src.lower()):
                        image_urls.append(src)
                        if len(image_urls) >= num_images:
                            break
                
                if not image_urls:
                    urls = re.findall('https?://[^"\']*?(?:jpg|png|jpeg)(?!\?thumb)', response.text, re.IGNORECASE)
                    image_urls = urls[:num_images]
                
                return image_urls
                
            except Exception as e:
                print(f"Error searching images (Attempt {attempt + 1}): {str(e)}")
                if attempt < retries - 1:
                    time.sleep(1)  # Wait before retry
                    continue
                return []

    def enhance_image(self, img: Image.Image) -> Image.Image:
        """Enhance image quality."""
        try:
            # Auto-contrast
            enhancer = ImageEnhance.Contrast(img)
            img = enhancer.enhance(1.2)
            
            # Slight sharpening
            enhancer = ImageEnhance.Sharpness(img)
            img = enhancer.enhance(1.1)
            
            return img
        except Exception as e:
            print(f"Error enhancing image: {str(e)}")
            return img

    def create_collage(self, image_urls: List[str], texts: List[str]) -> Optional[bytes]:
        """Create a collage from multiple images with text overlays."""
        try:
            # Download and process images
            images = []
            for url in image_urls:
                try:
                    cache_path = self._get_cached_image_path(url)
                    
                    # Try to load from cache first
                    if os.path.exists(cache_path):
                        img = Image.open(cache_path)
                    else:
                        response = self.session.get(url, timeout=10)
                        response.raise_for_status()
                        img = Image.open(io.BytesIO(response.content))
                        img = ImageOps.exif_transpose(img)
                        img = img.convert('RGB')
                        img = self.enhance_image(img)
                        img.save(cache_path, 'JPEG', quality=95)
                    
                    images.append(img)
                except Exception as e:
                    print(f"Error processing image {url}: {str(e)}")
                    continue

            if not images:
                return None

            # Calculate collage dimensions with better spacing
            num_images = len(images)
            border_width = 10  # Increased border width
            
            if num_images == 1:
                collage_width = 800
                collage_height = 800
            else:
                collage_width = 1200
                collage_height = 800

            # Create white background
            collage = Image.new('RGB', (collage_width, collage_height), 'white')
            draw = ImageDraw.Draw(collage)

            # Calculate positions with better spacing
            if num_images == 1:
                positions = [(border_width, border_width, 
                            collage_width-border_width, collage_height-border_width)]
            elif num_images == 2:
                positions = [
                    (border_width, border_width, 
                     collage_width//2-border_width, collage_height-border_width),
                    (collage_width//2+border_width, border_width, 
                     collage_width-border_width, collage_height-border_width)
                ]
            else:
                positions = [
                    (border_width, border_width, 
                     collage_width//3-border_width, collage_height-border_width),
                    (collage_width//3+border_width, border_width, 
                     2*collage_width//3-border_width, collage_height-border_width),
                    (2*collage_width//3+border_width, border_width, 
                     collage_width-border_width, collage_height-border_width)
                ]

            # Place images in collage with enhanced positioning
            for idx, (img, pos) in enumerate(zip(images, positions)):
                target_width = pos[2] - pos[0]
                target_height = pos[3] - pos[1]
                
                # Better aspect ratio preservation
                img_ratio = img.width / img.height
                target_ratio = target_width / target_height
                
                if img_ratio > target_ratio:
                    new_width = target_width
                    new_height = int(target_width / img_ratio)
                else:
                    new_height = target_height
                    new_width = int(target_height * img_ratio)
                
                img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
                
                x_offset = pos[0] + (target_width - new_width) // 2
                y_offset = pos[1] + (target_height - new_height) // 2
                collage.paste(img, (x_offset, y_offset))

                # Add text with improved styling
                if idx < len(texts):
                    try:
                        # Try multiple font options
                        font_options = ['arial.ttf', 'Arial.ttf', 'DejaVuSans.ttf']
                        font = None
                        font_size = 40
                        
                        for font_name in font_options:
                            try:
                                font = ImageFont.truetype(font_name, font_size)
                                break
                            except:
                                continue
                        
                        if not font:
                            font = ImageFont.load_default()

                        text = texts[idx]
                        text_bbox = draw.textbbox((0, 0), text, font=font)
                        text_width = text_bbox[2] - text_bbox[0]
                        text_x = x_offset + (new_width - text_width) // 2
                        text_y = y_offset + new_height - 80  # Increased padding

                        self._draw_text_with_border(draw, text, (text_x + text_width//2, text_y), font)

                    except Exception as e:
                        print(f"Error adding text overlay: {str(e)}")
                        continue

            # Save the collage with optimization
            img_byte_arr = io.BytesIO()
            collage.save(img_byte_arr, format='PNG', optimize=True, quality=95)
            img_byte_arr.seek(0)
            return img_byte_arr.getvalue()

        except Exception as e:
            print(f"Error creating collage: {str(e)}")
            return None

    def _draw_text_with_border(self, draw: ImageDraw, text: str, position: Tuple[int, int], font: ImageFont):
        """Draw text with improved border and shadow effect."""
        x, y = position
        border_color = "black"
        text_color = "white"
        border_size = 3  # Increased border size
        shadow_offset = 2  # Shadow effect

        # Draw shadow
        draw.text((x+shadow_offset, y+shadow_offset), text, font=font, fill="black", anchor="mm", alpha=128)

        # Draw border
        for adj in range(-border_size, border_size+1):
            for opp in range(-border_size, border_size+1):
                draw.text((x+adj, y+opp), text, font=font, fill=border_color, anchor="mm")

        # Draw main text
        draw.text((x, y), text, font=font, fill=text_color, anchor="mm")
