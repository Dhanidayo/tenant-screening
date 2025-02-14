import re
import json
from typing import Dict, List
from fuzzywuzzy import fuzz
from openai import OpenAIError, RateLimitError, AuthenticationError
from tenant_screening.ai_helper import AIHelper

class TenantMatcher:       
    def __init__(self, tenant_data, blacklist_data, api_helper: AIHelper, threshold: int = 80):
        """
        Initialize with tenant screening data, blacklist data, and AIHelper instance.

        :param tenant_data: dict with details (name, birthdate, nationality, etc.)
        :param blacklist_data: list of dicts with potential matches
        :param api_helper: AIHelper instance to query ChatGPT for worldcheck list validation
        :param threshold: Minimum similarity score for a match
        """

        self.tenant_data = tenant_data
        self.blacklist_data = [
            entry for entry in blacklist_data if entry.get("pipeline", {}).get("type") == "refinitiv-blacklist"
        ]
        self.api_helper = api_helper
        self.threshold = threshold


    def normalize_name(self, name):
        """Normalize names for better comparison, handling multiple-name structures for regions like LATAM."""
        name = re.sub(r'\W+', ' ', name).strip().lower()

        stopwords = {"de", "la", "del", "los", "las"}
        name_parts = [part for part in name.split() if part not in stopwords]
        
        return " ".join(name_parts)


    def calculate_match_score(self, record):
        """
        Calculate name similarity score using fuzzy matching.
        
        :param record: Blacklist entry
        :return: Score (0 to 100)
        """
        tenant_name = self.normalize_name(self.tenant_data.get("name", ""))
        record_name = self.normalize_name(record.get("name", ""))
        
        return fuzz.ratio(tenant_name, record_name)
    
    def assess_risk(self, record: Dict[str, str]) -> Dict[str, str]:
        """
        Assess the blacklist match using AIHelper. If AIHelper fails, fall back to fuzzy matching.
        """
        try:
            ai_result = self.api_helper.query_chatgpt(self.tenant_data, record)
            classification = ai_result["classification"]
            reasoning = ai_result["reasoning"]
        except (RateLimitError, AuthenticationError, OpenAIError) as e:
            print(f"\nAI API Error: {e}")
            print("Using fallback matching based on fuzzy name similarity and metadata.\n")

            match_score = self.calculate_match_score(record)
            dob_match = self.tenant_data.get("dob") == record.get("dob")
            nationality_match = self.tenant_data.get("nationality") == record.get("nationality")

            if match_score >= self.threshold and dob_match:
                classification = "Relevant Match"
                reasoning = "High name similarity and DOB match."
            elif match_score >= self.threshold - 10 and nationality_match:
                classification = "Moderate Match"
                reasoning = "Name similarity is close and same nationality."
            else:
                classification = "Probably Not Relevant"
                reasoning = "Low name similarity or mismatched metadata."

        return {
            "name": record.get("name", ""),
            "dob": record.get("dob", ""),
            "nationality": record.get("nationality", ""),
            "score": self.calculate_match_score(record),
            "classification": classification,
            "reasoning": reasoning
        }

    def filter_results(self) -> List[Dict[str, str]]:
        """Evaluate blacklist matches and return sorted classified results."""
        results = [self.assess_risk(record) for record in self.blacklist_data]

        results.sort(key=lambda x: (x["classification"] == "Relevant Match", x["score"]), reverse=True)
        return results

# Example usage
if __name__ == "__main__":
    tenant = {"name": "Juan Carlos Gomez", "dob": "1985-07-20", "nationality": "Mexico"}
    blacklist = [
        {"name": "Juan C. Gomez", "dob": "1985-07-20", "nationality": "Mexico"},
        {"name": "Carlos Juarez", "dob": "1979-05-14", "nationality": "Argentina"}
    ]
    
    api_helper = AIHelper()
    matcher = TenantMatcher(tenant, blacklist, api_helper)
    
    print(json.dumps(matcher.filter_results(), indent=2))
