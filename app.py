from flask import Flask, render_template, request
from werkzeug.utils import secure_filename

app = Flask(__name__)

# Dictionary: chromosome name -> chromosome information.
# Built-in records are illustrative demo data, not real reference annotations.
GENOME_DATA = {
    "1": {"length": 1000000, "genes": [
        {"name":"GENE_A","start":85000,"end":145000,"strand":"+","function":"Example protein-coding feature"},
        {"name":"GENE_B","start":260000,"end":335000,"strand":"-","function":"Example regulatory feature"},
        {"name":"GENE_C","start":570000,"end":645000,"strand":"+","function":"Example metabolic feature"},
        {"name":"GENE_D","start":790000,"end":875000,"strand":"-","function":"Example signaling feature"}]},
    "2": {"length": 900000, "genes": [
        {"name":"GENE_E","start":70000,"end":160000,"strand":"+","function":"Example cellular feature"},
        {"name":"GENE_F","start":310000,"end":390000,"strand":"-","function":"Example enzyme feature"},
        {"name":"GENE_G","start":620000,"end":710000,"strand":"+","function":"Example transport feature"}]},
    "X": {"length": 800000, "genes": [
        {"name":"GENE_X1","start":90000,"end":185000,"strand":"-","function":"Example X-chromosome feature"},
        {"name":"GENE_X2","start":360000,"end":455000,"strand":"+","function":"Example regulatory feature"},
        {"name":"GENE_X3","start":620000,"end":735000,"strand":"-","function":"Example structural feature"}]}
}

def parse_fasta(text):
    """Parse FASTA text and return a dictionary of sequence names and DNA strings."""
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

def parse_annotation(text, file_type):
    """Parse basic GFF3 or BED records into a list of feature dictionaries."""
    features = []
    for line in text.splitlines():
        if not line.strip() or line.startswith("#") or line.startswith("track") or line.startswith("browser"):
            continue
        columns = line.rstrip().split("\t")
        try:
            if file_type == "bed" and len(columns) >= 3:
                chromosome, start, end = columns[0], int(columns[1]) + 1, int(columns[2])
                name = columns[3] if len(columns) > 3 else "BED_feature"
                strand = columns[5] if len(columns) > 5 and columns[5] == "-" else "+"
            elif file_type == "gff3" and len(columns) >= 9:
                if columns[2] not in ("gene", "mRNA", "ncRNA_gene", "pseudogene"):
                    continue
                chromosome, start, end = columns[0], int(columns[3]), int(columns[4])
                attributes = {}
                for item in columns[8].split(";"):
                    if "=" in item:
                        key, value = item.split("=", 1)
                        attributes[key] = value
                name = attributes.get("Name", attributes.get("gene", attributes.get("ID", columns[2])))
                strand = columns[6] if columns[6] == "-" else "+"
            else:
                continue
            if start >= 1 and end >= start:
                features.append({"chromosome":chromosome,"name":name,"start":start,"end":end,
                                 "strand":strand,"function":"Feature loaded from annotation file"})
        except (ValueError, IndexError):
            continue
    return features

def prepare_genes(genes, chromosome_length):
    """Calculate each gene's percentage position and width for the browser track."""
    prepared = []
    for gene in genes:
        start = max(1, min(int(gene["start"]), chromosome_length))
        end = max(start, min(int(gene["end"]), chromosome_length))
        item = dict(gene)
        item.update({"start":start,"end":end,
                     "left":start / chromosome_length * 100,
                     "width":max((end - start) / chromosome_length * 100, 1.2)})
        prepared.append(item)
    return prepared

@app.route("/", methods=["GET", "POST"])
def home():
    selected_chromosome = request.values.get("chromosome", "1")
    if selected_chromosome not in GENOME_DATA:
        selected_chromosome = "1"
    search_text = request.values.get("gene_search", "").strip()
    message = ""

    if request.method == "POST" and "annotation_file" in request.files:
        uploaded = request.files["annotation_file"]
        if uploaded and uploaded.filename:
            filename = secure_filename(uploaded.filename).lower()
            content = uploaded.read().decode("utf-8", errors="replace")
            file_type = "bed" if filename.endswith(".bed") else "gff3"
            features = parse_annotation(content, file_type)
            matching = [feature for feature in features if feature["chromosome"] == selected_chromosome]
            if matching:
                GENOME_DATA[selected_chromosome]["genes"] = matching
                message = f"Loaded {len(matching)} features from {filename}."
            else:
                message = "No features for the selected chromosome were found in this file."

    chromosome_data = GENOME_DATA[selected_chromosome]
    genes = chromosome_data["genes"]
    selected_gene = next((gene for gene in genes if gene["name"].lower() == search_text.lower()), None) if search_text else None
    if search_text and selected_gene is None:
        message = f'Gene "{search_text}" was not found on chromosome {selected_chromosome}.'
    displayed_genes = prepare_genes(genes, chromosome_data["length"])
    if selected_gene:
        selected_gene = next(gene for gene in displayed_genes if gene["name"] == selected_gene["name"])

    return render_template("index.html", chromosomes=GENOME_DATA,
        selected_chromosome=selected_chromosome, chromosome_data=chromosome_data,
        genes=displayed_genes, selected_gene=selected_gene,
        search_text=search_text, message=message)

if __name__ == "__main__":
    app.run(debug=True)
