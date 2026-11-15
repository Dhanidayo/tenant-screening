from typing import Dict, List, Optional
import json
import os
import logging
from dotenv import load_dotenv
from openai import OpenAI, OpenAIError

load_dotenv()

AMBIGUOUS_MIN = 60
AMBIGUOUS_MAX = 80

CLASSIFICATIONS = ("relevant match", "probably not relevant")
DEFAULT_MODEL = "gpt-4o-mini"

SYSTEM_PROMPT = (
    "You review possible matches between a tenant applicant and a blacklist record. "
    "Compare names (allowing for spelling variants, initials and swapped first/last names), "
    "birthdate, nationality and age. Classify the record and give a one-sentence reason."
)

RESPONSE_FORMAT = {
    "type": "json_schema",
    "json_schema": {
        "name": "match_assessment",
        "strict": True,
        "schema": {
            "type": "object",
            "properties": {
                "classification": {"type": "string", "enum": list(CLASSIFICATIONS)},
                "reason": {"type": "string"},
            },
            "required": ["classification", "reason"],
            "additionalProperties": False,
        },
    },
}


class AIHelper:
    def __init__(self, api_key=None, model=None):
        """
        Initialize AIHelper with OpenAI API key.

        Without a key the helper is disabled and every result keeps its
        rule-based (fuzzy matching) classification.

        :param api_key: OpenAI API key; defaults to the OPENAI_API_KEY environment variable
        :param model: chat model name; defaults to OPENAI_MODEL, then DEFAULT_MODEL
        """
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        self.model = model or os.getenv("OPENAI_MODEL") or DEFAULT_MODEL
        self.client = None

        if not self.api_key:
            logging.info("No OPENAI_API_KEY set. Using fuzzy matching only.")
            return

        try:
            self.client = OpenAI(api_key=self.api_key)
        except Exception as e:
            logging.error(f"Failed to initialize OpenAI client: {e}")
            self.client = None

    def query_chatgpt(self, candidate: Dict, search_results: List[Dict]) -> List[Dict]:
        """
        Use OpenAI API to assess ambiguous cases.

        Only results whose match score falls in the ambiguous band are sent to the model.
        If the call fails, or the reply is not one of the allowed classifications,
        the rule-based classification stands.

        :param candidate: the applicant's details
        :param search_results: scored blacklist records from TenantMatcher
        :returns: the same records, with model classifications applied where available
        """
        if not self.client:
            logging.warning("OpenAI client is not available. Returning original search results.")
            return search_results

        if not candidate or not isinstance(candidate, dict):
            logging.error("Invalid candidate data provided.")
            return search_results

        if not search_results or not isinstance(search_results, list):
            logging.error("Invalid search results provided.")
            return search_results

        required_fields = ["first_name", "last_name", "birthdate", "nationality", "age", "match_score"]

        for result in search_results:
            if not all(field in result for field in required_fields):
                logging.warning(f"Skipping invalid result: {result}")
                continue

            if not AMBIGUOUS_MIN <= result["match_score"] <= AMBIGUOUS_MAX:
                continue

            try:
                assessment = self._assess(candidate, result)
            except OpenAIError as api_err:
                logging.error(f"OpenAI API error, keeping rule-based classification: {api_err}")
                continue
            except Exception as e:
                logging.error(f"Unexpected error, keeping rule-based classification: {e}")
                continue

            if assessment is None:
                continue

            result["classification"] = assessment["classification"]
            result["ai_reason"] = assessment["reason"]
            result["classified_by"] = "ai"

        return search_results

    def _assess(self, candidate: Dict, result: Dict) -> Optional[Dict]:
        """
        Ask the model to classify one candidate/record pair.

        :param candidate: the applicant's details
        :param result: one scored blacklist record
        :returns: {"classification", "reason"}, or None when the reply is unusable
        :raises OpenAIError: when the API call fails
        """
        prompt = f"""
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
        """

        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": prompt},
            ],
            response_format=RESPONSE_FORMAT,
            temperature=0,
        )

        message = response.choices[0].message if response and response.choices else None
        if message is None or getattr(message, "refusal", None) or not message.content:
            logging.warning("Model returned no usable answer. Keeping rule-based classification.")
            return None

        try:
            data = json.loads(message.content)
        except json.JSONDecodeError:
            logging.warning("Model reply was not valid JSON. Keeping rule-based classification.")
            return None

        if data.get("classification") not in CLASSIFICATIONS:
            logging.warning(f"Unexpected classification {data.get('classification')!r}. Keeping rule-based classification.")
            return None

        return {"classification": data["classification"], "reason": str(data.get("reason", ""))}
