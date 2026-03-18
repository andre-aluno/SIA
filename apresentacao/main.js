/* ═══════════════════════════════════════════════════
   DATA — Professores e Disciplinas
═══════════════════════════════════════════════════ */
const PROFS = [
  { id: 1, name: 'Ana',    short: 'A', areas: ['Mat'],         level: 3, maxLoad: 80,  color: '#f59e0b' },
  { id: 2, name: 'Bruno',  short: 'B', areas: ['Comp', 'BD'],  level: 4, maxLoad: 60,  color: '#3b82f6' },
  { id: 3, name: 'Clara',  short: 'C', areas: ['Fís'],         level: 3, maxLoad: 80,  color: '#a855f7' },
  { id: 4, name: 'Diego',  short: 'D', areas: ['Estat','Mat'], level: 2, maxLoad: 40,  color: '#10b981' },
  { id: 5, name: 'Elena',  short: 'E', areas: ['Comp'],        level: 4, maxLoad: 80,  color: '#ef4444' },
  { id: 6, name: 'Felipe', short: 'F', areas: ['BD', 'Estat'], level: 3, maxLoad: 60,  color: '#f97316' },
];

const COURSES = [
  { id: 0, name: 'Cálculo I',       area: 'Mat',   load: 60, levelReq: 2 },
  { id: 1, name: 'Programação',     area: 'Comp',  load: 60, levelReq: 3 },
  { id: 2, name: 'Física I',        area: 'Fís',   load: 60, levelReq: 2 },
  { id: 3, name: 'Banco de Dados',  area: 'BD',    load: 40, levelReq: 3 },
  { id: 4, name: 'Estatística',     area: 'Estat', load: 40, levelReq: 2 },
  { id: 5, name: 'Álgebra Linear',  area: 'Mat',   load: 60, levelReq: 3 },
  { id: 6, name: 'Redes',           area: 'Comp',  load: 40, levelReq: 2 },
  { id: 7, name: 'Análise Dados',   area: 'Estat', load: 60, levelReq: 3 },
];

const CONCEPT_DETAILS = [
  'Um <strong>indivíduo</strong> é uma solução candidata completa. No nosso caso, é um plano de alocação: cada disciplina com um professor atribuído.',
  'O <strong>cromossomo</strong> é a representação do indivíduo. Aqui: uma lista onde cada posição é uma disciplina e cada valor é o ID do professor.',
  'Um <strong>gene</strong> é a menor decisão: "qual professor dá esta disciplina?". Nosso cromossomo tem 8 genes — um por oferta de disciplina.',
  'A <strong>população</strong> contém 100 cromossomos diferentes. Eles evoluem juntos — os melhores influenciam as próximas gerações.',
  'O <strong>fitness</strong> mede a qualidade da alocação. Avalia 5 critérios: competência, nível, carga, utilização e balanceamento.',
  'O <strong>crossover</strong> combina dois planos de alocação. Pai A contribui com as primeiras disciplinas, Pai B com as últimas — gerando filhos melhores.',
  'A <strong>mutação</strong> troca aleatoriamente o professor de alguma disciplina. Isso evita que o algoritmo fique preso em soluções medíocres.',
];

/* ═══════════════════════════════════════════════════
   NAVIGATION
═══════════════════════════════════════════════════ */
const slides     = document.querySelectorAll('.slide');
const navLabels  = document.querySelectorAll('.nav-label');
const progressBar = document.getElementById('progressBar');
const keyHintCounter = document.getElementById('keyHintCounter');
const dotsNav    = document.getElementById('dotsNav');
const TOTAL      = slides.length;
let currentIndex = 0;
const initialized = new Set();

function goTo(n) {
  if (n < 0 || n >= TOTAL) return;
  slides[currentIndex].classList.remove('active');
  navLabels[currentIndex].classList.remove('active');
  dotsNav.children[currentIndex].classList.remove('active');
  currentIndex = n;
  slides[currentIndex].classList.add('active');
  navLabels[currentIndex].classList.add('active');
  dotsNav.children[currentIndex].classList.add('active');
  const pct = (currentIndex / (TOTAL - 1)) * 100;
  progressBar.style.width = pct + '%';
  keyHintCounter.textContent = (currentIndex + 1) + ' / ' + TOTAL;
  if (!initialized.has(currentIndex)) {
    initialized.add(currentIndex);
    initSlide(currentIndex);
  }
}

// Build dots
slides.forEach((_, i) => {
  const dot = document.createElement('div');
  dot.className = 'nav-dot' + (i === 0 ? ' active' : '');
  dot.addEventListener('click', () => goTo(i));
  dotsNav.appendChild(dot);
});

// Build nav label click handlers
navLabels.forEach((lbl, i) => lbl.addEventListener('click', () => goTo(i)));

// Keyboard navigation
document.addEventListener('keydown', (e) => {
  if (document.activeElement.tagName === 'INPUT' ||
      document.activeElement.tagName === 'TEXTAREA') return;
  if (['ArrowDown', 'ArrowRight'].includes(e.key)) { e.preventDefault(); goTo(currentIndex + 1); }
  if (['ArrowUp', 'ArrowLeft'].includes(e.key))    { e.preventDefault(); goTo(currentIndex - 1); }
});

function initSlide(i) {
  const inits = [
    initHero, initConcept, initChromosome, initGene,
    initPopulation, initFitness, initSelection, initCrossover,
    initMutation, initDemo, initMapSlide, () => {}
  ];
  if (inits[i]) inits[i]();
}

// ── helpers ──
function rnd(arr) { return arr[Math.floor(Math.random() * arr.length)]; }
function randInt(min, max) { return Math.floor(Math.random() * (max - min + 1)) + min; }
function profById(id) { return PROFS.find(p => p.id === id); }
function randChromosome() { return COURSES.map(() => rnd(PROFS).id); }

