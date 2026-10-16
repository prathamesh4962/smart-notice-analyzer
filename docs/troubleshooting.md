# Troubleshooting

Run project commands from `D:\NLP MICROPROJECT\smart-notice-analyzer`. In PowerShell, the prompt should start with `(.venv)` when the project environment is active.

## Python and virtual environment

- **`py -3.11` is not recognized or Python 3.11 is unavailable:** Run `py -0p` to list installed versions. Install Python 3.11 if it is missing, then recreate the environment with `py -3.11 -m venv .venv` from the project root.
- **PowerShell blocks `Activate.ps1`:** Run `Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope Process`, then `.\.venv\Scripts\Activate.ps1`.
- **The prompt does not show `(.venv)`:** Activate with `.\.venv\Scripts\Activate.ps1`. Verify with `python --version` and `python -m pip --version`; the pip path should contain the project's `.venv` directory.
- **`cpython` or `code` is not recognized:** Use `python` or `py` for Python commands. The `code` command is optional; it is not required to use VS Code.
- **Pylance reports packages missing even though terminal commands work:** In VS Code, run `Python: Select Interpreter` and choose `.venv\Scripts\python.exe` inside the project.

## Package installation

- **`No module named streamlit` or another dependency:** From the project root with `(.venv)` active, run `python -m pip install -r requirements.txt`.
- **Installation is still showing `Installing collected packages`:** Leave the terminal open until the PowerShell prompt returns. A pip update notice is optional and is not an installation failure.
- **`python -m pip check` says `unknown command "checkpython"`:** Multiple commands were pasted together. At a fresh prompt, enter only `python -m pip check` once. A healthy environment prints `No broken requirements found.`
- **`swigvarlink` DeprecationWarning appears:** This warning can come from PyMuPDF's native bindings. If the test command ends with `OK` and returns to the prompt, the warning did not fail the tests.

## Project files and models

- **`FileNotFoundError` for the dataset or classifier:** Confirm `Get-Location` shows the project root. Train the model there with `python -m src.classifier`; it reads `data\notices.csv` and writes `models\notice_classifier.joblib`.
- **The spaCy model is missing:** From the active project environment, run `python -m spacy download en_core_web_sm` once. Do not edit files inside `.venv\Lib\site-packages`.
- **PDF is invalid, unreadable, or scanned:** Try a valid PDF with selectable text or upload a TXT file. Scanned PDFs need OCR, which this project does not currently include.
- **A file type is unsupported:** The uploader accepts PDF and TXT only.

## Streamlit and application behavior

- **Streamlit is not found:** Activate `.venv`, move to the project root, and run `python -m streamlit run app.py`.
- **Streamlit reports it cannot connect to the analysis API:** Start the backend in a separate terminal with `python -m uvicorn backend.main:app --reload --port 8000`. If it is deployed elsewhere, set `NOTICE_API_URL` to its base URL in the Streamlit environment or Secrets.
- **The API server is not found:** Install dependencies with `python -m pip install -r requirements.txt`, then start it from the project root with `python -m uvicorn backend.main:app --reload --port 8000`.
- **The API health check fails:** Open `http://127.0.0.1:8000/health` while the backend is running. API docs are at `http://127.0.0.1:8000/docs`.
- **Port 8501 is already in use:** Start the app on another port with `python -m streamlit run app.py --server.port 8502`.
- **The `code` command or a pasted path causes a PowerShell parser error:** These commands do not need `code` or `&`. Enter only the command shown, without copying terminal output or an extra file path.
- **A category prediction is wrong or has a low estimated probability:** This is expected with the small synthetic dataset. The measured 20% holdout accuracy is not reliable real-world performance. Add more diverse, correctly labeled notices before drawing conclusions; do not report an inflated accuracy.
- **Tests fail:** From the project root with `(.venv)` active, run `python -m unittest discover -s tests -p "test_*.py"`. Read the first traceback above `FAILED` and fix that specific cause; warnings alone are not necessarily failures.
