const genomeData = {
  '1': { length: 248956422, genes: [
    {name:'GENE-A', start:10000000, end:18000000, strand:'forward', function:'Example protein-coding gene'},
    {name:'BRCA1', start:43044295, end:43170245, strand:'reverse', function:'DNA repair and tumor suppression'},
    {name:'GENE-B', start:82000000, end:90000000, strand:'forward', function:'Example regulatory gene'},
    {name:'TP53', start:110000000, end:110500000, strand:'forward', function:'Cell-cycle and DNA-damage response'}
  ]},
  '2': { length:242193529, genes: [
    {name:'GENE-C', start:15000000, end:22000000, strand:'forward', function:'Example metabolic gene'},
    {name:'GENE-D', start:65000000, end:73000000, strand:'reverse', function:'Example signaling gene'},
    {name:'GENE-E', start:125000000, end:135000000, strand:'forward', function:'Example protein-coding gene'}
  ]},
  'X': { length:156040895, genes: [
    {name:'GENE-X1', start:5000000, end:12000000, strand:'forward', function:'Example X-chromosome gene'},
    {name:'DMD', start:31000000, end:33300000, strand:'reverse', function:'Dystrophin-associated gene'},
    {name:'GENE-X2', start:80000000, end:87000000, strand:'forward', function:'Example regulatory gene'}
  ]}
};

const chromosome = document.getElementById('chromosome');
const geneTrack = document.getElementById('geneTrack');
const featureInfo = document.getElementById('featureInfo');
const regionTitle = document.getElementById('regionTitle');
const regionText = document.getElementById('regionText');
const ruler = document.getElementById('ruler');
const stats = document.getElementById('genomeStats');

function formatBp(n) { return n.toLocaleString() + ' bp'; }

function render() {
  const chr = chromosome.value;
  const data = genomeData[chr];
  regionTitle.textContent = `Chromosome ${chr}`;
  regionText.textContent = `1 – ${formatBp(data.length)}`;
  geneTrack.innerHTML = '';
  ruler.innerHTML = '';

  for (let i = 0; i <= 5; i++) {
    const tick = document.createElement('span');
    tick.textContent = formatBp(Math.round(data.length * i / 5));
    ruler.appendChild(tick);
  }

  data.genes.forEach((gene, index) => {
    const el = document.createElement('div');
    el.className = `gene ${gene.strand === 'forward' ? 'forward' : 'reverse'}`;
    el.style.left = `${(gene.start / data.length) * 100}%`;
    el.style.width = `${Math.max(((gene.end - gene.start) / data.length) * 100, 4)}%`;
    el.style.top = `${25 + (index % 2) * 45}px`;
    el.textContent = gene.name;
    el.title = `${gene.name}: ${formatBp(gene.start)}–${formatBp(gene.end)}`;
    el.onclick = () => selectGene(gene, el);
    geneTrack.appendChild(el);
  });

  stats.innerHTML = `<li>Chromosome: ${chr}</li><li>Length: ${formatBp(data.length)}</li><li>Displayed genes: ${data.genes.length}</li><li>Scale: full chromosome view</li>`;
  featureInfo.textContent = 'Click a gene on the genome track to see details.';
}

function selectGene(gene, element) {
  document.querySelectorAll('.gene').forEach(g => g.classList.remove('highlight'));
  element.classList.add('highlight');
  featureInfo.innerHTML = `<strong>${gene.name}</strong><br>Start: ${formatBp(gene.start)}<br>End: ${formatBp(gene.end)}<br>Strand: ${gene.strand}<br>Function: ${gene.function}`;
}

document.getElementById('searchBtn').onclick = () => {
  const query = document.getElementById('geneSearch').value.trim().toUpperCase();
  const data = genomeData[chromosome.value];
  const index = data.genes.findIndex(g => g.name.toUpperCase() === query);
  if (index === -1) {
    featureInfo.textContent = query ? `Gene “${query}” was not found on chromosome ${chromosome.value}.` : 'Enter a gene name to search.';
    return;
  }
  const element = geneTrack.children[index];
  selectGene(data.genes[index], element);
  element.scrollIntoView({behavior:'smooth', block:'center', inline:'center'});
};

document.getElementById('resetBtn').onclick = () => {
  document.getElementById('geneSearch').value = '';
  chromosome.value = '1';
  render();
};
chromosome.onchange = render;
render();