/* ═══════════════════════════════════════════════════
   SLIDE 0: HERO CANVAS
═══════════════════════════════════════════════════ */
function initHero() {
  const canvas = document.getElementById('heroCanvas');
  const ctx = canvas.getContext('2d');
  let W, H, dots = [];

  function resize() {
    W = canvas.width  = canvas.offsetWidth;
    H = canvas.height = canvas.offsetHeight;
    buildDots();
  }

  function buildDots() {
    dots = [];
    const cols = Math.ceil(W / 60);
    const rows = Math.ceil(H / 60);
    for (let r = 0; r < rows; r++) {
      for (let c = 0; c < cols; c++) {
        dots.push({ x: c * 60 + 30, y: r * 60 + 30, phase: Math.random() * Math.PI * 2, speed: 0.003 + Math.random() * 0.004 });
      }
    }
  }

  function draw(t) {
    ctx.clearRect(0, 0, W, H);
    dots.forEach(d => {
      const pulse = 0.2 + 0.6 * (0.5 + 0.5 * Math.sin(t * d.speed + d.phase));
      ctx.beginPath();
      ctx.arc(d.x, d.y, 1.5, 0, Math.PI * 2);
      ctx.fillStyle = `rgba(74,222,128,${pulse * 0.4})`;
      ctx.fill();
    });
    requestAnimationFrame(draw);
  }

  window.addEventListener('resize', resize);
  resize();
  requestAnimationFrame(draw);
}

/* ═══════════════════════════════════════════════════
   SLIDE 1: CONCEPT
═══════════════════════════════════════════════════ */
function initConcept() {
  const detail = document.getElementById('conceptDetailBox');
  const items = document.querySelectorAll('.concept-item');
  const arrows = document.querySelectorAll('.concept-arrow-row');

  items.forEach(item => {
    item.addEventListener('click', () => {
      const pair = parseInt(item.dataset.pair);
      items.forEach(i => i.classList.remove('highlighted'));
      arrows.forEach(a => a.classList.remove('highlighted'));
      document.querySelectorAll(`.concept-item[data-pair="${pair}"]`).forEach(i => i.classList.add('highlighted'));
      document.querySelectorAll(`.concept-arrow-row[data-pair="${pair}"]`).forEach(a => a.classList.add('highlighted'));
      detail.innerHTML = CONCEPT_DETAILS[pair];
      detail.classList.add('filled');
    });
  });
}

/* ═══════════════════════════════════════════════════
   SLIDE 2: GENE
═══════════════════════════════════════════════════ */
let geneState = [];

function initGene() {
  geneState = COURSES.slice(0, 5).map(() => randInt(0, PROFS.length - 1));
  renderGeneTable();
}

function renderGeneTable() {
  const table = document.getElementById('geneTable');
  if (!table) return;
  table.innerHTML = '';
  COURSES.slice(0, 5).forEach((course, i) => {
    const prof = PROFS[geneState[i]];
    const row = document.createElement('div');
    row.className = 'gene-table-row';
    row.innerHTML = `
      <span class="gene-course-name">${course.name}</span>
      <div class="gene-cell" style="background:${prof.color}" data-i="${i}">${prof.short}</div>
      <span class="gene-prof-name">id ${prof.id} · Prof. ${prof.name}</span>
    `;
    table.appendChild(row);
  });

  table.querySelectorAll('.gene-cell').forEach(cell => {
    cell.addEventListener('click', () => {
      const i = parseInt(cell.dataset.i);
      geneState[i] = (geneState[i] + 1) % PROFS.length;
      const prof = PROFS[geneState[i]];
      document.getElementById('geneDemoNote').textContent = `Gene alterado! ${COURSES[i].name} → Prof. ${prof.name}`;
      renderGeneTable();
    });
  });
}

/* ═══════════════════════════════════════════════════
   SLIDE 3: CHROMOSOME
═══════════════════════════════════════════════════ */
let chromState = [];

function initChromosome() {
  chromState = randChromosome();
  renderChromosome();
  document.getElementById('newChromBtn').addEventListener('click', () => {
    chromState = randChromosome();
    renderChromosome();
  });
}

function renderChromosome() {
  const coursesLabels = document.getElementById('chromCoursesLabels');
  const genesRow      = document.getElementById('chromGenesRow');
  const profLabels    = document.getElementById('chromProfLabels');
  const legend        = document.getElementById('chromLegend');
  const reading       = document.getElementById('readingGrid');
  if (!coursesLabels) return;

  coursesLabels.innerHTML = '';
  genesRow.innerHTML = '';
  profLabels.innerHTML = '';

  const usedProfs = new Set();

  COURSES.forEach((course, i) => {
    const prof = profById(chromState[i]);
    usedProfs.add(prof.id);

    const cl = document.createElement('div');
    cl.className = 'chrom-col-label';
    cl.textContent = course.name;
    coursesLabels.appendChild(cl);

    const gene = document.createElement('div');
    gene.className = 'chrom-gene';
    gene.style.background = prof.color;
    gene.textContent = prof.short;
    genesRow.appendChild(gene);

    const pl = document.createElement('div');
    pl.className = 'chrom-col-label';
    pl.textContent = prof.name;
    profLabels.appendChild(pl);
  });

  // Legend
  legend.innerHTML = '';
  PROFS.forEach(p => {
    if (!usedProfs.has(p.id)) return;
    const li = document.createElement('div');
    li.className = 'legend-item';
    li.innerHTML = `<span class="legend-dot" style="background:${p.color}"></span>id ${p.id} · Prof. ${p.name}`;
    legend.appendChild(li);
  });

  // Python code representation
  const codeEl = document.getElementById('chromCodeBlock');
  if (!codeEl) return;

  const arrayLiteral = chromState.map(id => id).join(', ');
  const lines = COURSES.map((course, i) => {
    const prof = profById(chromState[i]);
    const match = prof.areas.includes(course.area);
    return `  <span class="c-green">${prof.id}</span>,  <span class="c-muted"># pos ${i} · ${course.name} → Prof. ${prof.name}</span>`;
  }).join('\n');

  codeEl.innerHTML =
    `<span class="c-yellow">cromossomo</span> = [\n` +
    lines + `\n` +
    `]`
}

/* ═══════════════════════════════════════════════════
   SLIDE 4: POPULATION
═══════════════════════════════════════════════════ */
function initPopulation() {
  renderPopulation();
  document.getElementById('newPopBtn').addEventListener('click', renderPopulation);
}

