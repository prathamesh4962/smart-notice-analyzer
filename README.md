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
python -m streamlit run app.py
```

Open the local URL printed by Streamlit, normally `http://localhost:8501`. Keep the Streamlit terminal open while using the app. Stop it with Ctrl+C in that terminal. If PowerShell blocks activation, run `Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope Process` and activate again.

The classifier command reads `data/notices.csv` and saves `models/notice_classifier.joblib`. The spaCy English model is pinned in `requirements.txt` so local and cloud installs use the same model version.

## Project Layout

```text
app.py
requirements.txt
.gitignore
README.md
data/notices.csv
models/notice_classifier.joblib
src/
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

1. Commit and push the latest project files to the GitHub repository.
2. Sign in to Streamlit Community Cloud with GitHub and choose **Create app**.
3. Select repository `prathamesh4962/smart-notice-analyzer`, branch `main`, and main file path `app.py`.
4. In advanced settings, select Python 3.11 to match the version used to create the model.
5. Deploy and wait for the build logs to finish. Streamlit Cloud installs `requirements.txt`; the dataset and trained model are already committed in `data/` and `models/`.
6. Open the generated app URL and test the sample notice, a PDF/TXT upload, the extracted dates and entities, and report download.

No API keys or Streamlit secrets are required. If the repository is private, grant Streamlit Community Cloud access to it through GitHub.

If deployment fails, inspect the build logs first. For a missing spaCy model, confirm the pinned `en-core-web-sm` wheel is in `requirements.txt`. For a missing classifier, confirm `models/notice_classifier.joblib` is committed. Keep the pinned scikit-learn version aligned with the version used to train the saved model.

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
