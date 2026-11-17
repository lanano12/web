#!/usr/bin/env python3
"""Generate NexaFusion’s pages, feed and sitemap.

Page templates live in tools/home.html, tools/engineering.html and tools/device.svg. Service and
article content lives below. All pages share the same navigation and metadata.

    python3 tools/build.py

Edit the SERVICES / ARTICLES data, re-run, commit the output.
"""
from __future__ import annotations

import html
import json
from urllib.parse import quote
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SITE = "https://www.nexafusion.io"
EMAIL = "hello@nexafusion.io"
TODAY = "2026-11-17"
ARTICLE_DATE = "2026-11-16"

CSP = ("default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline'; "
       "img-src 'self' data:; font-src 'self'; connect-src 'self'; object-src 'none'; "
       "base-uri 'self'; form-action 'self'; upgrade-insecure-requests")

ARROW = ('<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.4" '
         'stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M5 12h14M13 6l6 6-6 6"/></svg>')

LOGO = '''<svg viewBox="0 0 64 64" aria-hidden="true">
        <defs><linearGradient id="lg" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#b5ff68"/><stop offset=".55" stop-color="#74e2bb"/><stop offset="1" stop-color="#6bcfe2"/></linearGradient></defs>
        <rect x="2" y="2" width="60" height="60" rx="16" fill="none" stroke="url(#lg)" stroke-width="3" opacity=".5"/>
        <path d="M20 44V20l24 24V20" fill="none" stroke="url(#lg)" stroke-width="5.5" stroke-linecap="round" stroke-linejoin="round"/>
      </svg>'''

# --------------------------------------------------------------------------
# Content
# --------------------------------------------------------------------------

SERVICES = [
    {
        "slug": "embedded-software",
        "name": "Embedded software engineering",
        "title": "Software that understands the hardware.",
        "lede": "Embedded software development, integration and debugging, with security and testability considered from the first design decision.",
        "fit": [
            "You need firmware developed or integrated with an existing product.",
            "An intermittent fault, timing issue or hardware interaction is holding up delivery.",
            "You need to change an established codebase without losing confidence in the behaviour that already works.",
        ],
        "what": [
            ("Firmware development", "Implementation close to the hardware, with explicit interfaces, ownership and resource constraints."),
            ("Hardware integration", "Bring software and hardware together, investigate peripheral interactions and make failures reproducible."),
            ("Debugging & root cause", "Follow the evidence through code, traces and device behaviour to find the actual fault."),
            ("Testing & verification", "Build repeatable tests around critical behaviour and the changes your product needs."),
            ("Codebase improvement", "Review and improve existing C and C++ incrementally, with tests around the behaviour that matters."),
            ("Release & handover", "Reproducible builds, clear release records and documentation your team can maintain."),
        ],
        "deliver": ["Reviewable implementation in your repository", "Tests and a reproducible verification method", "Recorded design decisions and known limitations", "Build, release and handover documentation"],
        "tags": ["Firmware", "C / C++", "Hardware integration", "Debugging", "Verification"],
        "related": ["memory-safety-roadmaps"],
    },
    {
        "slug": "cyber-security",
        "name": "Embedded product security",
        "title": "Know the boundaries. Engineer the defences.",
        "lede": "Product cyber security grounded in the device: its firmware, interfaces, update mechanism and the people who maintain it.",
        "fit": [
            "You need a clear view of your product’s attack surface and the risks worth addressing first.",
            "You have security findings to resolve in firmware or an existing codebase.",
            "You need security decisions and verification evidence that your engineers can explain.",
        ],
        "what": [
            ("Threat modelling", "Map assets, entry points and trust boundaries. Connect each significant risk to an engineering decision."),
            ("Firmware hardening", "Review exposed interfaces, input handling and privilege boundaries, then address the findings in code."),
            ("Update security", "Review authentication, version policy, recovery and failure behaviour across the product’s update path."),
            ("Supply-chain visibility", "Identify software dependencies and build a maintainable SBOM and vulnerability review process."),
            ("Security verification", "Use focused tests, static analysis and fuzzing where they provide useful evidence for the risks identified."),
            ("Vulnerability handling", "Connect security intake, triage, remediation and release records so reports have an owner and a path to resolution."),
        ],
        "deliver": ["Product threat model and prioritised findings", "Reviewable remediation and verification evidence", "Dependency and vulnerability visibility", "Documented decisions, residual risks and next steps"],
        "tags": ["Threat modelling", "Firmware security", "Secure updates", "SBOM", "Fuzzing"],
        "related": ["memory-safety-roadmaps", "eu-cyber-resilience-act"],
    },
    {
        "slug": "cra-readiness",
        "name": "CRA engineering readiness",
        "title": "Build the product. Keep the evidence.",
        "lede": "Turn Cyber Resilience Act readiness into practical engineering work: product risk assessment, vulnerability handling, software inventories and traceable technical documentation.",
        "fit": [
            "You supply products with digital elements to the EU market and need an engineering readiness plan.",
            "You need to connect existing development work to the evidence required for your product.",
            "Your team needs a workable vulnerability-handling and reporting process.",
        ],
        "what": [
            ("Engineering gap review", "Map the product, its lifecycle and existing engineering artefacts to the applicable requirements, alongside your regulatory advisers."),
            ("Product risk assessment", "Record the attack surface, security decisions and the verification needed to support them."),
            ("Reporting readiness", "Establish ownership and a rehearsed workflow for vulnerability and incident reporting."),
            ("Release inventories", "Generate machine-readable SBOMs and connect them to specific product versions and build records."),
            ("Support & updates", "Document the support period, update mechanism and vulnerability-handling process for each product."),
            ("Technical evidence", "Connect risks, implementation, tests and release records into a maintainable documentation set."),
        ],
        "deliver": ["Prioritised engineering readiness plan", "Product risk assessment and evidence map", "SBOM and release-record workflow", "Vulnerability-handling process and technical documentation"],
        "tags": ["EU CRA", "Risk assessment", "SBOM", "Vulnerability handling", "Technical evidence"],
        "related": ["eu-cyber-resilience-act"],
    },
]