function calcSimpleFitness(chrom) {
  let score = 0;
  COURSES.forEach((course, i) => {
    const prof = profById(chrom[i]);
    if (prof.areas.includes(course.area)) score += 200;
    else score -= 1000;
    if (prof.level >= course.levelReq) score += 50;
  });
  return score;
}

function renderPopulation() {
  const grid = document.getElementById('populationGrid');
  const stats = document.getElementById('popStats');
  if (!grid) return;
  grid.innerHTML = '';
  const individuals = Array.from({ length: 24 }, () => randChromosome());
  const fitnesses = individuals.map(calcSimpleFitness);
  const maxF = Math.max(...fitnesses);
  const minF = Math.min(...fitnesses);

  let goodCount = 0, midCount = 0, badCount = 0;

  individuals.forEach((chrom, idx) => {
    const f = fitnesses[idx];
    const norm = maxF === minF ? 0.5 : (f - minF) / (maxF - minF);
    let cls = norm > 0.65 ? 'good' : norm > 0.35 ? 'mid' : 'bad';
    if (cls === 'good') goodCount++;
    else if (cls === 'mid') midCount++;
    else badCount++;

    const div = document.createElement('div');
    div.className = `pop-individual ${cls}`;
    const genes = COURSES.map((_, i) => {
      const prof = profById(chrom[i]);
      return `<div class="pop-mini-gene" style="background:${prof.color}"></div>`;
    }).join('');
    div.innerHTML = `<div class="pop-mini-genes">${genes}</div><div class="pop-fitness-label ${cls}">${f > 0 ? '+' : ''}${f}</div>`;
    grid.appendChild(div);
  });

  const avg = Math.round(fitnesses.reduce((a, b) => a + b, 0) / fitnesses.length);
  stats.innerHTML = `
    <div class="pop-stat-row"><span class="pop-stat-label">Indivíduos</span><span class="pop-stat-value">24</span></div>
    <div class="pop-stat-row"><span class="pop-stat-label">Melhor fitness</span><span class="pop-stat-value" style="color:var(--accent)">${maxF}</span></div>
    <div class="pop-stat-row"><span class="pop-stat-label">Pior fitness</span><span class="pop-stat-value" style="color:var(--danger)">${minF}</span></div>
    <div class="pop-stat-row"><span class="pop-stat-label">Média</span><span class="pop-stat-value">${avg}</span></div>
    <div class="pop-stat-row"><span class="pop-stat-label">Alta qualidade</span><span class="pop-stat-value" style="color:var(--accent)">${goodCount}</span></div>
    <div class="pop-stat-row"><span class="pop-stat-label">Baixa qualidade</span><span class="pop-stat-value" style="color:var(--danger)">${badCount}</span></div>
  `;
}

/* ═══════════════════════════════════════════════════
   SLIDE 5: FITNESS
═══════════════════════════════════════════════════ */
const FITNESS_EXAMPLE = {
  competency:   { label: 'Competência', icon: 'circle-check-big', val: +800, base: 800 },
  level:        { label: 'Nível',       icon: 'graduation-cap',   val: +250, base: 250 },
  overload:     { label: 'Carga máx.',  icon: 'clock-alert',      val:    0, base:   0 },
  utilization:  { label: 'Utilização',  icon: 'users',            val: -500, base:-500 },
  balance:      { label: 'Balanço',     icon: 'scale',            val: +100, base: 100 },
};

const criteriaKeys = ['competency', 'level', 'overload', 'utilization', 'balance'];
const criteriaActive = [true, true, true, true, true];

function initFitness() {
  renderFitnessScore();
  lucide.createIcons();

  document.querySelectorAll('.criterion-card').forEach(card => {
    card.addEventListener('click', () => {
      const crit = parseInt(card.dataset.crit);
      criteriaActive[crit] = !criteriaActive[crit];
      card.classList.toggle('active', criteriaActive[crit]);
      card.classList.toggle('inactive', !criteriaActive[crit]);
      renderFitnessScore();
    });
  });
}

function renderFitnessScore() {
  const breakdown = document.getElementById('scoreBreakdown');
  const totalEl   = document.getElementById('totalFitnessValue');
  if (!breakdown) return;

  breakdown.innerHTML = '';
  let total = 0;
  const maxAbs = Math.max(...criteriaKeys.map(k => Math.abs(FITNESS_EXAMPLE[k].base)));

  criteriaKeys.forEach((key, i) => {
    const entry = FITNESS_EXAMPLE[key];
    const active = criteriaActive[i];
    const val = active ? entry.val : 0;
    total += val;

    const sign  = val >= 0 ? 'pos' : 'neg';
    const barW  = Math.round((Math.abs(val) / maxAbs) * 100);
    const shown = active ? (val > 0 ? `+${val}` : `${val}`) : '—';

    const item = document.createElement('div');
    item.className = 'score-item';
    item.innerHTML = `
      <div class="score-item-top">
        <span class="score-item-name">
          <i data-lucide="${entry.icon}" class="score-item-icon"></i>${entry.label}
        </span>
        <span class="score-item-value ${active ? sign : 'zero'}">${shown}</span>
      </div>
      <div class="score-bar-wrap">
        <div class="score-bar ${active ? sign : ''}" style="width:${active ? barW : 0}%"></div>
      </div>
    `;
    breakdown.appendChild(item);
  });

  lucide.createIcons();
  totalEl.textContent = total > 0 ? `+${total}` : `${total}`;
  totalEl.style.color = total > 0 ? 'var(--accent)' : 'var(--danger)';
}

/* ═══════════════════════════════════════════════════
   SLIDE 6: SELEÇÃO
═══════════════════════════════════════════════════ */
const GLADIATOR_NAMES = [
  'Maximus', 'Spartacus', 'Commodus', 'Decimus', 'Lucius',
  'Brutus', 'Cassius', 'Titus', 'Flavius', 'Marcus',
  'Petronius', 'Varro',
];
const gladiatorWins = {};

function initSelection() {
  runTournament();
  lucide.createIcons();
  document.getElementById('runTournamentBtn').addEventListener('click', runTournament);
}

