from setuptools import setup, find_packages

setup(
    name="tenant_screening",
    version="1.0.0",
    packages=find_packages(),
    install_requires=[
        "fuzzywuzzy",
        "python-Levenshtein",
        "openai"
    ],
    extras_require={
        "dev": ["pytest", "python-dotenv", "black", "flake8"]
    },
)
