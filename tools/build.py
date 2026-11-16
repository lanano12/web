#!/usr/bin/env python3
"""Generate NexaFusion's inner pages (services, insights) and sitemap.xml.

The homepage (index.html) is hand-written. Everything else is generated from
the content below so the header, footer, metadata and styling stay consistent.

    python3 tools/build.py

Edit the SERVICES / ARTICLES data, re-run, commit the output.
"""
from __future__ import annotations

import html
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SITE = "https://www.nexafusion.io"
EMAIL = "hello@nexafusion.io"  # TODO: replace with a real, monitored mailbox
TODAY = "2026-11-16"

CSP = ("default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline'; "
       "img-src 'self' data:; font-src 'self'; connect-src 'self'; object-src 'none'; "
       "base-uri 'self'; form-action 'self'")

ARROW = ('<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.4" '
         'stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M5 12h14M13 6l6 6-6 6"/></svg>')

LOGO = '''<svg viewBox="0 0 64 64" aria-hidden="true">
        <defs><linearGradient id="lg" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#5ef2ff"/><stop offset=".55" stop-color="#a37bff"/><stop offset="1" stop-color="#ff5cc8"/></linearGradient></defs>
        <rect x="2" y="2" width="60" height="60" rx="16" fill="none" stroke="url(#lg)" stroke-width="3" opacity=".5"/>
        <path d="M20 44V20l24 24V20" fill="none" stroke="url(#lg)" stroke-width="5.5" stroke-linecap="round" stroke-linejoin="round"/>
      </svg>'''

# --------------------------------------------------------------------------
# Content
# --------------------------------------------------------------------------

