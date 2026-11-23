from flask import Flask, render_template, request
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 5 * 1024 * 1024

# Dictionary: chromosome ID -> chromosome length and illustrative feature records.
# Built-in records are teaching examples, not verified reference-genome data.
GENOME_DATA = {
    "1": {"length": 1_000_000, "genes": [
        {"name":"GENE_A","start":85000,"end":145000,"strand":"+","feature_type":"gene","function":"Illustrative protein-coding feature"},
        {"name":"GENE_B","start":260000,"end":335000,"strand":"-","feature_type":"gene","function":"Illustrative regulatory feature"},
        {"name":"GENE_C","start":570000,"end":645000,"strand":"+","feature_type":"gene","function":"Illustrative metabolic feature"},
        {"name":"GENE_D","start":790000,"end":875000,"strand":"-","feature_type":"gene","function":"Illustrative signalling feature"}]},
    "2": {"length": 900_000, "genes": [
        {"name":"GENE_E","start":70000,"end":160000,"strand":"+","feature_type":"gene","function":"Illustrative cellular feature"},
        {"name":"GENE_F","start":310000,"end":390000,"strand":"-","feature_type":"gene","function":"Illustrative enzyme feature"},
        {"name":"GENE_G","start":620000,"end":710000,"strand":"+","feature_type":"gene","function":"Illustrative transport feature"}]},
    "X": {"length": 800_000, "genes": [
        {"name":"GENE_X1","start":90000,"end":185000,"strand":"-","feature_type":"gene","function":"Illustrative X-chromosome feature"},
        {"name":"GENE_X2","start":360000,"end":455000,"strand":"+","feature_type":"gene","function":"Illustrative regulatory feature"},
        {"name":"GENE_X3","start":620000,"end":735000,"strand":"-","feature_type":"gene","function":"Illustrative structural feature"}]}
}


def normalize_chromosome(chromosome):
    """Make chromosome labels such as chr1 and 1 comparable."""
    return chromosome.strip().lower().removeprefix("chr").upper()


def parse_fasta(text):
    """Return a dictionary containing FASTA sequence IDs and sequence strings."""
    sequences, current_name, parts = {}, None, []
    for line in text.splitlines():
        line = line.strip()
        if not line:
            continue
        if line.startswith(">"):
            if current_name:
                sequences[current_name] = "".join(parts).upper()
            current_name, parts = line[1:].split()[0], []
        elif current_name:
            parts.append(line)
    if current_name:
        sequences[current_name] = "".join(parts).upper()
    return sequences


def calculate_sequence_stats(sequences):
    """Calculate sequence count, total length, GC percentage and ambiguous symbols."""
    combined = "".join(sequences.values()).upper()
    valid_bases = sum(combined.count(base) for base in "ACGT")
    gc_count = combined.count("G") + combined.count("C")
    return {
        "sequence_count": len(sequences),
        "total_bases": len(combined),
        "gc_percent": round(gc_count / valid_bases * 100, 2) if valid_bases else 0,
        "ambiguous_bases": sum(base not in "ACGT" for base in combined)
    }


def parse_annotation(text, file_type):
    """Parse basic gene records from BED or GFF3 annotation text."""
    features = []
    for line in text.splitlines():
        if not line.strip() or line.startswith("#") or line.startswith("track") or line.startswith("browser"):
            continue
        columns = line.rstrip().split("\t")
        try:
            if file_type == "bed" and len(columns) >= 3:
                chromosome = normalize_chromosome(columns[0])
                start, end = int(columns[1]) + 1, int(columns[2])
                name = columns[3] if len(columns) > 3 and columns[3] else "BED_feature"
                strand = columns[5] if len(columns) > 5 and columns[5] in ("+", "-") else "+"
                feature_type = "BED feature"
            elif file_type == "gff3" and len(columns) >= 9:
                feature_type = columns[2]
                if feature_type not in ("gene", "mRNA", "ncRNA_gene", "pseudogene"):
                    continue
                chromosome = normalize_chromosome(columns[0])
                start, end = int(columns[3]), int(columns[4])
                strand = columns[6] if columns[6] in ("+", "-") else "+"
                attributes = {}
                for item in columns[8].split(";"):
                    if "=" in item:
                        key, value = item.split("=", 1)
                        attributes[key] = value
                name = attributes.get("Name", attributes.get("gene", attributes.get("ID", feature_type)))
            else:
                continue
            if start >= 1 and end >= start:
                features.append({"chromosome":chromosome,"name":name,"start":start,"end":end,
                    "strand":strand,"feature_type":feature_type,"function":"Loaded from uploaded annotation file"})
        except (ValueError, IndexError):
            continue
    return features


