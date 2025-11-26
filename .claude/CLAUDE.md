# Company Researcher
This project is aimed at 

- `README.md` describes project setup and running the project
- `PROJECT_FLOW.md` describes the flow of the project when running

## Project Setup
- **Python 3.9+** with `venv/` virtual environment
- **Structure**: `src/` (code) + `tests/` (pytest)
- **Tools**: ruff (lint/format), pytest, mypy

⚠️ **CRITICAL**: Always activate venv before running commands: `source venv/bin/activate`

## Coding Standards
- PEP 8, 88 char lines (ruff enforced)
- Type hints on functions, docstrings on public APIs
- Tests in `tests/test_*.py`, use pytest fixtures
- Small focused functions, explicit error handling

## Commands

```bash
# Setup
python3 -m venv venv && source venv/bin/activate
pip install -r requirements.txt

# Before any command, activate venv!
source venv/bin/activate
```