function runTournament() {
  const container = document.getElementById('tournamentCompetitors');
  const result    = document.getElementById('tournamentResult');
  container.innerHTML = '';

  // Sorteia 3 gladiadores com reposição — o mesmo pode aparecer duas vezes
  const candidates = Array.from({ length: 3 }, () => {
    const name    = rnd(GLADIATOR_NAMES);
    const fitness = calcSimpleFitness(randChromosome());
    const wins    = gladiatorWins[name] || 0;
    return { name, fitness, wins };
  });

  const maxFitness = Math.max(...candidates.map(c => c.fitness));
  const winnerIdx  = candidates.findIndex(c => c.fitness === maxFitness);
  gladiatorWins[candidates[winnerIdx].name] = (gladiatorWins[candidates[winnerIdx].name] || 0) + 1;

  candidates.forEach((cand, i) => {
    const isWinner = i === winnerIdx;
    const fitnessStr = cand.fitness > 0 ? `+${cand.fitness}` : `${cand.fitness}`;
    const card = document.createElement('div');
    card.className = `competitor-card ${isWinner ? 'winner' : 'loser'}`;
    card.innerHTML = `
      <div class="gladiator-shield ${isWinner ? 'shield-winner' : ''}">
        <i data-lucide="${isWinner ? 'shield-check' : 'shield'}"></i>
      </div>
      <div class="competitor-info">
        <div class="competitor-name">${cand.name}</div>
        <div class="competitor-desc">
          Força: <strong>${fitnessStr}</strong>
          ${cand.wins > 0 ? `· <span class="wins-badge">${cand.wins} vitória${cand.wins > 1 ? 's' : ''} anteriores</span>` : ''}
        </div>
      </div>
      <div class="competitor-fitness-col">
        <span class="competitor-return ${isWinner ? 'return-selected' : 'return-back'}">
          ${isWinner ? 'selecionado como pai' : 'volta à fila'}
        </span>
      </div>
    `;
    container.appendChild(card);
  });

  const w = candidates[winnerIdx];
  const totalWins = gladiatorWins[w.name];
  result.innerHTML = `
    <span class="result-win">${w.name} vence o combate e é selecionado como pai</span>
    <span class="result-note">
      Todos os 3 voltam à fila de espera.
      ${totalWins > 1 ? `<strong>${w.name} já venceu ${totalWins} combates</strong> — pode ter múltiplas cópias na próxima geração.` : 'Continue clicando para ver um gladiador vencer mais de uma vez.'}
    </span>
  `;

  lucide.createIcons();
}

/* ═══════════════════════════════════════════════════
   SLIDE 7: CROSSOVER
═══════════════════════════════════════════════════ */
let cxParentA = [], cxParentB = [];
let currentCxCut = 4;

function initCrossover() {
  newCxParents();
  document.getElementById('newCxParentsBtn').addEventListener('click', newCxParents);
}

function newCxParents() {
  cxParentA = randChromosome();
  cxParentB = randChromosome();
  renderCrossover(currentCxCut);
}

function renderRuler(cut) {
  const ruler = document.getElementById('cxRuler');
  if (!ruler) return;
  ruler.innerHTML = '';
  const N = COURSES.length;
  for (let i = 0; i < N; i++) {
    const slot = document.createElement('div');
    slot.className = 'cx-ruler-slot';
    slot.textContent = i;
    ruler.appendChild(slot);
    if (i < N - 1) {
      const gap = document.createElement('div');
      gap.className = 'cx-ruler-gap' + (cut === i + 1 ? ' active' : '');
      gap.dataset.cut = i + 1;
      const inner = document.createElement('div');
      inner.className = 'cx-ruler-gap-inner';
      gap.appendChild(inner);
      gap.addEventListener('click', () => {
        currentCxCut = i + 1;
        renderCrossover(currentCxCut);
      });
      ruler.appendChild(gap);
    }
  }
}

function updateCutLine(cut) {
  const cutLine    = document.getElementById('cxCutLine');
  const canvas     = document.getElementById('cxCanvas');
  const parentWrap = document.getElementById('cxParentA');
  if (!cutLine || !canvas || !parentWrap) return;
  const genes = parentWrap.querySelectorAll('.cx-gene');
  if (genes.length < 2 || cut < 1 || cut > genes.length - 1) return;
  const canvasRect = canvas.getBoundingClientRect();
  const prevRect   = genes[cut - 1].getBoundingClientRect();
  const nextRect   = genes[cut].getBoundingClientRect();
  const midX       = (prevRect.right + nextRect.left) / 2;
  cutLine.style.left = (midX - canvasRect.left) + 'px';
}

function renderCrossover(cut) {
  renderRuler(cut);
  renderCxRow('cxParentA', cxParentA, cut, 'parent');
  renderCxRow('cxParentB', cxParentB, cut, 'parent');

  const childA = [...cxParentA.slice(0, cut), ...cxParentB.slice(cut)];
  const childB = [...cxParentB.slice(0, cut), ...cxParentA.slice(cut)];

  renderCxRow('cxChildA', childA, cut, 'childA');
  renderCxRow('cxChildB', childB, cut, 'childB');

  requestAnimationFrame(() => updateCutLine(cut));

  const label = document.getElementById('cxCutLabel');
  if (label) label.textContent = `corte: ${cut}`;

  const matchA = COURSES.filter((c, i) => profById(childA[i]).areas.includes(c.area)).length;
  const matchB = COURSES.filter((c, i) => profById(childB[i]).areas.includes(c.area)).length;
  const analysis = document.getElementById('cxAnalysis');
  analysis.innerHTML = `
    <div style="display:flex;flex-direction:column;gap:10px;">
      <div>Corte na posição <strong>${cut}</strong> de ${COURSES.length}</div>
      <div>Filho A herda posições <strong>0–${cut - 1}</strong> do Pai A e <strong>${cut}–${COURSES.length - 1}</strong> do Pai B</div>
      <div style="margin-top:6px;display:flex;flex-direction:column;gap:6px;">
        <div style="color:var(--accent)">Filho A: ${matchA}/${COURSES.length} matches de área</div>
        <div style="color:var(--accent)">Filho B: ${matchB}/${COURSES.length} matches de área</div>
      </div>
    </div>
  `;
}

