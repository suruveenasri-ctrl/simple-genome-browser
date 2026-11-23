# Simple Genome Browser — Python / Flask

An educational genome browser built with a Python Flask backend.

## Project members
- S. Veena Sri — SE25UMBT011
- Vanshika — SE25UBIT066

## Technologies
- Python 3 and Flask
- HTML templates (Jinja)
- CSS

## Features
- Select chromosome 1, 2 or X
- View chromosome length and gene positions
- Search gene names and display coordinates/strand
- Upload basic GFF3 or BED annotation files
- Includes a Python FASTA parsing function

## Files
- app.py — Python data dictionary, Flask route, search, and parsing functions
- requirements.txt — Python dependency list
- templates/index.html — page template displayed by Flask
- static/style.css — page styling

## Run locally
1. Install Python 3.
2. Open a terminal in this folder.
3. Run: python -m pip install -r requirements.txt
4. Run: python app.py
5. Open http://127.0.0.1:5000 in a browser.

On some computers, use python3 instead of python.

## Hosting note
GitHub Pages only serves static files and cannot run a Python Flask server. This repository is now a Flask application. To publish a working live website, deploy it on a Python-compatible hosting service and configure it to install requirements.txt and start app.py.

## Biological data note
The built-in gene names and coordinates are illustrative teaching data, not validated reference genome annotations. They must not be used for biological analysis. Real analysis requires a consistent reference assembly and verified annotation source.