SERVICES = [
    {
        "slug": "ai-agents",
        "name": "AI & agent engineering",
        "title": "AI & agent engineering that survives production",
        "lede": "Agents and LLM features that call your real systems — with evaluation, guardrails, observability and cost control designed in from the first commit.",
        "fit": [
            "You have an AI prototype that impresses in demos but you don’t trust it with customers.",
            "You want agents that act on internal tools and data, safely.",
            "Your LLM bill or latency is growing faster than usage.",
        ],
        "what": [
            ("Use-case triage", "Rank candidate features by value, risk and data readiness, and drop the weak ones early."),
            ("Evaluation harnesses", "Define what “good” means, build test sets and automated evals, and gate releases on them."),
            ("Tools, retrieval & MCP", "Typed tool interfaces, retrieval over your own data and Model Context Protocol servers."),
            ("Guardrails & security", "Permissioning, prompt-injection defences, red-teaming and human-in-the-loop where it matters."),
            ("LLMOps", "Tracing, cost budgets, model routing and staged rollouts behind feature flags."),
            ("Team enablement", "Patterns and reviews so your engineers can build the next feature without us."),
        ],
        "deliver": ["Prioritised use-case map", "Evaluation suite wired into CI", "Production agent or feature behind a flag", "Runbooks and cost dashboard"],
        "tags": ["Tool use / MCP", "RAG", "Evals", "LLMOps", "Guardrails"],
        "related": ["inference-cost-compilers"],
    },
    {
        "slug": "rust-cpp",
        "name": "Rust & C++ systems",
        "title": "Memory-safe Rust & C++ — without the big-bang rewrite",
        "lede": "New components in Rust, existing C and C++ hardened and modernised, and a memory-safety roadmap your customers and auditors can read.",
        "fit": [
            "You maintain a large C or C++ codebase that is hard to change safely.",
            "Customers or regulators are asking about memory safety.",
            "You want to introduce Rust but don’t know where to start.",
        ],
        "what": [
            ("Memory-safety roadmap", "Inventory, risk-rank components by exposure and publish a credible, staged plan."),
            ("Modern C++ hardening", "Current toolchains, sanitisers, hardened standard-library modes, static analysis and fuzzing in CI."),
            ("Rust adoption", "Pick the right first component, design the FFI boundary and set up build, test and review."),
            ("Interop done properly", "Safe wrappers with cxx or bindgen, clear ownership rules and no undefined behaviour at the seams."),
            ("Characterisation tests", "Pin today’s behaviour so modernisation never changes results by accident."),
            ("Performance", "Profile before and after so safety never quietly costs you latency."),
        ],
        "deliver": ["Published memory-safety roadmap", "Hardened CI with sanitisers and fuzzing", "First Rust component in production", "Interop and coding guidelines"],
        "tags": ["Rust", "C++23", "FFI / interop", "Sanitisers", "Fuzzing"],
        "related": ["memory-safety-roadmaps"],
    },
    {
        "slug": "cyber-security",
        "name": "Cyber security & resilience",
        "title": "Secure by design — and able to prove it",
        "lede": "Threat modelling, supply-chain security and secure-development practice that engineers actually follow, plus the evidence customers and regulators now expect.",
        "fit": [
            "You sell software or connected products into the EU and need to prepare for the Cyber Resilience Act.",
            "Enterprise customers send security questionnaires you struggle to answer.",
            "A pen test found issues and you want them fixed at the root, not patched.",
        ],
        "what": [
            ("Threat modelling", "Map assets, attack surfaces and abuse cases with your engineers, not just for them."),
            ("Supply-chain security", "SBOMs, dependency policy, signed builds and provenance for what you ship."),
            ("Secure SDLC", "Code review checklists, secrets handling, SAST and fuzzing that fit your delivery flow."),
            ("Vulnerability handling", "Intake, triage, disclosure and patch processes — including CRA reporting readiness."),
            ("Remediation", "Fix the findings that matter, in code, with tests so they stay fixed."),
            ("Evidence", "Technical documentation and records that stand up to customer and regulatory scrutiny."),
        ],
        "deliver": ["Threat model and risk register", "SBOM pipeline", "Vulnerability-handling process", "CRA gap analysis and plan"],
        "tags": ["Threat modelling", "SBOM", "Fuzzing", "EU CRA", "Secure SDLC"],
        "related": ["eu-cyber-resilience-act", "memory-safety-roadmaps"],
    },
    {
        "slug": "ai-compilers",
        "name": "AI compilers & performance",
        "title": "Faster models, smaller bills",
        "lede": "Compiler passes, custom kernels and profiling from the model graph down to the silicon — so inference and training run faster on the hardware you already pay for.",
        "fit": [
            "Inference latency or GPU cost is limiting what you can ship.",
            "You are bringing models to new or custom accelerators.",
            "Hot paths in your native code need serious performance work.",
        ],
        "what": [
            ("Profiling & roofline analysis", "Trace from framework to kernel to find whether you are compute-, memory- or launch-bound."),
            ("Graph compilation", "Fusion, layout and quantisation passes with torch.compile, XLA or MLIR-based stacks."),
            ("Custom kernels", "Triton or CUDA kernels for the operations that dominate your profile."),
            ("Serving optimisation", "Batching, KV-cache management and speculative decoding for LLM inference."),
            ("Accelerator bring-up", "MLIR / LLVM lowering for new hardware targets."),
            ("Regression guards", "Benchmarks and performance budgets in CI so gains don’t quietly erode."),
        ],
        "deliver": ["Profile report with ranked opportunities", "Optimised kernels or compiler passes", "Before/after benchmarks", "CI performance budgets"],
        "tags": ["MLIR", "LLVM", "Triton", "CUDA", "Profiling"],
        "related": ["inference-cost-compilers"],
    },
    {
        "slug": "cloud-platform",
        "name": "Cloud, platform & delivery",
        "title": "Platforms that don’t page you at 3am",
        "lede": "Infrastructure as code, paved roads for developers, fast and boring releases, and a cloud bill you can explain to finance.",
        "fit": [
            "Deploying is slow or scary, so you deploy less often.",
            "Nobody can explain the cloud bill.",
            "Environments drift and incidents take too long to diagnose.",
        ],
        "what": [
            ("Infrastructure as code", "Terraform or Pulumi with reviewable, reproducible environments."),
            ("CI/CD", "Parallel, cached pipelines with progressive delivery and automatic rollback."),
            ("Observability", "OpenTelemetry tracing, useful dashboards and alerts that mean something."),
            ("FinOps", "Cost attribution by team and feature, right-sizing and budgets enforced in code."),
            ("Kubernetes & runtime", "Only where it earns its keep — and simpler options where it doesn’t."),
            ("Developer experience", "Templates and golden paths so new services start production-ready."),
        ],
        "deliver": ["IaC for all environments", "Pipeline with progressive delivery", "Observability baseline", "Cost dashboard and budgets"],
        "tags": ["Terraform", "Kubernetes", "CI/CD", "OpenTelemetry", "FinOps"],
        "related": [],
    },
    {
        "slug": "fractional-cto",
        "name": "Fractional CTO & due diligence",
        "title": "Technical leadership, on tap",
        "lede": "Experienced technical judgement without a full-time hire: architecture, roadmaps, hiring and investor-grade technical due diligence.",
        "fit": [
            "You are a founder or CEO without a technical co-founder.",
            "Your team needs an outside view on architecture or delivery.",
            "You are investing in or acquiring a software business.",
        ],
        "what": [
            ("Architecture review", "A candid read of where you are, where the risks are and what to do first."),
            ("Technology roadmap", "A plan the board understands and the team believes in."),
            ("Hiring", "Role design, interview loops and help assessing candidates."),
            ("Technical due diligence", "Code, architecture, security, team and scalability — with clear findings for investors."),
            ("AI strategy", "Where AI genuinely helps your product and operations, and where it doesn’t."),
            ("Ongoing advisory", "Regular sessions with engineering and leadership as things move."),
        ],
        "deliver": ["Architecture assessment", "12-month technology roadmap", "Due-diligence report", "Hiring plan"],
        "tags": ["Architecture", "Tech DD", "Roadmaps", "Hiring"],
        "related": [],
    },
]