function renderCxRow(elId, chrom, cut, mode) {
  const wrap = document.getElementById(elId);
  if (!wrap) return;
  wrap.innerHTML = '';
  COURSES.forEach((course, i) => {
    const prof = profById(chrom[i]);
    const fromA = i < cut;
    const div = document.createElement('div');
    div.className = 'cx-gene';
    if (mode === 'parent') {
      div.style.background = prof.color;
      div.style.opacity = '1';
    } else if (mode === 'childA') {
      div.style.background = fromA ? profById(cxParentA[i]).color : profById(cxParentB[i]).color;
      div.style.opacity = fromA ? '1' : '0.65';
      div.style.outline = fromA ? 'none' : '2px dashed rgba(255,255,255,0.3)';
    } else {
      div.style.background = fromA ? profById(cxParentB[i]).color : profById(cxParentA[i]).color;
      div.style.opacity = fromA ? '1' : '0.65';
      div.style.outline = fromA ? 'none' : '2px dashed rgba(255,255,255,0.3)';
    }
    div.innerHTML = `${prof.short}<span style="font-size:9px;display:block;opacity:0.8">${course.name.slice(0,5)}</span>`;
    wrap.appendChild(div);
  });
}

/* ═══════════════════════════════════════════════════
   SLIDE 8: MUTAÇÃO
═══════════════════════════════════════════════════ */
let mutOriginal = [];
let mutResult   = [];

function initMutation() {
  mutOriginal = randChromosome();
  mutResult   = [...mutOriginal];
  renderMutBefore();
  renderMutAfter([], false);

  document.getElementById('mutSlider').addEventListener('input', function(e) {
    e.stopPropagation();
    document.getElementById('mutProbDisplay').textContent = this.value + '%';
  });

  document.getElementById('applyMutBtn').addEventListener('click', () => {
    const prob = parseInt(document.getElementById('mutSlider').value) / 100;
    const changed = [];
    mutResult = mutOriginal.map((profId, i) => {
      if (Math.random() < prob) {
        changed.push(i);
        let newP;
        do { newP = rnd(PROFS); } while (newP.id === profId && PROFS.length > 1);
        return newP.id;
      }
      return profId;
    });
    renderMutAfter(changed, true);
    const info = document.getElementById('mutChangedInfo');
    if (changed.length === 0) {
      info.textContent = 'Nenhum gene foi alterado desta vez.';
      info.style.color = 'var(--muted)';
    } else {
      info.textContent = `${changed.length} gene(s) mutado(s): ${changed.map(i => COURSES[i].name).join(', ')}`;
      info.style.color = 'var(--warning)';
    }
  });

  document.getElementById('resetMutBtn').addEventListener('click', () => {
    mutOriginal = randChromosome();
    mutResult   = [...mutOriginal];
    renderMutBefore();
    renderMutAfter([], false);
    document.getElementById('mutChangedInfo').textContent = '';
  });
}

function renderMutBefore() {
  const el = document.getElementById('mutBefore');
  if (!el) return;
  el.innerHTML = '';
  mutOriginal.forEach((profId, i) => {
    const prof = profById(profId);
    const div = document.createElement('div');
    div.className = 'mut-gene';
    div.style.background = prof.color;
    div.innerHTML = `${prof.short}<span class="mut-gene-label">${COURSES[i].name.slice(0,5)}</span>`;
    el.appendChild(div);
  });
}

function renderMutAfter(changedIdxs, applied) {
  const el = document.getElementById('mutAfter');
  if (!el) return;
  el.innerHTML = '';
  const source = applied ? mutResult : mutOriginal;
  source.forEach((profId, i) => {
    const prof = profById(profId);
    const div = document.createElement('div');
    div.className = 'mut-gene' + (changedIdxs.includes(i) ? ' mutated' : '');
    div.style.background = prof.color;
    if (changedIdxs.includes(i)) div.style.outline = '2px solid rgba(255,255,255,0.6)';
    div.innerHTML = `${prof.short}<span class="mut-gene-label">${COURSES[i].name.slice(0,5)}</span>`;
    el.appendChild(div);
  });
}

/* ═══════════════════════════════════════════════════
   SLIDE 9: DEMO — GA SIMULATION
═══════════════════════════════════════════════════ */
let demoChart = null;
let demoInterval = null;
let demoGen = 0;
let demoPop = [];
let demoBestData = [];
let demoAvgData  = [];
const DEMO_POP_SIZE = 40;
const DEMO_MAX_GEN  = 60;

function fullFitness(chrom) {
  let score = 0;
  const loads = {};
  PROFS.forEach(p => { loads[p.id] = 0; });

  COURSES.forEach((course, i) => {
    const prof = profById(chrom[i]);
    if (prof.areas.includes(course.area)) score += 200;
    else score -= 1000;
    if (prof.level >= course.levelReq) score += 50;
    loads[prof.id] += course.load;
  });

  PROFS.forEach(p => {
    if (loads[p.id] > p.maxLoad) score -= 5000 * (loads[p.id] - p.maxLoad);
  });

  const used = PROFS.filter(p => loads[p.id] > 0).length;
  score -= 500 * Math.pow(PROFS.length - used, 2);

  const ratios = PROFS.map(p => p.maxLoad > 0 ? loads[p.id] / p.maxLoad : 0);
  const mean = ratios.reduce((a, b) => a + b, 0) / ratios.length;
  const variance = ratios.reduce((s, r) => s + Math.pow(r - mean, 2), 0) / ratios.length;
  const sigma = Math.sqrt(variance);
  score += 100 * (1 - Math.min(Math.max(sigma, 0), 1));

  return score;
}

function tournament(pop, fitnesses, size = 3) {
  let best = null, bestF = -Infinity;
  for (let i = 0; i < size; i++) {
    const idx = randInt(0, pop.length - 1);
    if (fitnesses[idx] > bestF) { bestF = fitnesses[idx]; best = pop[idx]; }
  }
  return best;
}

function crossover(a, b) {
  const cut = randInt(1, COURSES.length - 1);
  return [
    [...a.slice(0, cut), ...b.slice(cut)],
    [...b.slice(0, cut), ...a.slice(cut)],
  ];
}

function mutate(chrom, prob = 0.15) {
  return chrom.map(profId => {
    if (Math.random() < prob) return rnd(PROFS).id;
    return profId;
  });
}

