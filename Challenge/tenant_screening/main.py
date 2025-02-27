import json
import os
import argparse
from .matcher import TenantMatcher
from .ai_helper import AIHelper

def main():
    parser = argparse.ArgumentParser(description="Tenant Screening CLI")
    parser.add_argument("input_file", help="Path to input JSON file")
    parser.add_argument("output_file", help="Path to output JSON file")
    args = parser.parse_args()

    # Read input data
    try:
        with open(args.input_file, "r", encoding="utf-8") as f:
            input_data = json.load(f)
    except FileNotFoundError:
        print(f"Input file '{args.input_file}' not found. Please provide valid data.")
        exit(1)
    except json.JSONDecodeError as e:
        print(f"Error reading JSON file: {e}")
        exit(1)

    candidate_info = input_data.get("candidate", {})
    raw_results = input_data.get("search_results", [])

    if not candidate_info or not raw_results:
        print("Candidate info or search results missing in input.json.")
        return

    classifier = TenantMatcher(
        tenant_data=candidate_info,
        blacklist_data=raw_results,
        api_helper=AIHelper(os.getenv("OPENAI_API_KEY"))
    )
    
    try:

        classified_results = classifier.classify(candidate_info, raw_results)

        try:
            classified_results.sort(key=lambda x: -x.get("match_score", 0))     
        except Exception as e:
            print(f"Sorting failed: {e}")
            
        # Save output
        with open(args.output_file, "w", encoding="utf-8") as f:
            json.dump(classified_results, f, indent=2)

        print(f"Results saved to {args.output_file}")
    
    except Exception as e:
       print(f"Classification Error: {e}")

if __name__ == "__main__":
    main()
