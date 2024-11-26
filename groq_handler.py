from groq import Groq
import json
from typing import Dict, List, Optional, Union
import asyncio
from concurrent.futures import ThreadPoolExecutor
from PIL import Image
import io
import base64

class GroqHandler:
    def __init__(self, api_key: str):
        self.client = Groq(api_key=api_key)
        self.model = "llama3-groq-8b-8192-tool-use-preview"

    def process_meme_composition(self, image_data: Dict, grok_vision: Dict) -> Dict:
        """Process meme composition using Groq's tool use capabilities."""
        system_prompt = """You are a meme composition expert that processes images based on Grok's vision.
        Given image data and Grok's vision, determine the best way to compose the meme.
        
        Available tools and constraints:
        1. Image Processing:
           - Resolution: 500-700 pixels (both height and width)
           - Text max width: 400 pixels
           - Background removal option
           - Collage creation (1-3 images)
           
        Return a JSON object with:
        {
            "composition_type": "single"|"collage",
            "remove_background": true|false,
            "target_resolution": {"width": int, "height": int},
            "text_placement": [
                {
                    "text": str,
                    "position": {"x": int, "y": int},
                    "max_width": int
                }
            ],
            "layout": {
                "type": "grid"|"vertical"|"horizontal",
                "spacing": int
            }
        }"""

        try:
            # Convert vision and image data to a structured prompt
            prompt = f"""
            Grok's Vision: {json.dumps(grok_vision)}
            Available Images: {json.dumps(image_data)}
            
            Based on this information, determine the optimal meme composition that:
            1. Maintains resolution between 500-700 pixels
            2. Keeps text within 400 pixels width
            3. Decides if background removal would enhance the meme
            4. Chooses the best layout for the content
            """

            completion = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=1000
            )
            
            # Parse and validate response
            response = completion.choices[0].message.content
            result = json.loads(response)
            
            # Validate resolution constraints
            if "target_resolution" in result:
                width = result["target_resolution"]["width"]
                height = result["target_resolution"]["height"]
                result["target_resolution"]["width"] = max(500, min(700, width))
                result["target_resolution"]["height"] = max(500, min(700, height))
            
            # Validate text placement
            for text_obj in result.get("text_placement", []):
                text_obj["max_width"] = min(400, text_obj.get("max_width", 400))
            
            return result

        except Exception as e:
            print(f"Error in process_meme_composition: {str(e)}")
            # Return default composition if something goes wrong
            return {
                "composition_type": "single",
                "remove_background": False,
                "target_resolution": {"width": 600, "height": 600},
                "text_placement": [
                    {
                        "text": list(image_data.values())[0]["caption"],
                        "position": {"x": 300, "y": 550},
                        "max_width": 400
                    }
                ],
                "layout": {"type": "grid", "spacing": 20}
            }

    def analyze_meme_request(self, prompt: str) -> Dict:
        """Analyze meme request and format response using Groq."""
        system_prompt = """You are a meme analysis assistant that helps format meme requests into structured data.
        Given a meme request, analyze it and return a JSON object with:
        1. Key subjects or concepts (up to 3)
        2. Specific image search queries for each subject
        3. Funny captions for each image
        4. Visual style suggestions
        
        Always return valid JSON in this format:
        {
            "subjects": ["subject1", "subject2", "subject3"],
            "search_queries": ["detailed query 1", "detailed query 2", "detailed query 3"],
            "captions": ["funny caption 1", "funny caption 2", "funny caption 3"],
            "style": {
                "mood": "funny|dramatic|sarcastic",
                "visual_effects": ["effect1", "effect2"],
                "composition": "single|multi_panel"
            }
        }"""

        try:
            completion = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": f"Analyze this meme request: {prompt}"}
                ],
                temperature=0.7,
                max_tokens=500
            )
            
            # Parse and validate response
            response = completion.choices[0].message.content
            result = json.loads(response)
            
            # Ensure all lists have the same length
            min_length = min(len(result["subjects"]), len(result["search_queries"]), len(result["captions"]))
            result["subjects"] = result["subjects"][:min_length]
            result["search_queries"] = result["search_queries"][:min_length]
            result["captions"] = result["captions"][:min_length]
            
            return result

        except Exception as e:
            print(f"Error in analyze_meme_request: {str(e)}")
            return None

    async def analyze_meme_request_async(self, prompt: str) -> Dict:
        """Asynchronous version of analyze_meme_request."""
        loop = asyncio.get_event_loop()
        with ThreadPoolExecutor() as pool:
            result = await loop.run_in_executor(pool, self.analyze_meme_request, prompt)
            return result

    def generate_meme_text(self, context: Dict) -> List[str]:
        """Generate meme text based on context."""
        system_prompt = """You are a witty meme caption generator.
        Given the context and subjects, create funny and relevant captions.
        Keep captions short, punchy, and meme-worthy.
        Return only the list of captions."""

        try:
            completion = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": f"Generate captions for these subjects: {json.dumps(context['subjects'])}"}
                ],
                temperature=0.8,
                max_tokens=200
            )
            
            response = completion.choices[0].message.content
            # Extract captions from response
            captions = json.loads(response) if '[' in response else [response]
            return captions[:len(context['subjects'])]

        except Exception as e:
            print(f"Error generating meme text: {str(e)}")
            return context.get('captions', ["When the AI can't think of a caption 🤔"])
