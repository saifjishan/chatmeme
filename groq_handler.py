from groq import Groq
import json
from typing import Dict, List, Optional, Union
import asyncio
from concurrent.futures import ThreadPoolExecutor

class GroqHandler:
    def __init__(self, api_key: str):
        self.client = Groq(api_key=api_key)
        self.model = "llama3-groq-8b-8192-tool-use-preview"

    def analyze_meme_request(self, prompt: str) -> Dict:
        """Analyze meme request and format response using Groq."""
        system_prompt = """You are a meme analysis assistant that helps format meme requests into structured data.
        Given a meme request, analyze it and return a JSON object with:
        1. Key subjects or concepts (up to 3)
        2. Specific image search queries for each subject
        3. Funny captions for each image
        
        Always return valid JSON in this format:
        {
            "subjects": ["subject1", "subject2", "subject3"],
            "search_queries": ["detailed query 1", "detailed query 2", "detailed query 3"],
            "captions": ["funny caption 1", "funny caption 2", "funny caption 3"]
        }
        
        Keep queries specific and captions short and funny."""

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
            print(f"Error in Groq analysis: {str(e)}")
            # Return a basic structure if there's an error
            return {
                "subjects": ["meme"],
                "search_queries": [prompt],
                "captions": ["When the meme doesn't work as expected"]
            }

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
