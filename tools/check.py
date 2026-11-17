#!/usr/bin/env python3
"""Check the committed static site without modifying it or using the network.

Edit tools/home.html, tools/engineering.html, tools/device.svg or tools/build.py, then:
    python3 tools/build.py
    python3 tools/check.py

Browser interactions and responsive layouts are checked by browser-check.cjs.
The site itself needs only a static server; Python is a development dependency.
"""
from __future__ import annotations

import json
import re
import runpy
import struct
import sys
from datetime import datetime, timezone
from collections import Counter
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlparse
from xml.etree import ElementTree

ROOT = Path(__file__).resolve().parent.parent
sys.dont_write_bytecode = True
sys.path.insert(0, str(ROOT / "tools"))
build = runpy.run_path(str(ROOT / "tools/build.py"))


class Page(HTMLParser):
    def __init__(self, source: str):
        super().__init__()
        self.ids: list[str] = []
        self.refs: list[str] = []
        self.scripts: list[dict] = []
        self.meta: dict[str, str] = {}
        self.unsafe: list[str] = []
        self.feed(source)

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == 'style' or 'style' in attrs or any(key.startswith('on') for key in attrs):
            self.unsafe.append(f'inline style or event handler on {tag}')
        if any(str(value).strip().lower().startswith('javascript:') for value in attrs.values()):
            self.unsafe.append(f'executable URL on {tag}')
        if attrs.get("id"):
            self.ids.append(attrs["id"])
        for key in ("href", "src", "data" if tag == "object" else ""):
            if attrs.get(key):
                self.refs.append(attrs[key])
        if tag == "script":
            self.scripts.append(attrs)
        if tag == "meta":
            name = attrs.get("http-equiv", attrs.get("name", "")).lower()
            self.meta[name] = attrs.get("content", "")


def main():
    expected = {
        "index.html": build["build_home"](),
        "security/index.html": build["build_information"]("security"),
        "privacy/index.html": build["build_information"]("privacy"),
        "engineering/index.html": build["build_engineering"](),
        "insights/index.html": build["build_insights_index"](),
        "cra-readiness/index.html": build["build_cra_check"](),
        "insights/feed.xml": build["build_feed"](),
        "sitemap.xml": build["build_sitemap"](),
        "deployment/headers.json": json.dumps(build["HEADERS"], indent=2) + "\n",
        "deployment/_headers": build["cloudflare_headers"](),
    }
    for service in build["SERVICES"]:
        expected[f"services/{service['slug']}/index.html"] = build["build_service"](service)
    for article in build["ARTICLES"]:
        expected[f"insights/{article['slug']}/index.html"] = build["build_article"](article)
    for old, destination in build["LEGACY_REDIRECTS"].items():
        expected[old] = build["build_redirect"](destination)

    errors = []
    for name, content in expected.items():
        if not (ROOT / name).exists() or (ROOT / name).read_text() != content:
            errors.append(f"Generated output is stale: {name}; run python3 tools/build.py")

    pages = {}
    for name in [*[n for n in expected if n.endswith(".html")], "404.html"]:
        source = (ROOT / name).read_text()
        page = Page(source)
        pages[(ROOT / name).resolve()] = page
        duplicates = [key for key, count in Counter(page.ids).items() if count > 1]
        if duplicates:
            errors.append(f"{name}: duplicate IDs: {duplicates}")
        errors.extend(f'{name}: {item}' for item in page.unsafe)
        if "default-src 'none'" not in page.meta.get("content-security-policy", ""):
            errors.append(f"{name}: missing Content Security Policy")
        if page.meta.get('content-security-policy') != build['CSP']:
            errors.append(f'{name}: policy differs from the reviewed browser policy')
        for script in page.scripts:
            if not script.get("src") and script.get("type") not in (
                "application/ld+json", "application/json"
            ):
                errors.append(f"{name}: executable inline script blocked by the site's CSP")
        for match in re.finditer(r'<script[^>]*type="application/(?:ld\+)?json"[^>]*>(.*?)</script>', source, re.S):
            try:
                json.loads(match[1])
            except ValueError as error:
                errors.append(f"{name}: invalid JSON: {error}")

    references = 0
    for path in (ROOT / 'assets').glob('*.js'):
        if re.search(r'\.innerHTML\s*=|insertAdjacentHTML\s*\(|\beval\s*\(|new\s+Function\s*\(', path.read_text()):
            errors.append(f'{path.relative_to(ROOT)}: unsafe HTML or script construction')
    disclosure = (ROOT / '.well-known/security.txt').read_text()
    if disclosure != (ROOT / 'security.txt').read_text() or 'TODO' in disclosure:
        errors.append('Disclosure contacts differ or contain an unfinished TODO')
    fields = dict(line.split(': ', 1) for line in disclosure.splitlines() if ': ' in line and not line.startswith('#'))
    if fields.get('Contact') != 'https://github.com/lanano12/web/security/advisories/new' or fields.get('Policy') != build['SITE'] + '/security/':
        errors.append('Disclosure contact or policy is missing')
    try:
        expiry = datetime.fromisoformat(fields['Expires'].replace('Z', '+00:00'))
        days = (expiry - datetime.now(timezone.utc)).days
        if not 0 < days <= 366:
            errors.append('security.txt expiry is stale or more than one year away')
    except (KeyError, ValueError, TypeError):
        errors.append('security.txt expiry is invalid')
    for source, page in pages.items():
        for ref in page.refs:
            url = urlparse(ref)
            if url.scheme or url.netloc:
                continue
            references += 1
            target = (ROOT / unquote(url.path).lstrip("/")) if url.path.startswith("/") else (
                source.parent / unquote(url.path) if url.path else source
            )
            if target.is_dir():
                target /= "index.html"
            target = target.resolve()
            if not target.exists():
                errors.append(f"{source.relative_to(ROOT)}: missing local target {ref}")
            elif url.fragment and target in pages and unquote(url.fragment) not in pages[target].ids:
                errors.append(f"{source.relative_to(ROOT)}: missing fragment {ref}")

    sitemap = ElementTree.parse(ROOT / "sitemap.xml")
    ElementTree.parse(ROOT / "insights/feed.xml")
    for loc in sitemap.findall(".//{*}loc"):
        target = (ROOT / urlparse(loc.text).path.lstrip("/") / "index.html").resolve()
        if target not in pages or "noindex" in pages[target].meta.get("robots", ""):
            errors.append(f"Sitemap includes missing or retired page: {loc.text}")

    manifest = json.loads((ROOT / "site.webmanifest").read_text())
    for item in manifest["icons"]:
        target = ROOT / item["src"].lstrip("/")
        if not target.is_file():
            errors.append(f"Missing manifest icon: {target.name}")
        elif target.suffix == ".png":
            dimensions = struct.unpack(">II", target.read_bytes()[16:24])
            if item["sizes"] != "x".join(map(str, dimensions)):
                errors.append(f"Wrong icon dimensions: {target.name}")
    if struct.unpack(">II", (ROOT / "og.png").read_bytes()[16:24]) != (1200, 630):
        errors.append("Share image must be 1200 × 630")

    if errors:
        print("\n".join(errors), file=sys.stderr)
        return 1
    print(f"PASS: {len(expected)} generated files, {len(pages)} pages, {references} local references")
    print("PASS: CSP, JSON, unique IDs, sitemap, feed, manifest and image dimensions")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
