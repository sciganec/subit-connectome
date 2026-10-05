import json
import os

json_path = os.path.normpath(os.path.join(os.path.dirname(__file__), "..", "output", "metagraphs", "subit64_metagraph.json"))
with open(json_path, "r", encoding="utf-8") as f:
    data = json.load(f)

html_template = """<!DOCTYPE html>
<html lang="uk" class="h-full">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>SUBIT-64 MaleCNS Functional Architecture</title>
  <script src="https://www.gstatic.com/antigravity/web/dev/tailwindcss.min.js"></script>
  <style>
    .glow-node {
      transition: all 0.2s ease-in-out;
    }
    .glow-node:hover {
      filter: drop-shadow(0 0 8px currentColor);
      transform: scale(1.15);
      cursor: pointer;
    }
    .edge-line {
      transition: stroke-opacity 0.2s ease, stroke-width 0.2s ease;
    }
  </style>
</head>
<body class="bg-[var(--background)] text-[var(--foreground)] min-h-full font-sans p-4 md:p-6 flex flex-col gap-6">

  <!-- Header -->
  <header class="flex flex-col md:flex-row md:items-center justify-between gap-4 border-b border-[var(--border)] pb-4">
    <div>
      <div class="flex items-center gap-3">
        <span class="px-2.5 py-0.5 rounded-full text-xs font-semibold bg-indigo-500/10 text-indigo-500 border border-indigo-500/20">SUBIT-64</span>
        <h1 class="text-xl md:text-2xl font-bold tracking-tight">Функціональна архітектура MaleCNS (Drosophila)</h1>
      </div>
      <p class="text-sm text-[var(--muted-foreground)] mt-1">
        Розклад 18,524 нейронів та 4,158,056 синапсів за рекурсивними вимірами <b>WHO &times; WHERE &times; WHEN</b>
      </p>
    </div>
    <div class="flex items-center gap-2">
      <div class="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-[var(--card)] border border-[var(--border)] text-xs">
        <span class="text-[var(--muted-foreground)]">Нейронів:</span>
        <span class="font-semibold text-emerald-500">18,524</span>
      </div>
      <div class="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-[var(--card)] border border-[var(--border)] text-xs">
        <span class="text-[var(--muted-foreground)]">Синапсів:</span>
        <span class="font-semibold text-blue-500">4.16M</span>
      </div>
      <div class="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-[var(--card)] border border-[var(--border)] text-xs">
        <span class="text-[var(--muted-foreground)]">Станів:</span>
        <span class="font-semibold text-purple-500">64</span>
      </div>
    </div>
  </header>

  <!-- Controls & Tabs -->
  <div class="flex flex-wrap items-center justify-between gap-4">
    <div class="flex items-center gap-2 p-1 bg-[var(--card)] border border-[var(--border)] rounded-xl">
      <button id="tab-flow" onclick="switchTab('flow')" class="px-3.5 py-1.5 text-xs font-medium rounded-lg transition-all bg-indigo-600 text-white shadow-sm">
        🪐 Топологічний потік (Flow Topology)
      </button>
      <button id="tab-matrix" onclick="switchTab('matrix')" class="px-3.5 py-1.5 text-xs font-medium rounded-lg transition-all text-[var(--muted-foreground)] hover:text-[var(--foreground)]">
        📊 Матриця переходів 64&times;64
      </button>
      <button id="tab-archetypes" onclick="switchTab('archetypes')" class="px-3.5 py-1.5 text-xs font-medium rounded-lg transition-all text-[var(--muted-foreground)] hover:text-[var(--foreground)]">
        🧬 Атлас макро-архетипів
      </button>
    </div>

    <!-- Edge Filter Slider (Only for Flow view) -->
    <div id="flow-controls" class="flex items-center gap-3 text-xs bg-[var(--card)] border border-[var(--border)] px-3 py-1.5 rounded-xl">
      <span class="text-[var(--muted-foreground)] whitespace-nowrap">Потужність потоку:</span>
      <input type="range" id="weight-slider" min="1" max="150" value="70" class="w-28 accent-indigo-600 cursor-pointer" oninput="updateEdgeThreshold(this.value)">
      <span id="weight-val" class="font-mono text-indigo-400 min-w-12 font-medium">Топ 70</span>
      <button onclick="resetSelection()" class="ml-2 px-2 py-0.5 rounded bg-[var(--background)] border border-[var(--border)] hover:bg-[var(--border)] text-[var(--muted-foreground)] hover:text-[var(--foreground)]">Скинути вибір</button>
    </div>
  </div>

  <!-- Legend for WHERE dimension -->
  <div class="flex flex-wrap items-center gap-4 text-xs px-3 py-2 rounded-lg bg-[var(--card)]/50 border border-[var(--border)]">
    <span class="font-semibold text-[var(--muted-foreground)] uppercase tracking-wider text-[10px]">Топологічна роль (WHERE):</span>
    <div class="flex items-center gap-1.5">
      <span class="w-3 h-3 rounded-full bg-[#38bdf8] inline-block shadow-sm"></span>
      <span>00: Периферія (Leaf)</span>
    </div>
    <div class="flex items-center gap-1.5">
      <span class="w-3 h-3 rounded-full bg-[#34d399] inline-block shadow-sm"></span>
      <span>01: Локальний кластер (Cluster)</span>
    </div>
    <div class="flex items-center gap-1.5">
      <span class="w-3 h-3 rounded-full bg-[#fbbf24] inline-block shadow-sm"></span>
      <span>10: Модулярний міст (Bridge)</span>
    </div>
    <div class="flex items-center gap-1.5">
      <span class="w-3 h-3 rounded-full bg-[#c084fc] inline-block shadow-sm"></span>
      <span>11: Центральне ядро (Core)</span>
    </div>
    <span class="text-[var(--muted-foreground)] ml-auto text-[11px] italic">Розмір кола &sim; &radic;(кількість нейронів)</span>
  </div>

  <!-- Main View Area -->
  <div class="relative grid grid-cols-1 lg:grid-cols-12 gap-6 flex-1 min-h-[640px]">

    <!-- Visual Canvas / View Area (9 cols on large screen) -->
    <div class="lg:col-span-8 xl:col-span-9 bg-[var(--card)] border border-[var(--border)] rounded-2xl p-4 flex flex-col items-center justify-center overflow-hidden relative shadow-sm">
      
      <!-- Flow Tab View -->
      <div id="view-flow" class="w-full h-full flex flex-col items-center justify-center">
        <svg id="svg-canvas" viewBox="0 0 1000 640" class="w-full h-auto max-h-[640px] select-none">
          <defs>
            <marker id="arrow" viewBox="0 0 10 10" refX="16" refY="5" markerWidth="5" markerHeight="5" orient="auto-start-reverse">
              <path d="M 0 1.5 L 8 5 L 0 8.5 z" fill="currentColor" />
            </marker>
          </defs>
          <g id="layer-grid"></g>
          <g id="layer-edges"></g>
          <g id="layer-nodes"></g>
        </svg>
      </div>

      <!-- Matrix Heatmap Tab View -->
      <div id="view-matrix" class="w-full h-full hidden flex-col items-center justify-center p-2">
        <div class="text-xs text-[var(--muted-foreground)] mb-2 text-center">
          Рядки: Джерело (Source State $S_i$) &rarr; Стовпчики: Приймач (Target State $S_j$). Логарифмічна шкала сумарної ваги синапсів.
        </div>
        <div class="overflow-auto max-w-full max-h-[580px] border border-[var(--border)] rounded-xl bg-[var(--background)] p-2">
          <canvas id="heatmap-canvas" width="640" height="640" class="cursor-crosshair"></canvas>
        </div>
      </div>

      <!-- Archetypes Tab View -->
      <div id="view-archetypes" class="w-full h-full hidden overflow-y-auto max-h-[600px] flex-col gap-4 p-2">
        <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
          
          <div class="p-4 rounded-xl bg-blue-500/5 border border-blue-500/20 flex flex-col gap-2">
            <div class="flex items-center justify-between">
              <span class="text-xs font-bold px-2 py-0.5 rounded bg-blue-500/20 text-blue-400">ПОЛЮС 1: Вхідний сенсорний</span>
              <span class="font-mono text-xs font-bold text-blue-400">2,867 нейронів (15.5%)</span>
            </div>
            <h3 class="text-base font-semibold text-[var(--foreground)]">Стани S0 [000000] та S4 [000100]</h3>
            <p class="text-xs text-[var(--muted-foreground)] leading-relaxed">
              Абсолютне домінування ранньої часової фази (WHEN=00) та сенсорного типу (WHO=00). Характеризуються високим out-degree при мінімальному in-degree. Виконують роль первинних рецепторів вентрального нервового каналу.
            </p>
          </div>

          <div class="p-4 rounded-xl bg-amber-500/5 border border-amber-500/20 flex flex-col gap-2">
            <div class="flex items-center justify-between">
              <span class="text-xs font-bold px-2 py-0.5 rounded bg-amber-500/20 text-amber-400">ПОЛЮС 2: Інтернейронні магістралі</span>
              <span class="font-mono text-xs font-bold text-amber-400">2,088 нейронів (11.3%)</span>
            </div>
            <h3 class="text-base font-semibold text-[var(--foreground)]">Стани S21 [010101] та S25 [011001]</h3>
            <p class="text-xs text-[var(--muted-foreground)] leading-relaxed">
              Релейні інтернейрони (WHO=01) проміжного транзиту (WHEN=01). З'єднують локальні сенсорні кластери з моторними центрами через модулярні мости (WHERE=10). Головні транспортні артерії рефлекторних дуг.
            </p>
          </div>

          <div class="p-4 rounded-xl bg-purple-500/5 border border-purple-500/20 flex flex-col gap-2">
            <div class="flex items-center justify-between">
              <span class="text-xs font-bold px-2 py-0.5 rounded bg-purple-500/20 text-purple-400">ПОЛЮС 3: Резонансні Аттрактори</span>
              <span class="font-mono text-xs font-bold text-purple-400">1,494 нейрони (8.1%)</span>
            </div>
            <h3 class="text-base font-semibold text-[var(--foreground)]">Стани S34 [100010], S38 [100110], S42 [101010]</h3>
            <p class="text-xs text-[var(--muted-foreground)] leading-relaxed">
              Висока взаємна реципрокність (Reciprocity > 0.4) та рекурентність (WHEN=10). Ці контури утримують динамічний стан після припинення вхідного імпульсу, слугуючи фізичним носієм короткострокової динамічної пам'яті.
            </p>
          </div>

          <div class="p-4 rounded-xl bg-emerald-500/5 border border-emerald-500/20 flex flex-col gap-2">
            <div class="flex items-center justify-between">
              <span class="text-xs font-bold px-2 py-0.5 rounded bg-emerald-500/20 text-emerald-400">ПОЛЮС 4: Моторні Виконавці</span>
              <span class="font-mono text-xs font-bold text-emerald-400">2,402 нейрони (13.0%)</span>
            </div>
            <h3 class="text-base font-semibold text-[var(--foreground)]">Стани S51 [110011] та S63 [111111]</h3>
            <p class="text-xs text-[var(--muted-foreground)] leading-relaxed">
              Термінальні стоки (WHEN=11, WHO=11). Величезний in-degree і висока внутрішня щільність (S63 має найбільшу внутрішню вагу зв'язків &gt; 1.2M). Безпосередньо керують моторними паттернами польоту та руху кінцівок.
            </p>
          </div>

        </div>

        <div class="p-4 rounded-xl bg-[var(--background)] border border-[var(--border)] mt-2">
          <h4 class="text-xs font-bold uppercase tracking-wider text-[var(--muted-foreground)] mb-2">Підтвердження гіпотези субстратної інваріантності</h4>
          <p class="text-xs text-[var(--muted-foreground)] leading-relaxed">
            Поділ на 64 класи SUBIT демонструє, що коннектом дрозофіли має чітку функціональну поляризацію: ранні стани позбавлені моторних властивостей, а термінальні центри концентрують масивні рекурентні петлі. Це дозволяє здійснювати стиснення та міжсубстратне моделювання системи не на рівні 18k ізольованих вузлів, а на рівні 64 макро-станів із збереженням інваріантної динаміки.
          </p>
        </div>
      </div>

    </div>

    <!-- Inspector / Info Panel (3 cols) -->
    <div class="lg:col-span-4 xl:col-span-3 bg-[var(--card)] border border-[var(--border)] rounded-2xl p-4 flex flex-col gap-4 shadow-sm">
      
      <div class="border-b border-[var(--border)] pb-3">
        <span class="text-[10px] uppercase tracking-wider text-[var(--muted-foreground)] font-semibold">Інспектор стану SUBIT-64</span>
        <div class="flex items-baseline justify-between mt-1">
          <h2 id="info-id" class="text-xl font-bold font-mono text-indigo-400">S63</h2>
          <span id="info-code" class="text-xs font-mono px-2 py-0.5 rounded bg-indigo-500/10 text-indigo-400 border border-indigo-500/20 font-semibold">[111111]</span>
        </div>
        <p id="info-desc" class="text-xs text-[var(--muted-foreground)] mt-1.5 font-medium leading-relaxed">
          Motor/Effector &bull; Central Core &bull; Terminal Readout
        </p>
      </div>

      <!-- State Metrics Card -->
      <div class="grid grid-cols-2 gap-2">
        <div class="p-2.5 rounded-xl bg-[var(--background)] border border-[var(--border)]">
          <span class="text-[10px] text-[var(--muted-foreground)]">Кількість нейронів</span>
          <div id="info-count" class="text-base font-bold text-[var(--foreground)] mt-0.5">1,016</div>
          <span id="info-pct" class="text-[10px] text-emerald-500 font-medium">5.49% від усіх</span>
        </div>
        <div class="p-2.5 rounded-xl bg-[var(--background)] border border-[var(--border)]">
          <span class="text-[10px] text-[var(--muted-foreground)]">Внутрішня петля</span>
          <div id="info-loop" class="text-base font-bold text-purple-400 mt-0.5">1.21M</div>
          <span class="text-[10px] text-[var(--muted-foreground)]">вага синапсів</span>
        </div>
      </div>

      <!-- Decomposition pills -->
      <div class="flex flex-col gap-2 p-3 rounded-xl bg-[var(--background)] border border-[var(--border)] text-xs">
        <div class="flex justify-between items-center">
          <span class="text-[var(--muted-foreground)]">WHO (Роль):</span>
          <span id="info-who" class="font-medium text-emerald-400">Motor/Effector [11]</span>
        </div>
        <div class="flex justify-between items-center">
          <span class="text-[var(--muted-foreground)]">WHERE (Локус):</span>
          <span id="info-where" class="font-medium text-purple-400">Central Core [11]</span>
        </div>
        <div class="flex justify-between items-center">
          <span class="text-[var(--muted-foreground)]">WHEN (Фаза):</span>
          <span id="info-when" class="font-medium text-indigo-400">Terminal Readout [11]</span>
        </div>
      </div>

      <!-- Top Connected Links -->
      <div class="flex-1 flex flex-col gap-2 min-h-[160px]">
        <span class="text-[10px] uppercase tracking-wider text-[var(--muted-foreground)] font-semibold">Головні синаптичні потоки:</span>
        <div id="info-links" class="flex flex-col gap-1.5 overflow-y-auto max-h-[180px] pr-1 text-xs">
          <!-- Dynamically populated -->
        </div>
      </div>

      <div class="text-[11px] text-[var(--muted-foreground)] bg-[var(--background)]/60 p-2.5 rounded-lg border border-[var(--border)] italic">
        💡 Натисніть на будь-який вузол для фіксації фокусу та фільтрації його потоків.
      </div>
    </div>

  </div>

  <script>
    const DATA = """ + json.dumps(data) + """;

    const WHO_LABELS = ["Sensory/Input", "Feedforward Relay", "Integrator/Hub", "Motor/Effector"];
    const WHERE_LABELS = ["Peripheral Leaf", "Local Cluster", "Modular Bridge", "Central Core"];
    const WHEN_LABELS = ["Early Cascade", "Middle Transit", "Recurrent Attractor", "Terminal Readout"];
    const WHERE_COLORS = ["#38bdf8", "#34d399", "#fbbf24", "#c084fc"];

    let selectedNodeId = 63;
    let edgeThreshold = 70;
    let nodePositions = {};

    function initLayout() {
      const svg = document.getElementById("svg-canvas");
      const gridLayer = document.getElementById("layer-grid");
      const nodeLayer = document.getElementById("layer-nodes");
      
      const width = 1000;
      const height = 640;
      const marginX = 80;
      const marginY = 60;
      const colW = (width - marginX * 2) / 3;
      const rowH = (height - marginY * 2) / 3;

      // Draw grid backgrounds and headers for WHEN and WHO
      for (let col = 0; col < 4; col++) {
        const x = marginX + col * colW;
        const text = document.createElementNS("http://www.w3.org/2000/svg", "text");
        text.setAttribute("x", x);
        text.setAttribute("y", marginY - 25);
        text.setAttribute("text-anchor", "middle");
        text.setAttribute("class", "text-[11px] font-semibold fill-[var(--muted-foreground)] uppercase tracking-wider");
        text.textContent = `WHEN ${col.toString(2).padStart(2,'0')}: ${WHEN_LABELS[col]}`;
        gridLayer.appendChild(text);

        // Column line
        if (col > 0) {
          const line = document.createElementNS("http://www.w3.org/2000/svg", "line");
          line.setAttribute("x1", x - colW/2);
          line.setAttribute("y1", marginY - 10);
          line.setAttribute("x2", x - colW/2);
          line.setAttribute("y2", height - marginY + 20);
          line.setAttribute("stroke", "currentColor");
          line.setAttribute("class", "text-[var(--border)] stroke-dasharray-[4,4]");
          line.setAttribute("stroke-width", "1");
          line.setAttribute("stroke-dasharray", "4,4");
          gridLayer.appendChild(line);
        }
      }

      for (let row = 0; row < 4; row++) {
        const y = marginY + row * rowH;
        const text = document.createElementNS("http://www.w3.org/2000/svg", "text");
        text.setAttribute("x", marginX - 15);
        text.setAttribute("y", y + 4);
        text.setAttribute("text-anchor", "end");
        text.setAttribute("class", "text-[10px] font-semibold fill-[var(--muted-foreground)] uppercase tracking-wider");
        text.textContent = `WHO ${row.toString(2).padStart(2,'0')}: ${WHO_LABELS[row]}`;
        gridLayer.appendChild(text);
      }

      // Calculate node positions
      // Sub-offset for WHERE (4 states per grid cell):
      // 0: top-left (-dx, -dy), 1: top-right (+dx, -dy), 2: bottom-left (-dx, +dy), 3: bottom-right (+dx, +dy)
      const dx = 26;
      const dy = 22;
      const subOffsets = [
        { x: -dx, y: -dy },
        { x: dx,  y: -dy },
        { x: -dx, y: dy  },
        { x: dx,  y: dy  }
      ];

      DATA.nodes.forEach(node => {
        const col = node.when;
        const row = node.who;
        const where = node.where;
        
        const baseX = marginX + col * colW;
        const baseY = marginY + row * rowH;
        const posX = baseX + subOffsets[where].x;
        const posY = baseY + subOffsets[where].y;

        nodePositions[node.id] = { x: posX, y: posY, ...node };

        // Node circle
        const radius = Math.max(5, Math.min(22, Math.sqrt(node.count) * 0.45));
        const circle = document.createElementNS("http://www.w3.org/2000/svg", "circle");
        circle.setAttribute("cx", posX);
        circle.setAttribute("cy", posY);
        circle.setAttribute("r", radius);
        circle.setAttribute("fill", WHERE_COLORS[where]);
        circle.setAttribute("fill-opacity", "0.85");
        circle.setAttribute("stroke", "#ffffff");
        circle.setAttribute("stroke-width", "1.5");
        circle.setAttribute("class", "glow-node");
        circle.setAttribute("id", `node-${node.id}`);
        circle.setAttribute("data-id", node.id);

        circle.addEventListener("mouseenter", () => highlightNode(node.id));
        circle.addEventListener("click", () => selectNode(node.id));

        nodeLayer.appendChild(circle);

        // Node text label
        if (node.count > 400) {
          const label = document.createElementNS("http://www.w3.org/2000/svg", "text");
          label.setAttribute("x", posX);
          label.setAttribute("y", posY + 3.5);
          label.setAttribute("text-anchor", "middle");
          label.setAttribute("class", "text-[9px] font-bold fill-slate-900 pointer-events-none select-none");
          label.textContent = `S${node.id}`;
          nodeLayer.appendChild(label);
        }
      });

      renderEdges();
      selectNode(selectedNodeId);
      drawHeatmap();
    }

    function renderEdges() {
      const edgeLayer = document.getElementById("layer-edges");
      edgeLayer.innerHTML = "";

      const linksToShow = DATA.links.slice(0, edgeThreshold);
      const maxW = linksToShow[0] ? linksToShow[0].weight : 1;

      linksToShow.forEach(link => {
        const src = nodePositions[link.source];
        const tgt = nodePositions[link.target];
        if (!src || !tgt) return;

        // Skip pure self-loops in main canvas to avoid clutter, or draw small circle
        if (link.source === link.target) return;

        const path = document.createElementNS("http://www.w3.org/2000/svg", "path");
        const dx = tgt.x - src.x;
        const dy = tgt.y - src.y;
        const cx = (src.x + tgt.x) / 2 - dy * 0.15;
        const cy = (src.y + tgt.y) / 2 + dx * 0.15;

        const d = `M ${src.x} ${src.y} Q ${cx} ${cy} ${tgt.x} ${tgt.y}`;
        const strokeW = Math.max(1, Math.min(6, (link.weight / maxW) * 8));

        path.setAttribute("d", d);
        path.setAttribute("fill", "none");
        path.setAttribute("stroke", "currentColor");
        path.setAttribute("class", "edge-line text-indigo-400");
        path.setAttribute("stroke-opacity", "0.25");
        path.setAttribute("stroke-width", strokeW);
        path.setAttribute("marker-end", "url(#arrow)");
        path.setAttribute("id", `edge-${link.source}-${link.target}`);

        edgeLayer.appendChild(path);
      });
    }

    function highlightNode(id) {
      if (selectedNodeId === id) return;
      previewNode(id);
    }

    function selectNode(id) {
      selectedNodeId = id;
      const node = DATA.nodes.find(n => n.id === id);
      if (!node) return;

      // Update Inspector panel
      document.getElementById("info-id").textContent = `S${node.id}`;
      document.getElementById("info-code").textContent = `[${node.code}]`;
      document.getElementById("info-desc").textContent = `${WHO_LABELS[node.who]} • ${WHERE_LABELS[node.where]} • ${WHEN_LABELS[node.when]}`;
      document.getElementById("info-count").textContent = node.count.toLocaleString();
      const pct = ((node.count / DATA.total_neurons) * 100).toFixed(2);
      document.getElementById("info-pct").textContent = `${pct}% від усього CNS`;
      document.getElementById("info-who").textContent = `${WHO_LABELS[node.who]} [${node.who.toString(2).padStart(2,'0')}]`;
      document.getElementById("info-where").textContent = `${WHERE_LABELS[node.where]} [${node.where.toString(2).padStart(2,'0')}]`;
      document.getElementById("info-when").textContent = `${WHEN_LABELS[node.when]} [${node.when.toString(2).padStart(2,'0')}]`;

      // Check self loop weight
      const selfLink = DATA.links.find(l => l.source === id && l.target === id);
      const loopW = selfLink ? Math.round(selfLink.weight).toLocaleString() : "0";
      document.getElementById("info-loop").textContent = loopW;

      // Highlight connections in canvas
      const allPaths = document.querySelectorAll(".edge-line");
      allPaths.forEach(p => {
        p.setAttribute("stroke-opacity", "0.05");
        p.classList.remove("text-emerald-400", "text-cyan-400", "text-amber-400");
        p.classList.add("text-indigo-400");
      });

      const relatedLinks = DATA.links.filter(l => l.source === id || l.target === id);
      const linksContainer = document.getElementById("info-links");
      linksContainer.innerHTML = "";

      relatedLinks.slice(0, 10).forEach(l => {
        const isOut = l.source === id;
        const otherId = isOut ? l.target : l.source;
        const otherNode = DATA.nodes.find(n => n.id === otherId);
        const edgeEl = document.getElementById(`edge-${l.source}-${l.target}`);
        
        if (edgeEl) {
          edgeEl.setAttribute("stroke-opacity", "0.85");
          edgeEl.classList.remove("text-indigo-400");
          edgeEl.classList.add(isOut ? "text-emerald-400" : "text-cyan-400");
          edgeEl.setAttribute("stroke-width", "3");
        }

        const linkRow = document.createElement("div");
        linkRow.className = "flex items-center justify-between p-1.5 rounded bg-[var(--card)] border border-[var(--border)] cursor-pointer hover:border-indigo-500";
        linkRow.onclick = () => selectNode(otherId);
        linkRow.innerHTML = `
          <div class="flex items-center gap-1.5">
            <span class="w-1.5 h-1.5 rounded-full ${isOut ? 'bg-emerald-400' : 'bg-cyan-400'}"></span>
            <span class="font-mono font-medium">${isOut ? '&rarr;' : '&larr;'} S${otherId}</span>
            <span class="text-[10px] text-[var(--muted-foreground)] truncate max-w-[100px]">${otherNode ? otherNode.code : ''}</span>
          </div>
          <span class="font-mono text-[10px] text-[var(--foreground)] font-semibold">${Math.round(l.weight).toLocaleString()}</span>
        `;
        linksContainer.appendChild(linkRow);
      });

      if (relatedLinks.length === 0) {
        linksContainer.innerHTML = `<span class="text-[var(--muted-foreground)] italic text-xs">Немає сильних зв'язків у вибірці</span>`;
      }

      // Highlight selected circle
      document.querySelectorAll(".glow-node").forEach(c => {
        c.setAttribute("stroke", "#ffffff");
        c.setAttribute("stroke-width", "1.5");
      });
      const activeCircle = document.getElementById(`node-${id}`);
      if (activeCircle) {
        activeCircle.setAttribute("stroke", "#f43f5e");
        activeCircle.setAttribute("stroke-width", "3.5");
      }
    }

    function previewNode(id) {
      const node = DATA.nodes.find(n => n.id === id);
      if (!node) return;
      document.getElementById("info-id").textContent = `S${node.id}`;
      document.getElementById("info-code").textContent = `[${node.code}]`;
      document.getElementById("info-desc").textContent = `${WHO_LABELS[node.who]} • ${WHERE_LABELS[node.where]} • ${WHEN_LABELS[node.when]}`;
      document.getElementById("info-count").textContent = node.count.toLocaleString();
    }

    function resetSelection() {
      selectNode(63);
    }

    function updateEdgeThreshold(val) {
      edgeThreshold = parseInt(val);
      document.getElementById("weight-val").textContent = `Топ ${val}`;
      renderEdges();
      selectNode(selectedNodeId);
    }

    function switchTab(tab) {
      document.getElementById("view-flow").classList.add("hidden");
      document.getElementById("view-matrix").classList.add("hidden");
      document.getElementById("view-archetypes").classList.add("hidden");
      document.getElementById("flow-controls").classList.add("hidden");

      document.getElementById("tab-flow").className = "px-3.5 py-1.5 text-xs font-medium rounded-lg transition-all text-[var(--muted-foreground)] hover:text-[var(--foreground)]";
      document.getElementById("tab-matrix").className = "px-3.5 py-1.5 text-xs font-medium rounded-lg transition-all text-[var(--muted-foreground)] hover:text-[var(--foreground)]";
      document.getElementById("tab-archetypes").className = "px-3.5 py-1.5 text-xs font-medium rounded-lg transition-all text-[var(--muted-foreground)] hover:text-[var(--foreground)]";

      if (tab === 'flow') {
        document.getElementById("view-flow").classList.remove("hidden");
        document.getElementById("flow-controls").classList.remove("hidden");
        document.getElementById("tab-flow").className = "px-3.5 py-1.5 text-xs font-medium rounded-lg transition-all bg-indigo-600 text-white shadow-sm";
      } else if (tab === 'matrix') {
        document.getElementById("view-matrix").classList.remove("hidden");
        document.getElementById("tab-matrix").className = "px-3.5 py-1.5 text-xs font-medium rounded-lg transition-all bg-indigo-600 text-white shadow-sm";
        drawHeatmap();
      } else if (tab === 'archetypes') {
        document.getElementById("view-archetypes").classList.remove("hidden");
        document.getElementById("tab-archetypes").className = "px-3.5 py-1.5 text-xs font-medium rounded-lg transition-all bg-indigo-600 text-white shadow-sm";
      }
    }

    function drawHeatmap() {
      const canvas = document.getElementById("heatmap-canvas");
      if (!canvas) return;
      const ctx = canvas.getContext("2d");
      const size = 640;
      const cellSize = size / 64;

      // Matrix 64x64
      const matrix = Array.from({length: 64}, () => Array(64).fill(0));
      let maxVal = 1;
      DATA.links.forEach(l => {
        if (l.source < 64 && l.target < 64) {
          matrix[l.source][l.target] = l.weight;
          if (l.weight > maxVal) maxVal = l.weight;
        }
      });

      ctx.clearRect(0, 0, size, size);

      for (let r = 0; r < 64; r++) {
        for (let c = 0; c < 64; c++) {
          const val = matrix[r][c];
          if (val > 0) {
            const intensity = Math.min(1, Math.log10(val + 1) / Math.log10(maxVal + 1));
            // Color scale: violet to cyan to yellow
            ctx.fillStyle = `rgba(168, 85, 247, ${Math.max(0.15, intensity)})`;
            if (intensity > 0.7) {
              ctx.fillStyle = `rgba(251, 191, 36, ${intensity})`;
            }
          } else {
            ctx.fillStyle = (r + c) % 2 === 0 ? "rgba(255,255,255,0.02)" : "rgba(0,0,0,0.05)";
          }
          ctx.fillRect(c * cellSize, r * cellSize, cellSize - 0.5, cellSize - 0.5);
        }
      }
    }

    window.addEventListener("DOMContentLoaded", initLayout);
  </script>
</body>
</html>"""

local_html = os.path.normpath(os.path.join(os.path.dirname(__file__), "subit_connectome_viz.html"))
with open(local_html, "w", encoding="utf-8") as f:
    f.write(html_template)

artifact_dir = r"C:\Users\sciga\.gemini\antigravity\brain\1db5efb7-9cc3-4eb0-a545-6d4e36b25d75"
if os.path.exists(artifact_dir):
    artifact_html = os.path.join(artifact_dir, "subit_connectome_viz.html")
    with open(artifact_html, "w", encoding="utf-8") as f:
        f.write(html_template)

print(f"Generated HTML successfully: {local_html}")