def prepare_genes(genes, chromosome_length):
    """Convert genomic coordinates to percentages for the visual chromosome track."""
    prepared = []
    for gene in genes:
        start = max(1, min(int(gene["start"]), chromosome_length))
        end = max(start, min(int(gene["end"]), chromosome_length))
        item = dict(gene)
        item.update({"start":start,"end":end,"left":start/chromosome_length*100,
                     "width":max((end-start)/chromosome_length*100, 1.2)})
        prepared.append(item)
    return sorted(prepared, key=lambda item: item["start"])


@app.route("/", methods=["GET", "POST"])
def home():
    selected_chromosome = request.values.get("chromosome", "1")
    if selected_chromosome not in GENOME_DATA:
        selected_chromosome = "1"
    chromosome_data = GENOME_DATA[selected_chromosome]
    genes = list(chromosome_data["genes"])
    search_text = request.values.get("gene_search", "").strip()
    message, message_type = "", "info"
    sequence_stats, sequence_preview, uploaded_filename = None, [], ""

    if request.method == "POST":
        fasta_file = request.files.get("fasta_file")
        if fasta_file and fasta_file.filename:
            filename = secure_filename(fasta_file.filename)
            if not filename.lower().endswith((".fa", ".fasta", ".fna", ".faa")):
                message, message_type = "Upload a FASTA file (.fa, .fasta, .fna or .faa).", "error"
            else:
                sequences = parse_fasta(fasta_file.read().decode("utf-8", errors="replace"))
                if sequences:
                    sequence_stats = calculate_sequence_stats(sequences)
                    sequence_preview = [{"name":name,"sequence":seq[:100]} for name,seq in list(sequences.items())[:5]]
                    uploaded_filename = filename
                    message, message_type = f"Read {len(sequences)} sequence record(s) from {filename}.", "success"
                else:
                    message, message_type = "No FASTA records found. Each record must begin with a > header.", "error"

        annotation_file = request.files.get("annotation_file")
        if annotation_file and annotation_file.filename:
            filename = secure_filename(annotation_file.filename)
            lower_name = filename.lower()
            file_type = "bed" if lower_name.endswith(".bed") else ("gff3" if lower_name.endswith((".gff", ".gff3")) else "")
            if not file_type:
                message, message_type = "Upload a BED, GFF or GFF3 annotation file.", "error"
            else:
                features = parse_annotation(annotation_file.read().decode("utf-8", errors="replace"), file_type)
                genes = [item for item in features if item["chromosome"] == normalize_chromosome(selected_chromosome)]
                if genes:
                    message, message_type = f"Loaded {len(genes)} feature(s) from {filename} for chromosome {selected_chromosome}.", "success"
                else:
                    message, message_type = f"No features for chromosome {selected_chromosome} were found in {filename}.", "error"

    displayed_genes = prepare_genes(genes, chromosome_data["length"])
    selected_gene = next((item for item in displayed_genes if item["name"].lower() == search_text.lower()), None) if search_text else None
    if search_text and selected_gene is None:
        message, message_type = f'Feature "{search_text}" was not found in the displayed records.', "error"

    return render_template("index.html", chromosomes=GENOME_DATA, selected_chromosome=selected_chromosome,
        chromosome_data=chromosome_data, genes=displayed_genes, selected_gene=selected_gene,
        search_text=search_text, message=message, message_type=message_type,
        sequence_stats=sequence_stats, sequence_preview=sequence_preview, uploaded_filename=uploaded_filename)


@app.errorhandler(413)
def file_too_large(_error):
    return render_template("error.html", message="The selected file is larger than the 5 MB upload limit."), 413


if __name__ == "__main__":
    app.run(debug=True)
