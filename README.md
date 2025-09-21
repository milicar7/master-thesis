# CSV to DDL Converter

A tool that analyzes CSV files and generates database schema in form of a SQL/DDL file with automatic detection of column types, primary keys, foreign keys, and normalization violations.

## Features

- **Type Inference**: Automatic detection of data types including dates, emails, URLs, UUIDs
- **Primary Key Detection**: Identifies single, composite, and surrogate keys
- **Foreign Key Analysis**: Detects relationships between tables
- **Normalization Analysis**: Identifies 1NF, 2NF, and 3NF violations
- **Multi-Database Support**: PostgreSQL, MySQL, SQL Server, SQLite

## Requirements

Python 3.13+

## Setup

```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -r requirements.txt
pip install -e .
```

## Usage

### Basic Usage

```bash
# Convert single CSV file (PostgreSQL by default)
python -m csv_to_ddl.main -i data.csv

# Convert all CSV files in a directory
python -m csv_to_ddl.main -i data/

# Specify database dialect
python -m csv_to_ddl.main -i data.csv -d mysql

# Save output to file
python -m csv_to_ddl.main -i data/ -o schema.sql

# Enable verbose logging
python -m csv_to_ddl.main -i data.csv -v
```

### Supported Database Dialects

- `postgresql` (default)
- `mysql`
- `sqlserver`
- `sqlite`

## Test Datasets

The project includes real-world datasets for evaluation

### Running Tests

```bash
cd testing/schema && unzip datasets.zip && cd ../..
python -m pytest testing/
```

## Output Example

Input CSV files are analyzed to produce:
- CREATE TABLE statements with appropriate data types
- PRIMARY KEY constraints (single, composite, or auto-generated)
- FOREIGN KEY relationships between tables
- Comments indicating normalization form violations