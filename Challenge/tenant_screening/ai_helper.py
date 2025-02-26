from typing import Dict, List
import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

class AIHelper:
    def __init__(self, api_key=None):
        """
        Initialize AIHelper with OpenAI API key.
        """
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")

        if not self.api_key:
            raise ValueError("API key not found! Set OPENAI_API_KEY in a .env file or environment variable.")
        
        self.client = OpenAI(api_key=self.api_key)

    def query_chatgpt(self, candidate: Dict, search_results: List[Dict]) -> List[Dict]:
        """Use OpenAI API to assess ambiguous cases."""
        if not self.client:
            return search_results  
        
        for result in search_results:
            if 60 <= result["match_score"] <= 80:  
                prompt = f"""
                Given the following details, assess if the search result is a match for the candidate.

                Candidate: 
                Name: {candidate['first_name']} {candidate['last_name']}
                Birthdate: {candidate['birthdate']}
                Nationality: {candidate['nationality']}
                Age: {candidate['age']}
                
                Search Result: 
                Name: {result['first_name']} {result['last_name']}
                Birthdate: {result['birthdate']}
                Nationality: {result['nationality']}
                Age: {result['age']}

                Provide a classification as either 'relevant match' or 'probably not relevant' based on these details.
                """

                response = self.client.completions.create(
                    model="gpt-3.5-turbo-instruct",
                    prompt=prompt,
                    max_tokens=50
                )

                result["classification"] = response.choices[0].text.strip()

        return search_results


