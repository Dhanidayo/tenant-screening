import sys
import os

sys.path.append(os.path.abspath("Challenge"))

import json
from tenant_screening.matcher import TenantMatcher
from tenant_screening.ai_helper import AIHelper

def main():
    """Main function to execute the tenant screening classification."""
    data_dir = "data"
    input_file = os.path.join(data_dir, "input.json")
    output_file = os.path.join(data_dir, "output.json")

    # Load input data
    with open(input_file, "r", encoding="utf-8") as f:
        input_data = json.load(f)

    candidate_info = input_data["candidate"]
    raw_results = input_data["search_results"]

    # Initialize classifier
    classifier = TenantMatcher(
        tenant_data=candidate_info,
        blacklist_data=raw_results,
        api_helper=AIHelper(os.getenv("OPENAI_API_KEY"))
    )

    # Process classification
    classified_results = classifier.classify(candidate_info, raw_results)

    # Save results to output file
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(classified_results, f, indent=2)

    print(f"Classification results saved to {output_file}")

if __name__ == "__main__":
    main()