ARTICLES = [
    {
        "slug": "memory-safety-roadmaps",
        "title": "Memory-safety roadmaps: Rust without the rewrite",
        "desc": "Why memory safety moved from a security talking point to a customer question, and how to build a roadmap that pairs hardened C++ with targeted Rust.",
        "topic": "Rust & C++",
        "read": "7 min read",
        "service": "rust-cpp",
        "body": """
<p>For years, memory safety was something security teams worried about and product teams didn’t. That has changed. Government security agencies across the Five Eyes now recommend memory-safe languages, and US guidance from CISA and the FBI asked software manufacturers to publish a <strong>memory-safety roadmap</strong> for existing products by 1 January 2026. That guidance is not law — but customers, insurers and procurement teams increasingly ask the question, and “we’re thinking about it” is no longer a good answer.</p>

<h2>Why it matters</h2>
<p>Memory-safety bugs — buffer overflows, use-after-free, out-of-bounds reads — have historically accounted for a large share of serious vulnerabilities in C and C++ software. Both Microsoft and the Chromium project have reported figures around 70% for their severe security bugs.</p>
<p>The most useful data point for planning, though, comes from Android. Google reported that memory-safety vulnerabilities fell from <strong>76% of Android vulnerabilities in 2019 to 24% in 2024</strong> — not by rewriting old code, but by writing <em>new</em> code in memory-safe languages. Vulnerabilities concentrate in new and recently changed code; old code that has been exercised for years gets safer over time.</p>
<blockquote>The lesson: you don’t need to rewrite everything. You need to stop adding new memory-unsafe code in the places that matter, and harden what stays.</blockquote>

<h2>What a credible roadmap contains</h2>
<ol>
  <li><strong>An inventory ranked by exposure.</strong> Parsers, network-facing services and anything handling untrusted input come first. Internal batch tools come last.</li>
  <li><strong>A policy for new code.</strong> Which components must be written in a memory-safe language from now on, and what counts as an exception.</li>
  <li><strong>Hardening for code that stays in C/C++.</strong> The roadmap should say how existing code gets safer, not just how it eventually gets replaced.</li>
  <li><strong>Milestones and metrics.</strong> For example: share of new code in memory-safe languages, number of components behind safe interfaces, memory-safety bugs found per quarter.</li>
  <li><strong>Ownership.</strong> Named owners and a review date. A roadmap nobody owns is a press release.</li>
</ol>

<h2>Hardening the C++ you keep</h2>
<p>Most organisations will run significant C++ for a decade or more, so this part pays off immediately:</p>
<ul>
  <li>Move to a current compiler and standard, and turn on warnings as errors for new code.</li>
  <li>Run <strong>AddressSanitizer and UndefinedBehaviorSanitizer</strong> in CI test runs.</li>
  <li>Add <strong>coverage-guided fuzzing</strong> (libFuzzer, AFL++) to every parser and protocol handler.</li>
  <li>Enable hardened standard-library modes and compiler hardening flags in release builds.</li>
  <li>Adopt bounds-checked access and modern ownership idioms in code review guidelines.</li>
</ul>

<h2>Introducing Rust where it pays</h2>
<p>The best first Rust component is usually small, exposed and well-specified — a file-format parser, a protocol decoder, a sandboxed plugin. It should have clear inputs and outputs, so the C++/Rust boundary stays narrow.</p>
<p>Get the interop right early. Tools like <code>cxx</code> and <code>bindgen</code> make the boundary explicit; the important work is deciding who owns memory on each side and keeping <code>unsafe</code> code small, reviewed and tested. Measure performance before and after — Rust is typically competitive with C++, but you want evidence, not assumptions.</p>

<h2>A realistic first quarter</h2>
<table>
  <thead><tr><th>Weeks</th><th>Outcome</th></tr></thead>
  <tbody>
    <tr><td>1–2</td><td>Inventory, exposure ranking, draft roadmap</td></tr>
    <tr><td>3–6</td><td>Sanitisers and fuzzing in CI; first bugs found and fixed</td></tr>
    <tr><td>6–10</td><td>First Rust component behind a safe interface, in production behind a flag</td></tr>
    <tr><td>10–12</td><td>Roadmap published with metrics and owners</td></tr>
  </tbody>
</table>
<p>That is enough to answer the customer question honestly — and to start measurably reducing risk.</p>
""",
    },
    {
        "slug": "eu-cyber-resilience-act",
        "title": "The EU Cyber Resilience Act: what UK software firms need to know",
        "desc": "Reporting duties started in September 2026 and the main obligations follow in December 2027. A practical guide for UK companies selling software into the EU.",
        "topic": "Cyber security",
        "read": "8 min read",
        "service": "cyber-security",
        "body": """
<p>The EU Cyber Resilience Act (CRA) is the first horizontal cyber-security law for products in the EU. It covers hardware and software “products with digital elements” — and it applies to UK companies too, if they place those products on the EU market. Brexit doesn’t change that.</p>

<h2>The timeline</h2>
<table>
  <thead><tr><th>Date</th><th>What happens</th></tr></thead>
  <tbody>
    <tr><td>10 Dec 2024</td><td>The CRA (Regulation (EU) 2024/2847) entered into force.</td></tr>
    <tr><td>11 Sep 2026</td><td>Reporting obligations apply: actively exploited vulnerabilities and severe incidents must be reported — including for products already on the market.</td></tr>
    <tr><td>11 Dec 2027</td><td>The main obligations apply: essential security requirements, conformity assessment, CE marking and documentation.</td></tr>
  </tbody>
</table>

<h2>Reporting: already in force</h2>
<p>Since 11 September 2026, manufacturers must notify actively exploited vulnerabilities and severe incidents affecting their products through the single reporting platform operated by ENISA. The structure is staged:</p>
<ul>
  <li><strong>Early warning</strong> within 24 hours of becoming aware.</li>
  <li><strong>Notification</strong> with more detail within 72 hours.</li>
  <li><strong>Final report</strong> within 14 days of a corrective measure being available for a vulnerability, or within one month for an incident.</li>
</ul>
<p>If you don’t yet have a way to receive vulnerability reports, triage them quickly and know who makes the call to notify, that is the first gap to close.</p>

<h2>What December 2027 brings</h2>
<ul>
  <li><strong>Security by design and by default</strong> — products must meet essential requirements, ship without known exploitable vulnerabilities and with secure default configurations.</li>
  <li><strong>Vulnerability handling</strong> for the support period, including security updates and a coordinated disclosure policy.</li>
  <li><strong>A software bill of materials (SBOM)</strong> in a machine-readable format, covering at least top-level dependencies.</li>
  <li><strong>Technical documentation and conformity assessment</strong> — self-assessment for most products, stricter routes for “important” and “critical” categories.</li>
  <li><strong>CE marking</strong> for compliant products.</li>
</ul>
<p>Penalties for breaching the essential requirements can reach €15 million or 2.5% of worldwide annual turnover, whichever is higher.</p>

<h2>Is my product in scope?</h2>
<p>Broadly: if you sell software or connected hardware to EU customers commercially, assume yes until you have checked. Some sectors with their own regimes (such as medical devices and vehicles) are excluded. Pure software-as-a-service is generally covered by other EU rules rather than the CRA, but remote data processing that a product needs in order to function can bring backend services into scope. Non-commercial open source is outside the regime, with a lighter set of duties for open-source stewards.</p>

<h2>And in the UK?</h2>
<p>UK firms face parallel developments: the Product Security and Telecommunications Infrastructure (PSTI) regime already applies to consumer connectable products, and the Cyber Security and Resilience Bill is extending incident-reporting duties for operators and key suppliers. If you sell into both markets, design one secure-development and vulnerability-handling process that satisfies both.</p>

<h2>A practical checklist</h2>
<ol>
  <li>List every product and version you place on the EU market.</li>
  <li>Stand up a vulnerability intake (a <code>security.txt</code> file and a monitored mailbox are a good start) and a 24-hour triage path.</li>
  <li>Generate SBOMs in your build pipeline.</li>
  <li>Threat-model your main products and record the decisions.</li>
  <li>Define a support period and an update process for each product.</li>
  <li>Run a gap analysis against the essential requirements and plan the work to December 2027.</li>
</ol>
<p class="note">This article is general guidance, not legal advice. Check the regulation and take legal advice for your specific products.</p>
""",
    },
    {
        "slug": "inference-cost-compilers",
        "title": "Why your inference bill is a compiler problem",
        "desc": "LLM inference is usually limited by memory bandwidth, not raw compute. That makes fusion, quantisation and kernel work the biggest levers on cost and latency.",
        "topic": "AI compilers",
        "read": "6 min read",
        "service": "ai-compilers",
        "body": """
<p>When an AI feature gets expensive, the first instinct is to look at the model: use a smaller one, or a cheaper provider. Sometimes that is right. But if you run models yourself, a large share of the cost is often in <em>how</em> the model runs — and that is a compiler and kernel problem.</p>

<h2>Bytes, not FLOPs</h2>
<p>Generating text with a large language model happens one token at a time. For each new token, the model’s weights have to be read from GPU memory. At small batch sizes, the arithmetic per byte read is low, so the GPU spends much of its time waiting on memory rather than computing. In roofline terms, decoding is usually <strong>memory-bandwidth bound</strong>.</p>
<p>That changes what “optimisation” means. Making the maths faster doesn’t help much. Moving fewer bytes does.</p>

<h2>The levers that matter</h2>
<h3>Batching</h3>
<p>Serving many requests together reuses each weight read across more tokens. Continuous batching — adding and removing requests from a running batch — is now standard in serious serving stacks.</p>
<h3>Quantisation</h3>
<p>Storing weights in 8-bit or 4-bit formats instead of 16-bit cuts the bytes moved per token. Done carefully, with evaluation, quality loss can be small. Done carelessly, it quietly degrades your product — which is why evals come first.</p>
<h3>Kernel fusion</h3>
<p>Every time an intermediate result is written to GPU memory and read back, you pay for bandwidth. Fusing operations keeps data in fast on-chip memory. FlashAttention is the best-known example: it computes attention without ever materialising the full attention matrix in GPU memory.</p>
<h3>KV-cache management</h3>
<p>The attention cache grows with context length and concurrency. Paging and sharing it efficiently lets you serve more users per GPU.</p>
<h3>Speculative decoding</h3>
<p>A small draft model proposes several tokens and the large model verifies them in one pass, turning sequential work into parallel work.</p>

<h2>Where compilers come in</h2>
<p>Modern ML compilers automate much of this. <code>torch.compile</code>, XLA and MLIR-based stacks capture the model graph, fuse operations and choose memory layouts. <strong>MLIR</strong> lets compilers lower a model step by step through dialects — from high-level tensor operations down to hardware instructions — which is also how new accelerators get supported. <strong>Triton</strong> lets engineers write custom GPU kernels at the level of tiles rather than threads, for the hot operations a general compiler doesn’t handle well.</p>

<h2>A sane process</h2>
<ol>
  <li><strong>Measure the right thing:</strong> cost per thousand tokens and p95 latency at realistic load — not a single-request benchmark.</li>
  <li><strong>Profile:</strong> framework profilers and Nsight Systems / Nsight Compute show where time goes, kernel by kernel.</li>
  <li><strong>Classify:</strong> compute-bound, memory-bound or launch-overhead-bound? Each needs a different fix.</li>
  <li><strong>Fix the top items:</strong> serving configuration first, then compilation, then custom kernels for what remains.</li>
  <li><strong>Guard the gains:</strong> benchmarks in CI so the next model or library upgrade doesn’t erase them.</li>
</ol>
<p>Teams that work this way often find substantial savings on the same hardware — and they understand why, which means the savings last.</p>
""",
    },
]

