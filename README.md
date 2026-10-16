# Smart Notice Analyzer

A beginner-friendly Streamlit micro-project that analyzes college notices using lightweight NLP and traditional machine learning.

## Features

- Paste notice text or upload a PDF/TXT file.
- Predict one of eight notice categories: Examination, Scholarship, Placement, Events, Fees, Academic, Holiday, or General.
- Extract explicit dates, named entities, and action-related sentences.
- Create an extractive TextRank summary and a downloadable Markdown report.
- Keep a small analysis history for the current app session.

Scanned PDFs are not supported because this project does not include OCR. Numeric dates that could mean either day/month or month/day are marked ambiguous instead of guessed.

## Limitations

The classifier is trained on 40 synthetic notices (five per category). In the current 30/10 train/holdout split, observed holdout accuracy was 0.20. This is a weak result from a tiny synthetic sample, not evidence of real-world performance. Treat category predictions and their estimated probabilities as unreliable until the dataset is expanded with diverse, correctly labeled real notices and evaluated again.

## Requirements

- Windows, Python 3.11, and VS Code
- Git for version control
- Internet access to install packages

## Setup and Run (PowerShell)

Open PowerShell in the project root (the folder containing `app.py`).

```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python -m src.classifier
python -m unittest discover -s tests -p "test_*.py"
python -m uvicorn backend.main:app --reload --port 8000
```

In a second PowerShell terminal, start the Streamlit interface:

```powershell
.\.venv\Scripts\Activate.ps1
python -m streamlit run app.py
```

The API is available at `http://127.0.0.1:8000`. Check `http://127.0.0.1:8000/docs` for interactive API documentation and `http://127.0.0.1:8000/health` for its health check. The Streamlit UI calls `POST /api/analyze` on that API. Locally, it defaults to `http://127.0.0.1:8000`; set `NOTICE_API_URL` to change the backend address. Keep both terminals running. Stop each process with Ctrl+C in its terminal. If PowerShell blocks activation, run `Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope Process` and activate again.

The classifier command reads `data/notices.csv` and saves `models/notice_classifier.joblib`. The spaCy English model is pinned in `requirements.txt` so local and cloud installs use the same model version.

## Project Layout

```text
app.py
backend/
  main.py
requirements.txt
.gitignore
README.md
data/notices.csv
models/notice_classifier.joblib
src/
  analysis_service.py
  api_client.py
  action_extractor.py
  classifier.py
  date_extractor.py
  entity_extractor.py
  pdf_extractor.py
  preprocessing.py
  report_generator.py
  summarizer.py
tests/
  test_extractors.py
  test_preprocessing.py
docs/
  troubleshooting.md
```

## Tests

Run `python -m unittest discover -s tests -p "test_*.py"` from the project root with `.venv` active. The current suite has 18 tests covering preprocessing, PDF/TXT extraction, dates, ambiguous dates, action extraction, summaries, entities, and reports.

## Deploy to Streamlit Community Cloud

The Streamlit UI and FastAPI service are separate processes. Deploy the API first to a Python hosting service that supports long-running ASGI apps. Configure its start command as:

```text
uvicorn backend.main:app --host 0.0.0.0 --port $PORT
```

Ensure the API deployment includes this repository's `data/` and `models/` directories and installs `requirements.txt`. Confirm its `/health` endpoint responds before connecting the UI.

Then deploy the Streamlit frontend:

1. Commit and push the latest project files to GitHub.
2. In Streamlit Community Cloud choose **Create app**.
3. Select repository `prathamesh4962/smart-notice-analyzer`, branch `main`, and main file path `app.py`.
4. In advanced settings, select Python 3.11.
5. In the app's **Secrets** settings, configure `NOTICE_API_URL` to the public base URL of the deployed API, for example `NOTICE_API_URL = "https://your-api.example.com"` (no `/api/analyze` suffix).
6. Deploy and test notice analysis, PDF/TXT upload, extracted dates and entities, and report download.

The API base URL is not a secret, but Streamlit Secrets provides a straightforward setting for the frontend. If the repository is private, grant Streamlit Community Cloud access to it through GitHub.

If deployment fails, inspect the build logs first. For API connection errors, verify `NOTICE_API_URL` and that the API service is running and publicly reachable. For a missing spaCy model, confirm the pinned `en-core-web-sm` wheel is in `requirements.txt`. For a missing classifier, confirm `models/notice_classifier.joblib` is committed. Keep the pinned scikit-learn version aligned with the version used to train the saved model.

## GitHub

Initialize and review the repository from the project root:

```powershell
git init
git status --short
git add .gitignore README.md requirements.txt app.py data docs models src tests
git status --short
git commit -m "Build smart notice analyzer"
```

Create an empty repository on GitHub named `smart-notice-analyzer` (do not initialize it with a README). Then connect and push:

```powershell
git branch -M main
git remote add origin https://github.com/prathamesh4962/smart-notice-analyzer.git
git push -u origin main
```

Authenticate through Git Credential Manager or the browser prompt; never put a password, token, or secret in project files or chat. The `.gitignore` excludes the virtual environment and common local secrets, while keeping the dataset and trained model available for deployment.

See [docs/troubleshooting.md](docs/troubleshooting.md) for common setup and runtime fixes.