ARTICLES = [
    {
        "slug": "memory-safety-roadmaps",
        "title": "Memory-safety roadmaps: Rust without the rewrite",
        "desc": "Why memory safety moved from a security talking point to a customer question, and how to build a roadmap that pairs hardened C++ with targeted Rust.",
        "topic": "Rust & C++",
        "read": "7 min read",
        "service": "embedded-software",
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
  <li><strong>Final report</strong> within 14 days of a corrective measure being available for a vulnerability, or within one month of the 72-hour incident notification (with a progress report if the incident is still ongoing).</li>
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
<p class="note">Engineering guidance, not legal advice. Check the <a href="https://digital-strategy.ec.europa.eu/en/policies/cyber-resilience-act">European Commission’s CRA overview</a> and <a href="https://eur-lex.europa.eu/eli/reg/2024/2847/oj">Regulation (EU) 2024/2847</a> with your legal advisers for your specific products.</p>
""",
    },
]


NAV = [("/engineering/", "Engineering"), ("/cra-readiness/", "CRA check"), ("/insights/", "Field notes")]

# --------------------------------------------------------------------------
# Templates
# --------------------------------------------------------------------------

e = html.escape
ACTIVE = ' class="active" aria-current="page"'


def page(*, path: str, title: str, desc: str, body: str, active: str = "", ld: list | None = None, og_type: str = "website", home: bool = False, module: str | None = None) -> str:
    url = SITE + path
    nav = "".join(
        f'<a href="{href}"{ACTIVE if label == active else ""}>{label}</a>'
        for href, label in NAV
    )
    ld_html = "".join(
        f'\n  <script type="application/ld+json">{json.dumps(x, ensure_ascii=False)}</script>' for x in (ld or [])
    )
    if home:
        header = f'''  <header class="top" id="top">
    <a class="logo" href="/" aria-label="NexaFusion home">{LOGO}<span>Nexa<b>Fusion</b></span></a>
    <div class="top-actions"><a class="header-contact" href="#contact">Let’s talk <span aria-hidden="true">↗</span></a></div>
  </header>'''
        footer = '''  <footer>
    <div class="wrap foot">
      <a class="footer-brand" href="/">NexaFusion</a>
      <nav aria-label="Footer"><a href="/engineering/">How we work</a><a href="/insights/">Field notes</a></nav>
      <span class="footer-meta">© 2026 NexaFusion · UK</span>
    </div>
  </footer>'''
        assets = '<link rel="stylesheet" href="/assets/home.css" />\n  <script src="/assets/home.js" defer></script>'
        no_script = ""
    else:
        header = f'''  <header class="top" id="top">
    <a class="logo" href="/" aria-label="NexaFusion home">
      {LOGO}
      <span>Nexa<b>Fusion</b></span>
    </a>
    <nav class="nav" id="nav" aria-label="Primary">{nav}</nav>
    <div class="top-actions">
      <button class="kbar-btn" type="button" data-kbar aria-label="Search and jump">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" aria-hidden="true"><circle cx="11" cy="11" r="7"/><path d="M20 20l-3.5-3.5"/></svg>
        <span class="kbar-label">Find</span><kbd class="kbar-hint">Ctrl K</kbd>
      </button>
      <button class="icon-btn" id="theme" type="button" aria-label="Switch colour theme">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" aria-hidden="true"><circle cx="12" cy="12" r="4"/><path d="M12 2v2M12 20v2M4.9 4.9l1.4 1.4M17.7 17.7l1.4 1.4M2 12h2M20 12h2M4.9 19.1l1.4-1.4M17.7 6.3l1.4-1.4"/></svg>
      </button>
      <button class="icon-btn menu-btn" id="menu" type="button" aria-label="Open menu" aria-expanded="false" aria-controls="nav">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" aria-hidden="true"><path d="M4 7h16M4 12h16M4 17h10"/></svg>
      </button>
      <a class="btn small" href="/#contact">Start a project {ARROW}</a>
    </div>
  </header>'''
        footer = f'''  <footer>
    <div class="wrap foot">
      <a class="footer-brand" href="/">NexaFusion<span>Embedded software. Security engineered in.</span></a>
      <nav aria-label="Footer">
        <a href="/services/embedded-software/">Embedded</a><a href="/services/cyber-security/">Security</a><a href="/services/cra-readiness/">CRA readiness</a><a href="mailto:{EMAIL}">Contact</a>
      </nav>
      <span class="footer-meta">© 2026 NexaFusion · UK</span>
    </div>
  </footer>'''
        assets = '''<script src="/assets/theme-init.js"></script>
  <script src="/assets/site.js" defer></script>
  <script src="/assets/ui.js" defer></script>'''
        no_script = '<noscript><style>.top{position:static;flex-wrap:wrap}.nav{display:flex;position:static;width:100%;flex-direction:row;flex-wrap:wrap;padding:0;border:0;box-shadow:none;background:none}.nav a{padding:8px 0;margin-right:20px}.top-actions{display:none}.scene-selector,.scene-hint,.boot-controls{display:none}</style></noscript>'
    if module:
        assets += f'\n  <script src="{e(module)}" type="module"></script>'
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
  <meta name="theme-color" content="#080c0c" />
  <meta name="color-scheme" content="{'dark' if home else 'dark light'}" />
  <meta property="og:type" content="{og_type}" />
  <meta property="og:site_name" content="NexaFusion" />
  <meta property="og:locale" content="en_GB" />
  <meta property="og:url" content="{url}" />
  <meta property="og:title" content="{e(title)}" />
  <meta property="og:description" content="{e(desc)}" />
  <meta property="og:image" content="{SITE}/og.png" />
  <meta property="og:image:width" content="1200" />
  <meta property="og:image:height" content="630" />
  <meta property="og:image:alt" content="NexaFusion — we engineer secure embedded software" />
  <meta name="twitter:card" content="summary_large_image" />
  <meta name="twitter:image" content="{SITE}/og.png" />
  <link rel="icon" href="/favicon.svg" type="image/svg+xml" />
  <link rel="apple-touch-icon" href="/apple-touch-icon.png" />
  <link rel="manifest" href="/site.webmanifest" />
  <link rel="alternate" type="application/rss+xml" title="NexaFusion Field notes" href="/insights/feed.xml" />
  <link rel="preload" href="/fonts/sora.woff2" as="font" type="font/woff2" crossorigin />
  <link rel="stylesheet" href="/assets/site.css" />
  {assets}{ld_html}
{no_script}
</head>
<body{' class="home"' if home else ""}>
  <a class="skip" href="#main">Skip to content</a>
  <div class="ambient" aria-hidden="true"><div class="aurora a"></div><div class="aurora b"></div></div>

{header}

  <main id="main">
{body}
  </main>

{footer}
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
          <a class="btn" href="mailto:{EMAIL}?subject={quote(heading)}">Start a conversation {ARROW}</a>
          {tag_html}
        </aside>'''


ART = {a["slug"]: a for a in ARTICLES}
SVC = {s["slug"]: s for s in SERVICES}


def post_card(a: dict) -> str:
    return f'''<article class="post reveal">
            <div><time datetime="{ARTICLE_DATE}">16 Nov 2026</time><span class="topic">{e(a["topic"])}</span></div>
            <div><h2><a href="/insights/{a["slug"]}/">{e(a["title"])}</a></h2><p>{e(a["desc"])}</p></div>
          </article>'''


def build_service(s: dict) -> str:
    bc, bc_ld = crumbs(("Home", "/"), ("Expertise", "/engineering/#services"), (s["name"], None))
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
          <li><strong>Understand.</strong> Review the product, code and constraints, then agree the scope and acceptance criteria.</li>
          <li><strong>Implement and verify.</strong> Make reviewable changes and test them against the agreed behaviour and risks.</li>
          <li><strong>Hand over.</strong> Leave the code, build instructions, evidence and decisions in your team’s hands.</li>
        </ol>
      </div>
    </div>{related}'''
    ld = [bc_ld, {"@context": "https://schema.org", "@type": "Service", "name": s["name"], "description": s["lede"],
                  "provider": {"@type": "ProfessionalService", "name": "NexaFusion", "url": SITE + "/"},
                  "areaServed": "GB", "url": f"{SITE}/services/{s['slug']}/"}]
    return page(path=f"/services/{s['slug']}/", title=s["name"], desc=s["lede"], body=body, ld=ld)


def build_article(a: dict) -> str:
    bc, bc_ld = crumbs(("Home", "/"), ("Field notes", "/insights/"), (a["title"], None))
    svc = SVC[a["service"]]
    others = [x for x in ARTICLES if x["slug"] != a["slug"]]
    body = f'''    <section class="wrap page-hero">
      {bc}
      <p class="eyebrow">{e(a["topic"])}</p>
      <h1>{e(a["title"])}</h1>
      <p class="lede">{e(a["desc"])}</p>
      <div class="meta-row"><time datetime="{ARTICLE_DATE}">16 Nov 2026</time><span>{e(a["read"])}</span><span>NexaFusion</span></div>
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
                  "datePublished": ARTICLE_DATE, "dateModified": TODAY, "image": SITE + "/og.png",
                  "author": {"@type": "Organization", "name": "NexaFusion", "url": SITE + "/"},
                  "publisher": {"@type": "Organization", "name": "NexaFusion", "url": SITE + "/"},
                  "mainEntityOfPage": f"{SITE}/insights/{a['slug']}/"}]
    return page(path=f"/insights/{a['slug']}/", title=a["title"], desc=a["desc"], body=body, active="Field notes", ld=ld, og_type="article")


def build_insights_index() -> str:
    bc, bc_ld = crumbs(("Home", "/"), ("Field notes", None))
    body = f'''    <section class="wrap page-hero">
      {bc}
      <p class="eyebrow">Field notes</p>
      <h1>Under the <em class="grad-text">surface.</em></h1>
      <p class="lede">Notes on product security, memory safety and the engineering behind CRA readiness.</p>
    </section>
    <section class="wrap" style="padding-bottom:40px" aria-label="Articles">
      <div class="post-list">{"".join(post_card(a) for a in ARTICLES)}</div>
    </section>'''
    return page(path="/insights/", title="Field notes", desc="Practical writing on embedded product security, memory safety and CRA readiness from NexaFusion.",
                body=body, active="Field notes", ld=[bc_ld])


CRA_SCOPE = "Do you sell or supply software, or products containing software, to customers in the EU?"

# (id, question, advice if not in place, reporting priority?)
CRA_QUESTIONS = [
    ("intake", "Can outside researchers and customers easily report a vulnerability to you (e.g. a security.txt file or a published security contact)?",
     "Publish a security contact and a security.txt file, and make sure the mailbox is monitored.", True),
    ("triage", "Could you triage a reported, actively exploited vulnerability and make a decision within 24 hours?",
     "Define an on-call owner and a 24-hour triage path for exploited vulnerabilities.", True),
    ("report", "Do you know who would submit an early warning through ENISA’s single reporting platform, and how?",
     "Name who files CRA reports, rehearse the 24h / 72h / final-report sequence and keep templates ready.", True),
    ("sbom", "Do your builds generate a machine-readable software bill of materials (SBOM)?",
     "Generate SBOMs (e.g. CycloneDX or SPDX) automatically in CI for every release.", False),
    ("scan", "Do you check releases for known exploitable vulnerabilities before shipping?",
     "Add dependency and image vulnerability scanning as a release gate.", False),
    ("threat", "Have your main products been threat-modelled, with the decisions recorded?",
     "Threat-model your main products and record the risk decisions — this feeds your technical documentation.", False),
    ("defaults", "Do your products ship with secure defaults (no default passwords, minimal exposed services)?",
     "Review default configurations and remove default credentials and unnecessary exposed services.", False),
    ("support", "Have you defined a support period and a way to ship security updates for each product?",
     "Set and publish a support period per product, with a reliable security-update mechanism.", False),
    ("cvd", "Do you publish a coordinated vulnerability disclosure policy?",
     "Publish a coordinated vulnerability disclosure policy explaining how you handle reports.", False),
    ("docs", "Do you keep technical documentation of your security design and risk assessment?",
     "Start a technical documentation set now, built from real engineering artefacts.", False),
    ("class", "Do you know whether any of your products are “important” or “critical” under the CRA?",
     "Classify each product — “important” and “critical” products need stricter conformity assessment.", False),
]


def build_cra_check() -> str:
    bc, bc_ld = crumbs(("Home", "/"), ("CRA readiness check", None))
    def radios(qid: str, opts: list[tuple[str, str]]) -> str:
        return "".join(
            f'<label><input type="radio" name="{qid}" value="{v}" required /><span>{e(t)}</span></label>' for v, t in opts)
    yn = [("2", "Yes"), ("1", "Partly"), ("0", "No")]
    qs = "".join(
        f'''
          <fieldset class="q">
            <legend><span class="qn">{n:02d}</span>{e(q)}{' <span class="live-tag">Reporting priority</span>' if live else ''}</legend>
            <div class="opts">{radios(qid, yn)}</div>
          </fieldset>''' for n, (qid, q, _a, live) in enumerate(CRA_QUESTIONS, 1))
    data = {"questions": [{"id": i, "advice": a, "live": l} for i, _q, a, l in CRA_QUESTIONS], "email": EMAIL}
    body = f'''    <section class="wrap page-hero">
      {bc}
      <p class="eyebrow">Free tool</p>
      <h1>How ready are you for the <em class="grad-text">Cyber Resilience Act</em>?</h1>
      <p class="lede">Twelve quick questions, about three minutes. You’ll get an indicative readiness score and your biggest gaps — starting with vulnerability-reporting readiness.</p>
      <div class="meta-row"><span>Runs entirely in your browser</span><span>Your answers stay in this page</span><span>Not legal advice</span></div>
    </section>

    <section class="wrap" aria-label="CRA readiness questions">
      <noscript><p class="note">Enable JavaScript to calculate a score. You can still read the questions and our <a href="/services/cra-readiness/">CRA engineering readiness service</a>.</p></noscript>
      <form class="cra" id="cra-form" novalidate>
          <fieldset class="q scope">
            <legend><span class="qn">00</span>{e(CRA_SCOPE)}</legend>
            <div class="opts">{radios("scope", [("yes", "Yes"), ("unsure", "Not sure"), ("no", "No")])}</div>
          </fieldset>{qs}
          <div class="cra-actions">
            <button class="btn" type="submit" disabled>See my results {ARROW}</button>
            <button class="btn ghost" type="reset">Start again</button>
            <p class="cra-error" id="cra-error" role="alert"></p>
          </div>
      </form>
      <div class="cra-result" id="cra-result" aria-live="polite" tabindex="-1" hidden></div>
      <script type="application/json" id="cra-data">{json.dumps(data, ensure_ascii=False)}</script>
    </section>

    <section class="wrap related" aria-labelledby="more">
      <h2 id="more">Go deeper</h2>
      <div class="post-list">{post_card(ART["eu-cyber-resilience-act"])}</div>
    </section>'''
    page_html = page(path="/cra-readiness/", title="CRA readiness check",
                     desc="Free EU Cyber Resilience Act readiness check: twelve questions, an indicative score and your biggest gaps. Runs in your browser.",
                     body=body, active="CRA check", ld=[bc_ld])
    return page_html.replace('<script src="/assets/site.js" defer></script>',
                             '<script src="/assets/site.js" defer></script>\n  <script src="/assets/cra-check.js" defer></script>')


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
    <title>NexaFusion Field notes</title>
    <link>{SITE}/insights/</link>
    <description>Practical writing on embedded product security, memory safety and CRA readiness.</description>
    <language>en-gb</language>{items}
  </channel>
</rss>
'''


def build_sitemap() -> str:
    paths = ["/", "/engineering/", "/cra-readiness/", "/insights/"] + [f"/services/{s['slug']}/" for s in SERVICES] + [f"/insights/{a['slug']}/" for a in ARTICLES]
    urls = "".join(f"\n  <url><loc>{SITE}{p}</loc><lastmod>{TODAY}</lastmod></url>" for p in paths)
    return f'<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">{urls}\n</urlset>\n'


LEGACY_REDIRECTS = {
    "services/ai-compilers/index.html": "/engineering/#services",
    "services/ai-agents/index.html": "/engineering/#services",
    "services/cloud-platform/index.html": "/engineering/#services",
    "services/fractional-cto/index.html": "/engineering/#services",
    "services/rust-cpp/index.html": "/services/embedded-software/",
    "insights/inference-cost-compilers/index.html": "/insights/",
}


def build_redirect(destination: str) -> str:
    """Retire old offers without leaving incoming links at a 404."""
    return f'''<!doctype html>
<html lang="en-GB"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta http-equiv="Content-Security-Policy" content="{CSP}">
<meta name="robots" content="noindex,follow">
<meta http-equiv="refresh" content="0;url={destination}">
<link rel="canonical" href="{SITE}{destination.split('#')[0]}">
<link rel="stylesheet" href="/assets/site.css">
<title>Page moved · NexaFusion</title>  <noscript><style>.top{{position:static;flex-wrap:wrap}}.nav{{display:flex;position:static;width:100%;flex-direction:row;flex-wrap:wrap;padding:0;border:0;box-shadow:none;background:none}}.nav a{{padding:8px 0;margin-right:20px}}.top-actions{{display:none}}.scene-selector,.scene-hint,.boot-controls{{display:none}}</style></noscript>
</head>
<body><main class="wrap page-hero"><p class="eyebrow">NexaFusion</p>
<h1>Engineering close to the hardware.</h1>
<p>This page has moved as we focus on embedded software, product security and CRA readiness.</p>
<a class="btn" href="{destination}">Continue to NexaFusion →</a></main></body></html>
'''


def build_home() -> str:
    body = (ROOT / "tools/home.html").read_text(encoding="utf-8")
    body = body.replace("<!-- DEVICE -->", (ROOT / "tools/device.svg").read_text(encoding="utf-8"))
    return page(path="/", title="We engineer secure embedded software.", home=True,
                  desc="NexaFusion: embedded software development, product cyber security and the engineering evidence behind EU Cyber Resilience Act readiness.",
                  body=body, ld=[{
                      "@context": "https://schema.org", "@type": "ProfessionalService",
                      "name": "NexaFusion", "url": SITE + "/", "email": EMAIL,
                      "description": "Embedded software engineering, product cyber security and CRA engineering readiness.",
                      "areaServed": "GB", "knowsAbout": ["Embedded software", "Firmware", "Product cyber security", "EU Cyber Resilience Act"],
                  }])


def build_engineering() -> str:
    body = (ROOT / "tools/engineering.html").read_text(encoding="utf-8")
    body = body.replace("<!-- DEVICE -->", (ROOT / "tools/device.svg").read_text(encoding="utf-8"))
    return page(path="/engineering/", title="Embedded engineering, from firmware to evidence",
                desc="Explore NexaFusion’s embedded software, product security and CRA engineering approach, with an interactive device architecture and live signature verification.",
                body=body, active="Engineering", module="/assets/explorer.js")


def write(rel: str, text: str) -> None:
    out = ROOT / rel
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(text, encoding="utf-8")
    print("wrote", rel)


def main() -> None:
    write("index.html", build_home())
    write("engineering/index.html", build_engineering())
    for old, destination in LEGACY_REDIRECTS.items():
        write(old, build_redirect(destination))
    for s in SERVICES:
        write(f"services/{s['slug']}/index.html", build_service(s))
    for a in ARTICLES:
        write(f"insights/{a['slug']}/index.html", build_article(a))
    write("insights/index.html", build_insights_index())
    write("cra-readiness/index.html", build_cra_check())
    write("insights/feed.xml", build_feed())
    write("sitemap.xml", build_sitemap())


if __name__ == "__main__":
    main()
