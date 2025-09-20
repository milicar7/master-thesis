# CSV to DDL Converter

Requires Python 3.13+

## Setup

```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -r requirements.txt
pip install -e .
```

## Running Tests

```bash
cd testing/schema && unzip datasets.zip && cd ../..
python -m pytest testing/
```