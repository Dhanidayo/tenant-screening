# Tenant Screening Package

## Overview
The `tenant_screening` package is a Python-based tool designed to compare tenant information against a blacklist database using AI and fuzzy matching techniques. It helps landlords and property managers assess potential risks associated with new tenants.

## System Requirements
- **Python Version**: 3.1 - 3.11 (Recommended: 3.10)
- **Operating System**: Windows, macOS, or Linux

## Installation
Follow these steps to set the project up:

1. **Clone the projecte**
   - [clone at:](https://github.com/Dhanidayo/tenant-screening.git)

2. **Installation Methods**
    - Option 1: Using setup.py (Traditional Method)
      - Create and activate a virtual environment:
        ```sh
        python -m venv .venv
        source .venv/bin/activate  # macOS/Linux
        .venv\Scripts\activate      # Windows
        ```

      - Install the package using setup.py:
        ```sh
        pip install -e .
        ```
      
      - Verify installation:
        ```sh
        python -c "import tenant_screening; print('Installation successful!')"
        ```

    - Option 2: Using pyproject.toml (PEP 518 Modern Build System).
      - Ensure pip and build are up-to-date:
        ```sh
        pip install --upgrade pip setuptools wheel build
        ```

      - Create and activate a virtual environment:
        ```sh
        python -m venv .venv
        source .venv/bin/activate  # macOS/Linux
        .venv\Scripts\activate      # Windows
        ```

      - Install the package using pyproject.toml:
        ```sh
        pip install .
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
python main.py
```

### Expected Output
The program will:
1. Read tenant data and a list of blacklisted individuals.
2. Use AI or fuzzy matching to calculate similarity scores.
3. Print a JSON-formatted result indicating whether a match is found.

Example Output:
```json
[
  {
    "name": "Juan C. Gomez",
    "score": 85,
    "classification": "Relevant Match"
  },
  {
    "name": "Carlos Juarez",
    "score": 45,
    "classification": "Probably Not Relevant"
  }
]
```

## To run tests
To test the tenant screening tool, use:
```sh
pytest tests/
```

## Troubleshooting
### Common Issues and Solutions
#### `ModuleNotFoundError: No module named 'tenant_screening'`
- Ensure you are in the correct directory.
- Run `pip install -e .` to install the package in editable mode.

#### `TypeError: TenantMatcher.__init__() got an unexpected keyword argument 'threshold'`
- Ensure `TenantMatcher` is correctly instantiated with only `tenant_data` and `blacklist_data`.