NAV = [("/#services", "Services"), ("/#diagnose", "Diagnose"), ("/#approach", "Approach"), ("/insights/", "Insights"), ("/#contact", "Contact")]

# --------------------------------------------------------------------------
# Templates
# --------------------------------------------------------------------------

e = html.escape
ACTIVE = ' class="active" aria-current="page"'


def page(*, path: str, title: str, desc: str, body: str, active: str = "", ld: list | None = None, og_type: str = "website") -> str:
    url = SITE + path
    nav = "".join(
        f'<a href="{href}"{ACTIVE if label == active else ""}>{label}</a>'
        for href, label in NAV
    )
    ld_html = "".join(
        f'\n  <script type="application/ld+json">{json.dumps(x, ensure_ascii=False)}</script>' for x in (ld or [])
    )
    return f'''<!DOCTYPE html>
<html lang="en-GB">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover" />
  <meta http-equiv="Content-Security-Policy" content="{CSP}" />
  <meta name="referrer" content="strict-origin-when-cross-origin" />
  <title>{e(title)} · NexaFusion</title>
  <meta name="description" content="{e(desc)}" />
  <link rel="canonical" href="{url}" />
  <meta name="theme-color" content="#05060b" />
  <meta name="color-scheme" content="dark light" />
  <meta property="og:type" content="{og_type}" />
  <meta property="og:site_name" content="NexaFusion" />
  <meta property="og:locale" content="en_GB" />
  <meta property="og:url" content="{url}" />
  <meta property="og:title" content="{e(title)}" />
  <meta property="og:description" content="{e(desc)}" />
  <meta property="og:image" content="{SITE}/og.png" />
  <meta property="og:image:width" content="1200" />
  <meta property="og:image:height" content="630" />
  <meta name="twitter:card" content="summary_large_image" />
  <meta name="twitter:image" content="{SITE}/og.png" />
  <link rel="icon" href="/favicon.svg" type="image/svg+xml" />
  <link rel="apple-touch-icon" href="/apple-touch-icon.png" />
  <link rel="manifest" href="/site.webmanifest" />
  <link rel="alternate" type="application/rss+xml" title="NexaFusion Insights" href="/insights/feed.xml" />
  <link rel="preload" href="/fonts/sora.woff2" as="font" type="font/woff2" crossorigin />
  <link rel="stylesheet" href="/assets/site.css" />
  <script src="/assets/theme-init.js"></script>
  <script src="/assets/site.js" defer></script>{ld_html}
</head>
<body>
  <a class="skip" href="#main">Skip to content</a>
  <div class="ambient" aria-hidden="true"><div class="aurora a"></div><div class="aurora b"></div></div>

  <header class="top" id="top">
    <a class="logo" href="/" aria-label="NexaFusion home">
      {LOGO}
      <span>Nexa<b>Fusion</b></span>
    </a>
    <nav class="nav" id="nav" aria-label="Primary">{nav}</nav>
    <div class="top-actions">
      <button class="icon-btn" id="theme" type="button" aria-label="Switch colour theme">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" aria-hidden="true"><circle cx="12" cy="12" r="4"/><path d="M12 2v2M12 20v2M4.9 4.9l1.4 1.4M17.7 17.7l1.4 1.4M2 12h2M20 12h2M4.9 19.1l1.4-1.4M17.7 6.3l1.4-1.4"/></svg>
      </button>
      <button class="icon-btn menu-btn" id="menu" type="button" aria-label="Open menu" aria-expanded="false" aria-controls="nav">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" aria-hidden="true"><path d="M4 7h16M4 12h16M4 17h10"/></svg>
      </button>
      <a class="btn small" href="/#contact">Start a project {ARROW}</a>
    </div>
  </header>

  <main id="main">
{body}
  </main>

  <footer>
    <div class="wrap foot">
      <span>© 2026 NexaFusion · Software consultancy</span>
      <nav aria-label="Footer">
        <a href="/#services">Services</a><a href="/insights/">Insights</a><a href="/#faq">FAQ</a><a href="/#contact">Contact</a>
      </nav>
      <span class="status">All systems nominal</span>
    </div>
  </footer>
</body>
</html>
'''


