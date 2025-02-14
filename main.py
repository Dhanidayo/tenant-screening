import os
import json
from tenant_screening.matcher import TenantMatcher
from tenant_screening.ai_helper import AIHelper

tenant_data = {
    "name": "Juan Carlos Gomez",
    "dob": "1985-07-20",
    "nationality": "Mexico"
}

blacklist_data = [
    {"name": "Juan C. Gomez", "dob": "1985-07-20", "nationality": "Mexico", "pipeline": {"type": "refinitiv-blacklist"}},
    {"name": "Carlos Juarez", "dob": "1979-05-14", "nationality": "Argentina", "pipeline": {"type": "refinitiv-blacklist"}}
]

api_key = os.getenv("OPENAI_API_KEY") or input("Enter your OpenAI API key: ")
api_helper = AIHelper(api_key)

matcher = TenantMatcher(tenant_data, blacklist_data, api_helper, threshold=80)

results = matcher.filter_results()

print(json.dumps(results, indent=2))
