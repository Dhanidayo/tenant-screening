from setuptools import setup, find_packages

setup(
    name="tenant_screening",
    version="0.1.0",
    packages=find_packages(where="Challenge"), 
    package_dir={"": "Challenge"}, 
    install_requires=[
        "fuzzywuzzy",
        "python-Levenshtein",
        "openai",
    ],
    entry_points={
        "console_scripts": [
            "tenant-screening=tenant_screening.main:main",
        ],
    },
    author="Sarah Adebesin",
    author_email="sarahjoseph@ymail.com",
    description="A package for screening tenants using AI and fuzzy matching.",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/Dhanidayo/tenant-screening",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.7",
)
