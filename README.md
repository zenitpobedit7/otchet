# Marketplace Analytics (Streamlit)

Modern Python Streamlit app to analyze marketplace reports (Ozon, Wildberries).

## Quick start

1. Create virtualenv and install dependencies:

```bash
python -m venv .venv
source .venv/bin/activate  # linux/mac
.venv\Scripts\activate     # windows
pip install -r requirements.txt
```

2. Run:

```bash
streamlit run app.py
```

Open http://localhost:8501 in your browser.

## Build .exe (Windows) with GitHub Actions / PyInstaller

A sample GitHub Actions workflow is included in `.github/workflows/ci-windows-build.yml` to build an .exe artifact on push to main. See the file for details.

Note: bundling Streamlit into a single exe is non-trivial because Streamlit spawns server processes. Recommended approach: deploy to a small cloud VM or package a lightweight browser wrapper.