def crumbs(*items: tuple[str, str | None]) -> tuple[str, dict]:
    parts, ld_items = [], []
    for n, (label, href) in enumerate(items, 1):
        parts.append(f'<a href="{href}">{e(label)}</a>' if href else f'<span aria-current="page">{e(label)}</span>')
        ld_items.append({"@type": "ListItem", "position": n, "name": label, **({"item": SITE + href} if href else {})})
    return (f'<nav class="crumbs" aria-label="Breadcrumb">{" / ".join(parts)}</nav>',
            {"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": ld_items})


def contact_aside(heading: str, text: str, tags: list[str] | None = None) -> str:
    tag_html = f'<div class="tags">{"".join(f"<span>{e(t)}</span>" for t in tags)}</div>' if tags else ""
    return f'''<aside class="aside">
          <h2>{e(heading)}</h2>
          <p>{e(text)}</p>
          <a class="btn" href="mailto:{EMAIL}?subject={e(heading).replace(" ", "%20")}">Start a conversation {ARROW}</a>
          {tag_html}
        </aside>'''


ART = {a["slug"]: a for a in ARTICLES}
SVC = {s["slug"]: s for s in SERVICES}


def post_card(a: dict) -> str:
    return f'''<article class="post reveal">
            <div><time datetime="{TODAY}">16 Nov 2026</time><span class="topic">{e(a["topic"])}</span></div>
            <div><h2><a href="/insights/{a["slug"]}/">{e(a["title"])}</a></h2><p>{e(a["desc"])}</p></div>
          </article>'''