function evolveOnce() {
  const fitnesses = demoPop.map(fullFitness);
  const newPop = [];
  while (newPop.length < DEMO_POP_SIZE) {
    const pa = tournament(demoPop, fitnesses);
    const pb = tournament(demoPop, fitnesses);
    const [ca, cb] = crossover(pa, pb);
    newPop.push(mutate(ca), mutate(cb));
  }
  demoPop = newPop.slice(0, DEMO_POP_SIZE);
}

function initDemo() {
  const ctx = document.getElementById('evolutionChart').getContext('2d');
  if (demoChart) { demoChart.destroy(); demoChart = null; }
  demoChart = new Chart(ctx, {
    type: 'line',
    data: {
      labels: [],
      datasets: [
        {
          label: 'Melhor fitness',
          data: [],
          borderColor: '#4ade80',
          backgroundColor: 'rgba(74,222,128,0.1)',
          fill: true,
          tension: 0.4,
          borderWidth: 2,
          pointRadius: 0,
        },
        {
          label: 'Fitness médio',
          data: [],
          borderColor: '#38bdf8',
          backgroundColor: 'transparent',
          fill: false,
          tension: 0.4,
          borderWidth: 1.5,
          pointRadius: 0,
          borderDash: [4, 4],
        }
      ]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      animation: { duration: 0 },
      plugins: {
        legend: { labels: { color: '#5a6278', font: { family: 'JetBrains Mono', size: 11 } } }
      },
      scales: {
        x: { ticks: { color: '#5a6278', font: { family: 'JetBrains Mono', size: 10 } }, grid: { color: 'rgba(255,255,255,0.04)' } },
        y: { ticks: { color: '#5a6278', font: { family: 'JetBrains Mono', size: 10 } }, grid: { color: 'rgba(255,255,255,0.04)' } }
      }
    }
  });

  resetDemo();

  document.getElementById('demoPlayBtn').addEventListener('click', playDemo);
  document.getElementById('demoPauseBtn').addEventListener('click', pauseDemo);
  document.getElementById('demoResetBtn').addEventListener('click', resetDemo);
}

function resetDemo() {
  pauseDemo();
  demoGen = 0;
  demoBestData = [];
  demoAvgData  = [];
  demoPop = Array.from({ length: DEMO_POP_SIZE }, () => randChromosome());

  if (demoChart) {
    demoChart.data.labels = [];
    demoChart.data.datasets[0].data = [];
    demoChart.data.datasets[1].data = [];
    demoChart.update();
  }

  document.getElementById('demoGeneration').textContent = '0';
  document.getElementById('demoBestFitness').textContent = '—';
  document.getElementById('demoAvgFitness').textContent  = '—';
  document.getElementById('demoCompatibility').textContent = '—';
  document.getElementById('demoBestGenes').innerHTML = '';
  document.getElementById('demoPlayBtn').disabled  = false;
  document.getElementById('demoPauseBtn').disabled = true;
}

function playDemo() {
  if (demoInterval) return;
  document.getElementById('demoPlayBtn').disabled  = true;
  document.getElementById('demoPauseBtn').disabled = false;

  demoInterval = setInterval(() => {
    if (demoGen >= DEMO_MAX_GEN) { pauseDemo(); return; }
    evolveOnce();
    demoGen++;

    const fitnesses = demoPop.map(fullFitness);
    const best = Math.max(...fitnesses);
    const avg  = Math.round(fitnesses.reduce((a, b) => a + b, 0) / fitnesses.length);
    const bestChrom = demoPop[fitnesses.indexOf(best)];
    const matches = COURSES.filter((c, i) => profById(bestChrom[i]).areas.includes(c.area)).length;
    const compat = Math.round(matches / COURSES.length * 100);

    demoChart.data.labels.push(demoGen);
    demoChart.data.datasets[0].data.push(best);
    demoChart.data.datasets[1].data.push(avg);
    demoChart.update('none');

    document.getElementById('demoGeneration').textContent = demoGen;
    document.getElementById('demoBestFitness').textContent = best > 0 ? `+${best}` : `${best}`;
    document.getElementById('demoAvgFitness').textContent  = avg > 0 ? `+${avg}` : `${avg}`;
    document.getElementById('demoCompatibility').textContent = compat + '%';

    const genesEl = document.getElementById('demoBestGenes');
    genesEl.innerHTML = '';
    bestChrom.forEach((profId, i) => {
      const prof = profById(profId);
      const match = prof.areas.includes(COURSES[i].area);
      const span = document.createElement('div');
      span.className = 'demo-best-gene';
      span.style.background = prof.color;
      span.style.opacity = match ? '1' : '0.45';
      span.title = `${COURSES[i].name} → ${prof.name} ${match ? '✅' : '❌'}`;
      span.textContent = prof.short;
      genesEl.appendChild(span);
    });
  }, 120);
}

function pauseDemo() {
  clearInterval(demoInterval);
  demoInterval = null;
  document.getElementById('demoPlayBtn').disabled  = demoGen >= DEMO_MAX_GEN;
  document.getElementById('demoPauseBtn').disabled = true;
}

/* ═══════════════════════════════════════════════════
   SLIDE 10: MAPA — ANALOGIA DO ESPAÇO DE BUSCA
═══════════════════════════════════════════════════ */
const M_COLS = 26, M_ROWS = 12, M_CTR = 5.5;

const MAP_PHASES = [
  { tag: 'Ponto de partida', title: 'O Espaço de Busca',        desc: 'De A até B existe um número enorme de caminhos possíveis. Explorar todos levaria mais tempo que o universo tem.' },
  { tag: 'Geração 0',        title: 'Exploração Inicial',        desc: 'O AG sorteia cromossomos aleatórios — caminhos espalhados por todo o espaço de busca. A névoa se levanta onde exploramos.' },
  { tag: 'Fitness',          title: 'Avaliação dos Caminhos',    desc: 'Cada caminho recebe uma nota. Quanto mais direto ao destino, melhor o fitness. Verde é ótimo, vermelho é ruim.' },
  { tag: 'Seleção',          title: 'O Funil',                   desc: 'Apenas os melhores caminhos sobrevivem. O espaço de busca se concentra na direção mais promissora — o restante desaparece.' },
  { tag: 'Geração 1',        title: 'Crossover + Mutação',       desc: 'Combinamos os bons caminhos e adicionamos pequenas variações — exploramos um pouco mais dentro da boa direção.' },
  { tag: 'Geração 2',        title: 'Convergindo',               desc: 'A avaliação e seleção se repetem. A cada ciclo o funil se estreita — as boas direções ficam cada vez mais evidentes.' },
  { tag: 'Chegamos!',        title: 'Destino Alcançado',         desc: 'Sem explorar todo o espaço, o AG convergiu para o caminho ótimo através de ciclos de seleção e exploração localizada.' },
];

