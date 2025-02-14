import json
from typing import Dict
import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

class AIHelper:
    def __init__(self):
        """
        Initialize AIHelper by assigning API key and client.
        """
        api_key = os.getenv("OPENAI_API_KEY")

        if not api_key:
            raise ValueError("API key not found! Set OPENAI_API_KEY in a .env file or environment variable.")
        
        self.client = OpenAI(api_key=api_key)

    def query_chatgpt(self, tenant: Dict[str, str], blacklist_entry: Dict[str, str]) -> Dict[str, str]:
        """
        Prompt ChatGPT API to assess if the blacklist entry is a match.
        Returns structured output with classification and reasoning.
        """
        prompt = f"""
        Given the following tenant information and blacklist entry, determine if it's a likely match.

        Tenant: {json.dumps(tenant)}
        Blacklist Entry: {json.dumps(blacklist_entry)}

        Respond with a JSON object:
        {{
            "classification": "Relevant Match" or "Probably Not Relevant",
            "reasoning": "Short explanation"
        }}
        """

        response = self.client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.2,
            response_format="json"
        )
        
        try:
            return json.loads(response["choices"][0]["message"]["content"])
        except json.JSONDecodeError:
            return {"classification": "Probably Not Relevant", "reasoning": "Failed to parse AI response"}