def build_service(s: dict) -> str:
    bc, bc_ld = crumbs(("Home", "/"), ("Services", "/#services"), (s["name"], None))
    what = "".join(f'<div class="mini"><h3>{e(h)}</h3><p>{e(p)}</p></div>' for h, p in s["what"])
    fit = "".join(f"<li>{e(x)}</li>" for x in s["fit"])
    deliver = "".join(f"<li>{e(x)}</li>" for x in s["deliver"])
    related = ""
    if s["related"]:
        related = f'''
      <section class="wrap related" aria-labelledby="rel">
        <h2 id="rel">Related insights</h2>
        <div class="post-list">{"".join(post_card(ART[r]) for r in s["related"])}</div>
      </section>'''
    body = f'''    <section class="wrap page-hero">
      {bc}
      <p class="eyebrow">Service</p>
      <h1>{e(s["title"])}</h1>
      <p class="lede">{e(s["lede"])}</p>
    </section>

    <div class="wrap layout">
      <div class="prose">
        <h2>A good fit if…</h2>
        <ul>{fit}</ul>
      </div>
      {contact_aside("Talk about " + s["name"].split(" &")[0].split(",")[0], "Tell us what’s stuck. You’ll get a straight answer on whether we can help.", s["tags"])}
    </div>
    <section class="wrap" aria-labelledby="wwd">
      <div class="prose"><h2 id="wwd">What we do</h2></div>
      <div class="grid-3" style="margin-top:24px">{what}</div>
    </section>
    <div class="wrap layout">
      <div class="prose">
        <h2>What you get</h2>
        <ul>{deliver}</ul>
        <h2>How an engagement runs</h2>
        <ol>
          <li><strong>Diagnose (1–2 weeks).</strong> We read the code and the data, and agree the baseline and the number we expect to move.</li>
          <li><strong>Prove (3–5 weeks).</strong> A thin, real slice in production, measured against that baseline.</li>
          <li><strong>Scale and hand over.</strong> Widen the change with your engineers, then leave docs, runbooks and a team that owns it.</li>
        </ol>
      </div>
    </div>{related}'''
    ld = [bc_ld, {"@context": "https://schema.org", "@type": "Service", "name": s["name"], "description": s["lede"],
                  "provider": {"@type": "ProfessionalService", "name": "NexaFusion", "url": SITE + "/"},
                  "areaServed": "GB", "url": f"{SITE}/services/{s['slug']}/"}]
    return page(path=f"/services/{s['slug']}/", title=s["name"], desc=s["lede"], body=body, ld=ld)


