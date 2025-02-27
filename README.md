# Tenant Screening Package

## Overview
The `tenant_screening` package is a Python-based tool designed to compare tenant information against a blacklist database using AI and fuzzy matching techniques. It helps landlords and property managers assess potential risks associated with new tenants.

## System Requirements
- **Python Version**: 3.1 - 3.11 (Recommended: 3.10)
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
    - Install the package
      ```sh
      python -m pip install --upgrade pip setuptools wheel
      pip install --editable .
      pip install -r requirements.txt
      ```
      
      - Verify installation:
        ```sh
        python -c "import tenant_screening; print('Installation successful!')"
        ```

## Setting Up the API Key
To use this project, you need an OpenAI API key.
If you don't provide an API key, the program will fall back to the default fuzzy matching technique

### Use a `.env` File
1. Create an `.env` file in the project root.
2. Add the following line: 
    OPENAI_API_KEY=your_actual_api_key

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
2. Use AI or fuzzy matching to calculate similarity scores.
3. Generate a JSON-formatted output file, sorting search results from the most relevant to the least relevant match.

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
    "match_score": 82,
    "confidence": "Medium",
    "classification": "relevant match"
  },
]
```

## To run tests
To test the tenant screening tool, use:
```sh
pytest Challenge/tests/
```

## Troubleshooting
### Common Issues and Solutions
#### `ModuleNotFoundError: No module named 'tenant_screening'`
- Ensure you are in the correct directory.
- Run `pip install -e .` to install the package in editable mode.

#### `FileNotFoundError: [Errno 2] No such file or directory: 'input.json'`
- Ensure you specify the correct path to the input JSON file inside the Challenge/data/ directory.
