# Tenant Screening Package

## Overview
The `tenant_screening` package is a Python-based tool designed to compare tenant information against a blacklist database using AI and fuzzy matching techniques. It helps landlords and property managers assess potential risks associated with new tenants.

## How It Works
1. **Rules first.** Names are normalised (accents and particles such as "de la" removed) and compared with fuzzy matching. Matching birthdate, nationality and age add to the score. Each record gets a score (0–100), a confidence level and a classification.
2. **AI only for ambiguous cases.** Records scoring 60–80 are too close to call with rules alone, so they are sent to an OpenAI chat model. The model must answer with structured output: exactly `relevant match` or `probably not relevant`, plus a one-sentence reason.
3. **Safe fallback.** With no API key, an API error, a refusal or an unexpected answer, the rule-based classification stands. Every record records which step classified it (`classified_by`), so a reviewer can see where the AI was involved.

## System Requirements
- **Python Version**: 3.8 or later (tested on 3.13)
- **Operating System**: Windows, macOS, or Linux

## Installation
Follow these steps to set the project up:

1. **Clone the project**
   - (https://github.com/Dhanidayo/tenant-screening.git)

2. **Create and Activate a Virtual Environment**
   ```sh
    python -m venv .venv
    source .venv/bin/activate  # macOS/Linux
    # OR
    .venv\Scripts\activate  # Windows
   ```

3. **Installation Methods**
    - At the root of the project, install the dependencies and the package
      ```sh
      python -m pip install --upgrade pip setuptools wheel
      pip install -r requirements.txt
      pip install --editable .
      ```

      - Verify installation:
        ```sh
        python -c "import tenant_screening; print('Installation successful!')"
        ```

      If installation fails, see the troubleshooting section.

## Setting Up the API Key (optional)
The AI review step needs an OpenAI API key.
Without one, the program runs on fuzzy matching alone and every record keeps its rule-based classification.

### Use a `.env` File
1. Create an `.env` file in the project root.
2. Add the following line:
    OPENAI_API_KEY=your_actual_api_key
3. Optionally choose the model (default `gpt-4o-mini`; it must support structured outputs):
    OPENAI_MODEL=gpt-4o-mini

## Running the Project
To run the tenant screening tool, use:
```sh
tenant-screening Challenge/data/input.json Challenge/data/output.json
  OR
python Challenge/tenant_screening/main.py Challenge/data/input.json Challenge/data/output.json
```

### Expected Output
The program will:
1. Read tenant data from input.json and a list of blacklisted individuals.
2. Score every record with fuzzy matching, then send ambiguous scores to the AI review step (when an API key is set).
3. Generate a JSON-formatted output file, sorting search results from the most relevant to the least relevant match.

`classified_by` is `rules` or `ai`. When the AI classified a record, `ai_reason` explains why.

Example Output:
```json
[
  {
    "first_name": "Rodriguez",
    "last_name": "Juan Carlos",
    "birthdate": "1985-06-15",
    "nationality": "Mexican",
    "age": 38,
    "pipeline": {
      "type": "refinitiv-blacklist"
    },
    "match_score": 76,
    "confidence": "Medium",
    "classification": "relevant match",
    "classified_by": "ai",
    "ai_reason": "Same name with first and last names swapped, and identical birthdate, nationality and age."
  },
]
```

## To run tests
Install the package first (see Installation), then run:
```sh
pytest Challenge/tests/
```

The tests cover name normalisation, scoring, and the AI step's fallbacks: no API key, API errors, refusals, invalid or unexpected answers, and sending only ambiguous scores to the model. The OpenAI client is mocked, so no key or network access is needed.

## Troubleshooting
### Common Issues and Solutions
#### `ModuleNotFoundError: No module named 'tenant_screening'`
- Ensure you are in the correct directory.
- Run `pip install -e .` to install the package in editable mode.

#### `FileNotFoundError: [Errno 2] No such file or directory: 'input.json'`
- Ensure you specify the correct path to the input JSON file inside the Challenge/data/ directory.