def build_article(a: dict) -> str:
    bc, bc_ld = crumbs(("Home", "/"), ("Insights", "/insights/"), (a["title"], None))
    svc = SVC[a["service"]]
    others = [x for x in ARTICLES if x["slug"] != a["slug"]]
    body = f'''    <section class="wrap page-hero">
      {bc}
      <p class="eyebrow">{e(a["topic"])}</p>
      <h1>{e(a["title"])}</h1>
      <p class="lede">{e(a["desc"])}</p>
      <div class="meta-row"><time datetime="{TODAY}">16 Nov 2026</time><span>{e(a["read"])}</span><span>NexaFusion</span></div>
    </section>

    <div class="wrap layout">
      <article class="prose">{a["body"]}</article>
      {contact_aside("Need help with this?", f"Our {svc['name']} service covers exactly this ground.", svc["tags"])}
    </div>
    <div class="wrap"><p class="prose"><a href="/services/{svc['slug']}/">More about {e(svc['name'])} →</a></p></div>

    <section class="wrap related" aria-labelledby="more">
      <h2 id="more">More insights</h2>
      <div class="post-list">{"".join(post_card(x) for x in others)}</div>
    </section>'''
    ld = [bc_ld, {"@context": "https://schema.org", "@type": "Article", "headline": a["title"], "description": a["desc"],
                  "datePublished": TODAY, "dateModified": TODAY, "image": SITE + "/og.png",
                  "author": {"@type": "Organization", "name": "NexaFusion", "url": SITE + "/"},
                  "publisher": {"@type": "Organization", "name": "NexaFusion", "url": SITE + "/"},
                  "mainEntityOfPage": f"{SITE}/insights/{a['slug']}/"}]
    return page(path=f"/insights/{a['slug']}/", title=a["title"], desc=a["desc"], body=body, active="Insights", ld=ld, og_type="article")


