from groq import Groq
from typing import Dict, Optional
import json

class GroqHandler:
    def __init__(self, api_key: str):
        self.client = Groq(api_key=api_key)
        self.model = "mixtral-8x7b-32768"  # Using stable model

    def analyze_meme_request(self, prompt: str) -> Optional[Dict]:
        """Analyze the meme request and generate search queries."""
        system_prompt = """You are a meme analysis expert. Given a meme request, extract:
        1. Main subjects/topics
        2. Image search queries
        3. Captions or text to add
        
        IMPORTANT: You must return a valid JSON object in exactly this format:
        {
            "subjects": ["list of main subjects"],
            "search_queries": ["list of image search terms"],
            "captions": ["list of captions for each image"]
        }
        Each list must contain at least one item. Do not include any other text or explanation."""

        try:
            completion = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=500
            )
            
            content = completion.choices[0].message.content.strip()
            
            # Validate JSON structure
            try:
                data = json.loads(content)
                if not all(key in data for key in ["subjects", "search_queries", "captions"]):
                    raise ValueError("Missing required fields in response")
                if not all(isinstance(data[key], list) and len(data[key]) > 0 for key in ["subjects", "search_queries", "captions"]):
                    raise ValueError("Empty or invalid lists in response")
                return data
            except (json.JSONDecodeError, ValueError) as e:
                print(f"Invalid response format: {str(e)}\nResponse: {content}")
                return None
                
        except Exception as e:
            print(f"Error analyzing meme request: {str(e)}")
            return None

    def format_meme_text(self, text: str) -> str:
        """Format text for meme display."""
        try:
            completion = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a meme text formatter. Make the text punchy and meme-worthy."},
                    {"role": "user", "content": text}
                ],
                temperature=0.7,
                max_tokens=100
            )
            return completion.choices[0].message.content
        except Exception as e:
            print(f"Error formatting meme text: {str(e)}")
            return text
