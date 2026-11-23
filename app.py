import streamlit as st
import pandas as pd

st.set_page_config(page_title="Genome Browser", page_icon="🧬", layout="wide")

# Dictionary: chromosome name -> chromosome length and gene records.
GENOME = {
    "Chromosome 1": {"length": 1000000, "genes": [
        {"name": "geneA", "start": 85000, "end": 145000, "strand": "+", "type": "gene"},
        {"name": "geneB", "start": 260000, "end": 335000, "strand": "-", "type": "gene"},
        {"name": "geneC", "start": 570000, "end": 645000, "strand": "+", "type": "gene"},
        {"name": "geneD", "start": 790000, "end": 875000, "strand": "-", "type": "gene"}]},
    "Chromosome 2": {"length": 900000, "genes": [
        {"name": "geneE", "start": 70000, "end": 160000, "strand": "+", "type": "gene"},
        {"name": "geneF", "start": 310000, "end": 390000, "strand": "-", "type": "gene"},
        {"name": "geneG", "start": 620000, "end": 710000, "strand": "+", "type": "gene"}]},
    "Chromosome X": {"length": 800000, "genes": [
        {"name": "geneX1", "start": 90000, "end": 185000, "strand": "-", "type": "gene"},
        {"name": "geneX2", "start": 360000, "end": 455000, "strand": "+", "type": "gene"},
        {"name": "geneX3", "start": 620000, "end": 735000, "strand": "-", "type": "gene"}]},
}

def parse_fasta(file_text):
    """Read FASTA records into a dictionary: sequence ID -> sequence."""
    sequences = {}
    current_id = None
    sequence_parts = []
    for line in file_text.splitlines():
        line = line.strip()
        if not line:
            continue
        if line.startswith(">"):
            if current_id is not None:
                sequences[current_id] = "".join(sequence_parts).upper()
            current_id = line[1:].split()[0]
            sequence_parts = []
        elif current_id is not None:
            sequence_parts.append(line)
    if current_id is not None:
        sequences[current_id] = "".join(sequence_parts).upper()
    return sequences

def sequence_statistics(sequences):
    """Calculate sequence count, total length and GC percentage."""
    combined = "".join(sequences.values())
    valid = [base for base in combined if base in "ACGTU"]
    gc = combined.count("G") + combined.count("C")
    gc_percent = round(gc / len(valid) * 100, 2) if valid else None
    return len(sequences), len(combined), gc_percent

def parse_annotation(file_text, file_type):
    """Read basic gene features from a BED or GFF3 annotation file."""
    features = []
    for line in file_text.splitlines():
        if not line.strip() or line.startswith("#"):
            continue
        fields = line.rstrip().split("\t")
        try:
            if file_type == "BED" and len(fields) >= 3:
                chrom = fields[0].lower().removeprefix("chr")
                start, end = int(fields[1]) + 1, int(fields[2])
                name = fields[3] if len(fields) > 3 else "feature"
                strand = fields[5] if len(fields) > 5 else "+"
            elif file_type == "GFF3" and len(fields) >= 9:
                if fields[2] not in ("gene", "mRNA", "ncRNA_gene"):
                    continue
                chrom = fields[0].lower().removeprefix("chr")
                start, end, strand = int(fields[3]), int(fields[4]), fields[6]
                attrs = dict(item.split("=", 1) for item in fields[8].split(";") if "=" in item)
                name = attrs.get("Name", attrs.get("ID", "feature"))
            else:
                continue
            features.append({"chromosome": chrom, "name": name, "start": start, "end": end, "strand": strand, "type": file_type})
        except (ValueError, IndexError):
            continue
    return features

st.title("🧬 Simple Genome Browser")
st.caption("A beginner-friendly genome browser built with Python.")
with st.sidebar:
    st.header("Genome selection")
    chromosome = st.selectbox("Choose chromosome", list(GENOME.keys()))
    st.markdown("---")
    st.write("1. Select a chromosome.")
    st.write("2. Search for a gene.")
    st.write("3. Upload FASTA, BED or GFF3 files.")

chromosome_data = GENOME[chromosome]
features = list(chromosome_data["genes"])
a, b = st.columns(2)
a.metric("Chromosome length", f'{chromosome_data["length"]:,} bp')
b.metric("Sample gene records", len(features))
st.info("Built-in chromosome labels and coordinates are fictional teaching examples, not real reference-genome data.")

search = st.text_input("Search gene name", placeholder="For example: geneA")
if search:
    features = [gene for gene in features if search.lower() in gene["name"].lower()]
    if not features:
        st.warning("No matching gene found.")

st.subheader("Gene features")
if features:
    table = pd.DataFrame(features)
    st.dataframe(table, use_container_width=True, hide_index=True)
    st.subheader("Gene coordinate overview")
    chart = table.set_index("name")[["start", "end"]]
    st.bar_chart(chart, use_container_width=True)
else:
    st.write("No features to display.")

st.divider()
st.subheader("Upload your annotation file")
ann_file = st.file_uploader("Choose BED or GFF3", type=["bed", "gff", "gff3"])
if ann_file:
    kind = "BED" if ann_file.name.lower().endswith(".bed") else "GFF3"
    uploaded = parse_annotation(ann_file.getvalue().decode("utf-8", errors="replace"), kind)
    chrom_key = chromosome.lower().replace("chromosome ", "")
    matching = [item for item in uploaded if item["chromosome"] == chrom_key]
    st.write(f"Found {len(matching)} feature(s) for {chromosome}.")
    if matching:
        st.dataframe(pd.DataFrame(matching), use_container_width=True, hide_index=True)
    else:
        st.warning("No matching chromosome records. Check chromosome names in your file.")

st.divider()
st.subheader("FASTA sequence analyser")
fasta_file = st.file_uploader("Choose FASTA", type=["fa", "fasta", "fna", "faa"])
if fasta_file:
    sequence_dictionary = parse_fasta(fasta_file.getvalue().decode("utf-8", errors="replace"))
    if sequence_dictionary:
        count, total, gc = sequence_statistics(sequence_dictionary)
        c1, c2, c3 = st.columns(3)
        c1.metric("Sequences", count)
        c2.metric("Total length", f"{total:,} bases / residues")
        c3.metric("GC content", f"{gc}%" if gc is not None else "N/A")
        preview = [{"Sequence ID": key, "Length": len(value), "First 80 characters": value[:80]} for key, value in sequence_dictionary.items()]
        st.dataframe(pd.DataFrame(preview), use_container_width=True, hide_index=True)
    else:
        st.error("No FASTA records found. Each sequence must begin with a > header.")

with st.expander("Understand the Python code (viva help)"):
    st.markdown("""
    - **GENOME** is a dictionary containing chromosome names, lengths and gene records.
    - **Variables** such as chromosome, features and sequence_dictionary store values.
    - **parse_fasta()** reads FASTA headers and joins sequence lines.
    - **sequence_statistics()** calculates sequence count, total length and GC percentage.
    - **parse_annotation()** reads basic BED and GFF3 gene coordinates.
    - **Streamlit** creates the web interface directly from Python.
    """)
st.caption("Educational project • Python + Streamlit • Use verified reference data for real biological analysis.")