def build_insights_index() -> str:
    bc, bc_ld = crumbs(("Home", "/"), ("Insights", None))
    body = f'''    <section class="wrap page-hero">
      {bc}
      <p class="eyebrow">Insights</p>
      <h1>Notes from the <em class="grad-text">engine room</em>.</h1>
      <p class="lede">Practical writing on AI engineering, memory safety, cyber security and performance — what works, what doesn’t, and why.</p>
    </section>
    <section class="wrap" style="padding-bottom:40px" aria-label="Articles">
      <div class="post-list">{"".join(post_card(a) for a in ARTICLES)}</div>
    </section>'''
    return page(path="/insights/", title="Insights", desc="Practical writing on AI engineering, Rust and memory safety, cyber security and AI compilers from NexaFusion.",
                body=body, active="Insights", ld=[bc_ld])


def build_feed() -> str:
    items = "".join(f'''
    <item>
      <title>{e(a["title"])}</title>
      <link>{SITE}/insights/{a["slug"]}/</link>
      <guid>{SITE}/insights/{a["slug"]}/</guid>
      <pubDate>Mon, 16 Nov 2026 09:00:00 +0000</pubDate>
      <description>{e(a["desc"])}</description>
    </item>''' for a in ARTICLES)
    return f'''<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0">
  <channel>
    <title>NexaFusion Insights</title>
    <link>{SITE}/insights/</link>
    <description>Practical writing on AI engineering, memory safety, cyber security and performance.</description>
    <language>en-gb</language>{items}
  </channel>
</rss>
'''


def build_sitemap() -> str:
    paths = ["/", "/insights/"] + [f"/services/{s['slug']}/" for s in SERVICES] + [f"/insights/{a['slug']}/" for a in ARTICLES]
    urls = "".join(f"\n  <url><loc>{SITE}{p}</loc><lastmod>{TODAY}</lastmod></url>" for p in paths)
    return f'<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">{urls}\n</urlset>\n'


def write(rel: str, text: str) -> None:
    out = ROOT / rel
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(text, encoding="utf-8")
    print("wrote", rel)


def main() -> None:
    for s in SERVICES:
        write(f"services/{s['slug']}/index.html", build_service(s))
    for a in ARTICLES:
        write(f"insights/{a['slug']}/index.html", build_article(a))
    write("insights/index.html", build_insights_index())
    write("insights/feed.xml", build_feed())
    write("sitemap.xml", build_sitemap())


if __name__ == "__main__":
    main()
