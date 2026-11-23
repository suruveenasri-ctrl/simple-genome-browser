# Simple Genome Browser (Python)

A beginner-friendly genome browser built with Python and Streamlit. The application interface and logic are written in Python.

## Features
- Select a sample chromosome and view gene coordinates and strand.
- Search for a gene by name.
- Upload BED or GFF3 annotation files.
- Upload FASTA files and calculate sequence count, total length and GC percentage.
- View explanations of the Python dictionary, variables and functions for viva preparation.

## Run locally
1. Install Python 3.
2. Download or clone this repository.
3. Run: python -m pip install -r requirements.txt
4. Run: python -m streamlit run app.py
5. Open the local URL shown in the terminal (usually http://localhost:8501).

## Deploy from GitHub
GitHub stores the Python code, but GitHub Pages cannot run Python applications. To publish this app, connect the repository to Streamlit Community Cloud and set the main file path to app.py.

## Project team
- S. Veena Sri — SE25UMBT011
- Vanshika — SE25UBIT066

## Data note
The built-in chromosome names and coordinates are fictional teaching examples. Upload trusted annotations and use a matching reference assembly for real biological analysis. This is a basic educational viewer, not a production-grade genome browser.