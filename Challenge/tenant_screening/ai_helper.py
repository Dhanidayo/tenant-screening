from typing import Dict, List
import os
import logging
from dotenv import load_dotenv
from openai import OpenAI, OpenAIError

load_dotenv()

class AIHelper:
    def __init__(self, api_key=None):
        """
        Initialize AIHelper with OpenAI API key.
        """
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")

        if not self.api_key:
            raise ValueError("API key not found! Set OPENAI_API_KEY in a .env file or environment variable.")

        try:
            self.client = OpenAI(api_key=self.api_key)
        except Exception as e:
            logging.error(f"Failed to initialize OpenAI client: {e}")
            self.client = None

    def query_chatgpt(self, candidate: Dict, search_results: List[Dict]) -> List[Dict]:
        """Use OpenAI API to assess ambiguous cases."""
        if not self.client:
            logging.warning("OpenAI client is not available. Returning original search results.")
            return search_results  

        if not candidate or not isinstance(candidate, dict):
            logging.error("Invalid candidate data provided.")
            return search_results

        if not search_results or not isinstance(search_results, list):
            logging.error("Invalid search results provided.")
            return search_results

        for result in search_results:
            try:
                required_fields = ["first_name", "last_name", "birthdate", "nationality", "age", "match_score"]
                if not all(field in result for field in required_fields):
                    logging.warning(f"Skipping invalid result: {result}")
                    continue

                if 60 <= result["match_score"] <= 80:  
                    prompt = f"""
                    Given the following details, assess if the search result is a match for the candidate.

                    Candidate: 
                    Name: {candidate.get('first_name', 'N/A')} {candidate.get('last_name', 'N/A')}
                    Birthdate: {candidate.get('birthdate', 'N/A')}
                    Nationality: {candidate.get('nationality', 'N/A')}
                    Age: {candidate.get('age', 'N/A')}
                    
                    Search Result: 
                    Name: {result.get('first_name', 'N/A')} {result.get('last_name', 'N/A')}
                    Birthdate: {result.get('birthdate', 'N/A')}
                    Nationality: {result.get('nationality', 'N/A')}
                    Age: {result.get('age', 'N/A')}

                    Provide a classification as either 'relevant match' or 'probably not relevant' based on these details.
                    """

                    response = self.client.completions.create(
                        model="gpt-3.5-turbo-instruct",
                        prompt=prompt,
                        max_tokens=50
                    )

                    if response and response.choices:
                        result["classification"] = response.choices[0].text.strip()
                    else:
                        logging.warning("OpenAI API returned an empty response.")
                        result["classification"] = "uncertain"

            except OpenAIError as api_err:
                logging.error(f"OpenAI API error: {api_err}")
                result["classification"] = "API error"

            except Exception as e:
                logging.error(f"Unexpected error processing search result: {e}")
                result["classification"] = "error"

        return search_results
