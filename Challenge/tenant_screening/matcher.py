import os
import re
import json
import logging
from typing import Dict, List
from fuzzywuzzy.process import fuzz
from .ai_helper import AIHelper

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

class TenantMatcher:
    def __init__(self, tenant_data: Dict, blacklist_data: List[Dict], api_helper: AIHelper):
        """
        Initialize with tenant screening data, blacklist data, and AIHelper instance.

        :param tenant_data: dict with details (first_name, last_name, birthdate, nationality, etc.)
        :param blacklist_data: list of dicts with potential matches
        :param api_helper: AIHelper instance to query ChatGPT for validation
        """
        self.tenant_data = tenant_data
        self.blacklist_data = [
            entry for entry in blacklist_data if entry.get("pipeline", {}).get("type") == "refinitiv-blacklist"
        ]
        self.api_helper = api_helper

    def normalize_name(self, first_name: str, last_name: str) -> str:
        """Normalize first and last names separately, then join for comparison."""
        def clean_name(name: str) -> str:
            name = re.sub(r'\W+', ' ', name).strip().lower()
            stopwords = {"de", "la", "del", "los", "las"}
            return " ".join(part for part in name.split() if part not in stopwords)

        return f"{clean_name(first_name)} {clean_name(last_name)}"

    def calculate_match_score(self, candidate: Dict, search_results: List[Dict]) -> List[Dict]:
        """Compare candidate details with search results using fuzzy matching."""
        normalized_candidate = self.normalize_name(candidate["first_name"], candidate["last_name"])

        for result in search_results:
            result_name = self.normalize_name(result.get("first_name", ""), result.get("last_name", ""))
            score = fuzz.ratio(normalized_candidate, result_name)

            # Additional matching criteria
            birthdate_match = candidate.get("birthdate") == result.get("birthdate")
            nationality_match = candidate.get("nationality") == result.get("nationality")
            age_match = candidate.get("age") == result.get("age")

            additional_score = sum([birthdate_match, nationality_match, age_match]) * 10
            final_score = min(score + additional_score, 100)

            confidence = (
                "High" if final_score > 90 else
                "Medium" if final_score > 75 else
                "Low"
            )

            result.update({
                "match_score": final_score,
                "confidence": confidence,
                "classification": "relevant match" if final_score > 80 else "probably not relevant"
            })

            logger.info(f"Processed {result['first_name']} {result['last_name']} - Score: {final_score}, Confidence: {confidence}")

        return search_results

    def classify(self, candidate: Dict, search_results: List[Dict]) -> List[Dict]:
        """Full classification pipeline using name, birthdate, nationality, and age."""
        search_results = self.calculate_match_score(candidate, search_results)

        try:
            search_results = self.api_helper.query_chatgpt(candidate, search_results)
        except Exception as e:
            logger.error(f"ChatGPT API call failed: {e}")
            logger.warning("Skipping AI classification and returning only match scores.")

        return search_results



# Example usage
if __name__ == "__main__":
    data_dir = "data"
    input_file = os.path.join(data_dir, "input.json")
    output_file = os.path.join(data_dir, "output.json")

    os.makedirs(data_dir, exist_ok=True)

    try:
        with open(input_file, "r", encoding="utf-8") as f:
            input_data = json.load(f)
    except FileNotFoundError:
        logger.error(f"Input file '{input_file}' not found. Please provide valid data.")
        exit(1)
    except json.JSONDecodeError as e:
        logger.error(f"Error reading JSON file: {e}")
        exit(1)

    candidate_info = input_data.get("candidate", {})
    raw_results = input_data.get("search_results", [])

    if not candidate_info or not raw_results:
        logger.warning("Candidate info or search results missing in input.json.")

    classifier = TenantMatcher(
        tenant_data=candidate_info,
        blacklist_data=raw_results,
        api_helper=AIHelper(os.getenv("OPENAI_API_KEY"))
    )

    try:
        classified_results = classifier.classify(candidate_info, raw_results)
        
        try:
            classified_results.sort(key=lambda x: -x.get("match_score", 0))
            logger.info("Sorting completed.")
        except Exception as e:
            logger.error(f"Sorting failed: {e}")

        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(classified_results, f, indent=2)

        logger.info(f"Classification results saved to {output_file}")

    except Exception as e:
        logger.error(f"Error during classification: {e}")
        exit(1)
