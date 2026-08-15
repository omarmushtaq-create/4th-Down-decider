# 4th-Down Decider

A small Flask-based web app that recommends a fourth-down decision (Go For It, Punt, or Field Goal) using pre-trained models in `saved_models/`.

## Quick Start

### 1) Clone and enter the repository
```bash
git clone https://github.com/omarmushtaq-create/4th-Down-decider.git
cd 4th-Down-decider
```

### 2) Create and activate a virtual environment
```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\\Scripts\\activate
```


### 3) Install dependencies
```bash
pip install -r requirements.txt
```

### 4) Run the app
```bash
python script.py
```
Then open `http://127.0.0.1:5000` in your browser.

## Development Commands

Install development tools:
```bash
pip install -r dev-requirements.txt
```

Run checks:
```bash
ruff check .
black --check .
pytest
```

To turn off venv type 
```bash
deactivate
```

## Repository Structure

```text
.
├── script.py              # Flask app and recommendation endpoint
├── index.html             # Frontend markup
├── style.css              # Frontend styles
├── requirements.txt       # Runtime Python dependencies
├── dev-requirements.txt   # Lint/format/test tools
├── pyproject.toml         # Black, Ruff, and Pytest configuration
├── saved_models/          # Trained model artifacts used by the app
├── pbp_cache/             # Cached data artifacts
└── tree_exports/          # Exported model tree images
```

## Notes

- This repository is configured for local development with Flask's built-in server.
- Quality tooling config is non-functional and does not change app behavior.
