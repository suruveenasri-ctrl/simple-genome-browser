# Genome Explorer

Genome Explorer is an educational genome-browser web application for exploring chromosome regions, viewing gene-feature coordinates and practising basic bioinformatics file handling.

## Project team
- S. Veena Sri — SE25UMBT011
- Vanshika — SE25UBIT066

## Technology
- Python 3
- Flask
- HTML templates with Jinja
- CSS

## Features
- Interactive chromosome selector for the included teaching dataset
- Linear visualization of feature positions and strand direction
- Case-insensitive search for a displayed gene or feature
- FASTA parser with sequence count, total length, GC percentage and ambiguous-symbol summary
- Basic GFF3 and BED annotation parser for the selected chromosome
- In-app explanation of the Python dictionary, variables and reusable functions

## Project structure
- app.py — application logic, data dictionary, Flask route and parsing/statistics functions
- requirements.txt — Python dependencies
- templates/index.html — application interface
- templates/error.html — upload error page
- static/style.css — interface styling
- Procfile — production server start command

## Run locally
1. Install Python 3.
2. Open a terminal in the project folder.
3. Install dependencies: python -m pip install -r requirements.txt
4. Start the application: python app.py
5. Open http://127.0.0.1:5000 in your browser.

If your system uses python3, replace python with python3.

## Upload guidance
- FASTA: .fa, .fasta, .fna or .faa
- Annotation: .bed, .gff or .gff3
- Maximum upload size: 5 MB
- BED start coordinates are converted from zero-based to one-based for display.
- GFF3 coordinates are already one-based.

## Important data limitation
The built-in chromosome labels, gene names and coordinates are illustrative teaching records. They are not verified reference-genome annotations and must not be used for biological interpretation. For real analysis, use a consistent reference assembly and a trusted annotation file. The current parser supports a basic subset of BED/GFF3 and is intended for learning, not full standards compliance.

## Deployment
This application requires a Python-capable web host. GitHub Pages cannot run a Flask server. A live public deployment has not been configured by this repository.