function initMapSlide() {
  const canvas = document.getElementById('mapCanvas');
  if (!canvas) return;
  const ctx = canvas.getContext('2d');
  let W, H, cW, cH;
  let mapPhaseIdx = 0;

  // Precompute terrain noise (stable across renders)
  const terrainNoise = Array.from({ length: M_ROWS }, (_, r) =>
    Array.from({ length: M_COLS }, (_, c) =>
      Math.sin(c * 0.7 + r * 1.3) * 0.5 + Math.cos(c * 1.1 - r * 0.8) * 0.3
    )
  );

  // ── Path generation ──
  function genPath(spread) {
    const nWP = 4;
    const wps = [{ t: 0, r: M_CTR }];
    for (let i = 1; i <= nWP; i++) {
      const t = i / (nWP + 1);
      const bell = 4 * t * (1 - t);
      const r = M_CTR + (Math.random() - 0.5) * 2 * spread * bell;
      wps.push({ t, r: Math.max(0.5, Math.min(M_ROWS - 0.5, r)) });
    }
    wps.push({ t: 1, r: M_CTR });

    const path = [];
    for (let c = 0; c < M_COLS; c++) {
      const t = c / (M_COLS - 1);
      let i = 0;
      while (i < wps.length - 2 && wps[i + 1].t < t) i++;
      const { t: t0, r: r0 } = wps[i];
      const { t: t1, r: r1 } = wps[i + 1];
      const alpha = t0 === t1 ? 0 : (t - t0) / (t1 - t0);
      path.push(r0 + alpha * (r1 - r0));
    }
    return path;
  }

  function genPathNear(base, spread) {
    // Sample base at a few waypoints, add smooth offsets, then interpolate —
    // same structure as genPath so the resulting path is smooth, not jagged.
    const nWP = 4;
    const wps = [];
    for (let i = 0; i <= nWP; i++) {
      const t   = i / nWP;
      const col = Math.round(t * (M_COLS - 1));
      const r   = base[col] + (Math.random() - 0.5) * 2 * spread;
      wps.push({ t, r: Math.max(0.5, Math.min(M_ROWS - 0.5, r)) });
    }
    const path = [];
    for (let c = 0; c < M_COLS; c++) {
      const t = c / (M_COLS - 1);
      let i = 0;
      while (i < wps.length - 2 && wps[i + 1].t < t) i++;
      const { t: t0, r: r0 } = wps[i];
      const { t: t1, r: r1 } = wps[i + 1];
      const alpha = t0 === t1 ? 0 : (t - t0) / (t1 - t0);
      path.push(r0 + alpha * (r1 - r0));
    }
    return path;
  }

  function pathFitness(path) {
    const avgDev = path.reduce((s, r) => s + Math.abs(r - M_CTR), 0) / path.length;
    return 1 - avgDev / (M_ROWS / 2);
  }

  function fitnessColor(f) {
    if (f > 0.72) return '#4ade80';
    if (f > 0.55) return '#a3e635';
    if (f > 0.38) return '#f59e0b';
    return '#ef4444';
  }

  // ── Pre-generate all path sets ──
  const pop1 = Array.from({ length: 22 }, () => genPath(M_ROWS * 0.43));
  const fit1 = pop1.map(pathFitness);

  const sel1 = [...pop1].map((p, i) => ({ p, f: fit1[i] }))
    .sort((a, b) => b.f - a.f).slice(0, 6).map(x => x.p);

  const pop2 = Array.from({ length: 18 }, () => {
    const base = sel1[Math.floor(Math.random() * sel1.length)];
    return genPathNear(base, M_ROWS * 0.17);
  });
  const fit2 = pop2.map(pathFitness);

  const sel2 = [...pop2].map((p, i) => ({ p, f: fit2[i] }))
    .sort((a, b) => b.f - a.f).slice(0, 5).map(x => x.p);

  const pop3 = Array.from({ length: 12 }, () => {
    const base = sel2[Math.floor(Math.random() * sel2.length)];
    return genPathNear(base, M_ROWS * 0.07);
  });
  const bestPath = [...pop3].map(p => ({ p, f: pathFitness(p) }))
    .sort((a, b) => b.f - a.f)[0].p;

  // ── Fog computation ──
  function makeFog(v) {
    return Array.from({ length: M_ROWS }, () => new Array(M_COLS).fill(v));
  }

  function liftFog(fog, paths) {
    const f = fog.map(r => [...r]);
    paths.forEach(path => {
      path.forEach((row, c) => {
        const r = Math.floor(row);
        const frac = row - r;
        [[r, 1 - frac], [r + 1, frac]].forEach(([cr, w]) => {
          if (cr >= 0 && cr < M_ROWS) f[cr][c] = Math.max(0, f[cr][c] - 0.85 * w);
        });
        [r - 1, r + 2].forEach(cr => {
          if (cr >= 0 && cr < M_ROWS) f[cr][c] = Math.max(0, f[cr][c] - 0.3);
        });
      });
    });
    return f;
  }

  const fog0 = makeFog(1);
  const fog1 = liftFog(fog0, pop1);
  const fog4 = liftFog(fog1, pop2);
  const fog6 = liftFog(fog4, pop3);

  // ── Phase descriptors ──
  const phaseData = [
    { fog: fog0, visible: [],                                                               dimmed: [],                                                                       best: null },
    { fog: fog1, visible: pop1.map((p, i) => ({ p, color: '#4ade80' })),                  dimmed: [],                                                                       best: null },
    { fog: fog1, visible: pop1.map((p, i) => ({ p, color: fitnessColor(fit1[i]) })),      dimmed: [],                                                                       best: null },
    { fog: fog1, visible: sel1.map(p => ({ p, color: '#4ade80' })),                        dimmed: pop1.filter(p => !sel1.includes(p)).map(p => ({ p, color: '#334155' })), best: null },
    { fog: fog4, visible: pop2.map((p, i) => ({ p, color: fitnessColor(fit2[i]) })),      dimmed: sel1.map(p => ({ p, color: '#1e2d22' })),                                 best: null },
    { fog: fog4, visible: sel2.map(p => ({ p, color: '#4ade80' })),                        dimmed: pop2.filter(p => !sel2.includes(p)).map(p => ({ p, color: '#334155' })), best: null },
    { fog: fog6, visible: [],                                                               dimmed: sel2.map(p => ({ p, color: '#1a2e1a' })),                                best: bestPath },
  ];

  // ── Drawing ──
  function drawTerrain() {
    ctx.fillStyle = '#07100a';
    ctx.fillRect(0, 0, W, H);
    for (let r = 0; r < M_ROWS; r++) {
      for (let c = 0; c < M_COLS; c++) {
        const alpha = Math.max(0.02, 0.05 + terrainNoise[r][c] * 0.025);
        ctx.fillStyle = `rgba(74,222,128,${alpha})`;
        ctx.fillRect(c * cW + 0.5, r * cH + 0.5, cW - 1, cH - 1);
      }
    }
  }

  function drawFog(fog) {
    for (let r = 0; r < M_ROWS; r++) {
      for (let c = 0; c < M_COLS; c++) {
        const op = fog[r][c];
        if (op > 0.02) {
          ctx.fillStyle = `rgba(7,16,10,${op * 0.94})`;
          ctx.fillRect(c * cW, r * cH, cW, cH);
        }
      }
    }
  }

  function drawPathLine(path, color, opacity, lineWidth) {
    ctx.save();
    ctx.globalAlpha = opacity;
    ctx.strokeStyle = color;
    ctx.lineWidth = lineWidth || 2;
    ctx.lineJoin = 'round';
    ctx.lineCap = 'round';
    ctx.beginPath();
    path.forEach((row, c) => {
      const x = (c + 0.5) * cW;
      const y = row * cH;
      if (c === 0) ctx.moveTo(x, y); else ctx.lineTo(x, y);
    });
    ctx.stroke();
    ctx.restore();
  }

  function drawMarker(col, label, isB) {
    const x = (col === 0 ? 0.5 : M_COLS - 0.5) * cW;
    const y = M_CTR * cH;
    const color = isB ? '#facc15' : '#4ade80';

    // Glow
    const grd = ctx.createRadialGradient(x, y, 0, x, y, 32);
    grd.addColorStop(0, isB ? 'rgba(250,204,21,0.35)' : 'rgba(74,222,128,0.3)');
    grd.addColorStop(1, 'rgba(0,0,0,0)');
    ctx.fillStyle = grd;
    ctx.fillRect(x - 34, y - 34, 68, 68);

    // Circle
    ctx.beginPath();
    ctx.arc(x, y, 11, 0, Math.PI * 2);
    ctx.fillStyle = color;
    ctx.fill();

    // Letter
    ctx.fillStyle = '#000';
    ctx.font = 'bold 11px "JetBrains Mono", monospace';
    ctx.textAlign = 'center';
    ctx.textBaseline = 'middle';
    ctx.fillText(label, x, y);
  }

  function drawBestPath(path) {
    drawPathLine(path, 'rgba(250,204,21,0.15)', 1, 8);
    drawPathLine(path, 'rgba(250,204,21,0.4)',  1, 4);
    drawPathLine(path, '#facc15',               1, 2);
  }

  function draw() {
    const pd = phaseData[mapPhaseIdx];
    drawTerrain();
    drawFog(pd.fog);
    pd.dimmed.forEach(({ p, color }) => drawPathLine(p, color, 0.45));
    pd.visible.forEach(({ p, color }) => drawPathLine(p, color, 0.85));
    if (pd.best) drawBestPath(pd.best);
    drawMarker(0,           'A', false);
    drawMarker(M_COLS - 1,  'B', true);
  }

  // ── UI ──
  function updateUI() {
    const ph = MAP_PHASES[mapPhaseIdx];
    document.getElementById('mapPhaseTag').textContent   = ph.tag;
    document.getElementById('mapPhaseTitle').textContent = ph.title;
    document.getElementById('mapPhaseDesc').textContent  = ph.desc;
    [...document.getElementById('mapDots').children].forEach((d, i) =>
      d.classList.toggle('active', i === mapPhaseIdx)
    );
    document.getElementById('mapPrevBtn').disabled = mapPhaseIdx === 0;
    const isLast = mapPhaseIdx === MAP_PHASES.length - 1;
    document.getElementById('mapNextBtn').disabled   = isLast;
    document.getElementById('mapNextBtn').textContent = isLast ? 'Fim' : 'Próxima →';
    draw();
  }

  // Build dots
  const dotsEl = document.getElementById('mapDots');
  MAP_PHASES.forEach((_, i) => {
    const dot = document.createElement('div');
    dot.className = 'map-dot' + (i === 0 ? ' active' : '');
    dot.addEventListener('click', () => { mapPhaseIdx = i; updateUI(); });
    dotsEl.appendChild(dot);
  });

  document.getElementById('mapPrevBtn').addEventListener('click', () => {
    if (mapPhaseIdx > 0) { mapPhaseIdx--; updateUI(); }
  });
  document.getElementById('mapNextBtn').addEventListener('click', () => {
    if (mapPhaseIdx < MAP_PHASES.length - 1) { mapPhaseIdx++; updateUI(); }
  });

  function resize() {
    W  = canvas.width  = canvas.parentElement.offsetWidth;
    H  = canvas.height = 260;
    cW = W / M_COLS;
    cH = H / M_ROWS;
    draw();
  }

  window.addEventListener('resize', resize);
  resize();
  updateUI();
}

/* ═══════════════════════════════════════════════════
   INIT
═══════════════════════════════════════════════════ */
navLabels[0].classList.add('active');
initialized.add(0);
initHero();
progressBar.style.width = '0%';
