/* NexaFusion "Liquid light" UI layer: intent command bar (Ctrl/⌘ K) and spatial card tilt.
   Loaded on every page. No network calls, no storage. */
(() => {
  const reduce = matchMedia("(prefers-reduced-motion: reduce)").matches;
  const finePointer = matchMedia("(pointer: fine)").matches;

  /* ---------- Spatial tilt + light ---------- */
  if (!reduce && finePointer) {
    document.querySelectorAll(".card, .post, .mini, .principle").forEach((el) => {
      el.classList.add("tilt");
      el.addEventListener("pointermove", (e) => {
        const r = el.getBoundingClientRect();
        const x = (e.clientX - r.left) / r.width, y = (e.clientY - r.top) / r.height;
        el.style.setProperty("--rx", ((0.5 - y) * 5).toFixed(2) + "deg");
        el.style.setProperty("--ry", ((x - 0.5) * 6).toFixed(2) + "deg");
        el.style.setProperty("--mx", (x * 100).toFixed(1) + "%");
        el.style.setProperty("--my", (y * 100).toFixed(1) + "%");
      });
      el.addEventListener("pointerleave", () => { el.style.setProperty("--rx", "0deg"); el.style.setProperty("--ry", "0deg"); });
    });
  }

  /* ---------- Intent command bar ---------- */
  const ITEMS = [
    { t: "CRA readiness check", d: "Free 3-minute self-assessment", u: "/cra-readiness/", k: "cra cyber resilience act eu compliance regulation readiness check score enisa reporting sbom" },
    { t: "EU CRA readiness", d: "Service", u: "/services/cra-readiness/", k: "cra compliance gap analysis documentation conformity ce marking 2027" },
    { t: "Cyber security & resilience", d: "Service", u: "/services/cyber-security/", k: "security secure threat model pen test fuzzing supply chain sbom vulnerability sdlc" },
    { t: "AI compilers & inference performance", d: "Service", u: "/services/ai-compilers/", k: "ai compiler mlir llvm triton cuda kernel gpu slow model inference latency cost quantisation accelerator hardware" },
    { t: "Rust & C++ systems", d: "Service", u: "/services/rust-cpp/", k: "rust c++ cpp memory safety legacy modernise rewrite ffi" },
    { t: "AI & agent engineering", d: "Service", u: "/services/ai-agents/", k: "ai agents llm rag evals mcp chatbot product guardrails" },
    { t: "Cloud, platform & delivery", d: "Service", u: "/services/cloud-platform/", k: "cloud aws azure gcp kubernetes terraform ci cd devops cost finops" },
    { t: "Fractional CTO & due diligence", d: "Service", u: "/services/fractional-cto/", k: "cto leadership architecture due diligence investor roadmap hiring" },
    { t: "The EU Cyber Resilience Act: what UK firms need to know", d: "Insight", u: "/insights/eu-cyber-resilience-act/", k: "cra article uk brexit timeline reporting 24 72 hours" },
    { t: "Why your inference bill is a compiler problem", d: "Insight", u: "/insights/inference-cost-compilers/", k: "inference cost gpu bandwidth fusion flashattention article" },
    { t: "Memory-safety roadmaps: Rust without the rewrite", d: "Insight", u: "/insights/memory-safety-roadmaps/", k: "memory safety roadmap cisa rust article" },
    { t: "All insights", d: "Articles", u: "/insights/", k: "blog articles insights writing" },
    { t: "Diagnose my problem", d: "Interactive", u: "/#diagnose", k: "diagnose problem help plan" },
    { t: "How we work", d: "Approach", u: "/#approach", k: "approach process engagement how weeks" },
    { t: "FAQ", d: "Questions", u: "/#faq", k: "faq questions ip ownership team" },
    { t: "Email us", d: "hello@nexafusion.io", u: "mailto:hello@nexafusion.io", k: "contact email talk hire quote call" },
  ];

  const dlg = document.createElement("dialog");
  dlg.className = "kbar";
  dlg.setAttribute("aria-label", "Search and jump");
  dlg.innerHTML = `
    <div class="kbar-box">
      <div class="kbar-input">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" aria-hidden="true"><circle cx="11" cy="11" r="7"/><path d="M20 20l-3.5-3.5"/></svg>
        <input type="text" role="combobox" aria-expanded="true" aria-controls="kbar-list" aria-autocomplete="list" placeholder="What do you need? e.g. “CRA”, “slow model”, “Rust”" autocomplete="off" spellcheck="false" />
        <kbd>Esc</kbd>
      </div>
      <ul id="kbar-list" class="kbar-list" role="listbox"></ul>
      <p class="kbar-foot"><span>↑↓ to move · Enter to open</span><span>NexaFusion</span></p>
    </div>`;
  document.body.appendChild(dlg);
  const input = dlg.querySelector("input"), list = dlg.querySelector("ul");
  let results = [], active = 0;

  const score = (it, q) => {
    if (!q) return 1;
    const words = q.toLowerCase().split(/\s+/).filter(Boolean);
    const hay = (it.t + " " + it.k).toLowerCase();
    let s = 0;
    for (const w of words) {
      if (it.t.toLowerCase().startsWith(w)) s += 5;
      else if (hay.includes(" " + w) || hay.startsWith(w)) s += 3;
      else if (hay.includes(w)) s += 1;
      else return 0;
    }
    return s;
  };
  const esc = (s) => s.replace(/[&<>]/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;" }[c]));
  const render = () => {
    const q = input.value.trim();
    results = ITEMS.map((it) => [score(it, q), it]).filter(([s]) => s > 0).sort((a, b) => b[0] - a[0]).map(([, it]) => it);
    active = Math.min(active, Math.max(0, results.length - 1));
    list.innerHTML = results.length
      ? results.map((it, i) => `<li id="kbar-${i}" role="option" aria-selected="${i === active}"><a href="${it.u}" tabindex="-1"><b>${esc(it.t)}</b><span>${esc(it.d)}</span></a></li>`).join("")
      : `<li class="kbar-empty">No match — try “security”, “CRA” or “compiler”, or <a href="mailto:hello@nexafusion.io">email us</a>.</li>`;
    input.setAttribute("aria-activedescendant", results.length ? "kbar-" + active : "");
  };
  const open = () => { if (dlg.open) return; input.value = ""; active = 0; render(); dlg.showModal(); input.focus(); };
  const go = (i) => { const it = results[i]; if (!it) return; dlg.close(); location.href = it.u; };

  input.addEventListener("input", () => { active = 0; render(); });
  input.addEventListener("keydown", (e) => {
    if (e.key === "ArrowDown") { e.preventDefault(); active = (active + 1) % Math.max(1, results.length); render(); list.children[active]?.scrollIntoView({ block: "nearest" }); }
    else if (e.key === "ArrowUp") { e.preventDefault(); active = (active - 1 + results.length) % Math.max(1, results.length); render(); list.children[active]?.scrollIntoView({ block: "nearest" }); }
    else if (e.key === "Enter") { e.preventDefault(); go(active); }
  });
  list.addEventListener("click", (e) => { const li = e.target.closest("li[role=option]"); if (li) { e.preventDefault(); go([...list.children].indexOf(li)); } });
  dlg.addEventListener("click", (e) => { if (e.target === dlg) dlg.close(); });

  addEventListener("keydown", (e) => {
    if ((e.key === "k" || e.key === "K") && (e.metaKey || e.ctrlKey)) { e.preventDefault(); dlg.open ? dlg.close() : open(); }
    else if (e.key === "/" && !dlg.open && !/^(INPUT|TEXTAREA|SELECT)$/.test(document.activeElement.tagName)) { e.preventDefault(); open(); }
  });
  document.querySelectorAll("[data-kbar]").forEach((b) => b.addEventListener("click", open));
  const mac = /Mac|iPhone|iPad/.test(navigator.platform || navigator.userAgent);
  document.querySelectorAll(".kbar-hint").forEach((h) => { h.textContent = mac ? "⌘K" : "Ctrl K"; });
})();
