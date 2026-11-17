#!/usr/bin/env python3
"""Publish an explicit file allowlist, never the source checkout or Git history."""
from __future__ import annotations
import argparse
import json
from pathlib import Path
import shutil
import sys

sys.dont_write_bytecode = True
from build import ARTICLES, SERVICES, LEGACY_REDIRECTS, ROOT
from security_policy import cloudflare_headers

ASSETS = (
    "assets/site.css", "assets/home.css", "assets/no-script.css", "assets/site.js",
    "assets/home.js", "assets/ui.js", "assets/theme-init.js", "assets/cra-check.js",
    "assets/explorer.js", "assets/boot-verifier.js", "assets/update-verifier.js",
    "examples/update-verifier.test.mjs", "fonts/sora.woff2", "fonts/jetbrains-mono.woff2",
    "fonts/OFL.txt", "favicon.svg", "og.png", "apple-touch-icon.png", "icon-192.png",
    "icon-512.png", "site.webmanifest", "robots.txt", "sitemap.xml", "security.txt",
    ".well-known/security.txt", "CNAME", ".nojekyll", "404.html", "insights/feed.xml",
)


def public_files() -> set[str]:
    return set(ASSETS) | {"index.html", "engineering/index.html", "cra-readiness/index.html",
        "security/index.html", "privacy/index.html", "insights/index.html"} | {
        f"services/{item['slug']}/index.html" for item in SERVICES} | {
        f"insights/{item['slug']}/index.html" for item in ARTICLES} | set(LEGACY_REDIRECTS)


def package(output: Path, target: str) -> set[str]:
    output = output.resolve()
    if output == ROOT or output in ROOT.parents:
        raise ValueError("The artifact directory must not be the source checkout or its parent")
    files = public_files()
    allowed = files | ({"_headers"} if target == "cloudflare" else set())
    output.mkdir(parents=True, exist_ok=True)
    existing = {str(path.relative_to(output)) for path in output.rglob('*') if path.is_file() or path.is_symlink()}
    unexpected = existing - allowed
    if unexpected:
        raise ValueError("Refusing an artifact with unexpected files: " + ', '.join(sorted(unexpected)))
    for name in sorted(files):
        source, destination = ROOT / name, output / name
        if source.is_symlink() or not source.is_file():
            raise ValueError(f"Publish input is not an ordinary file: {name}")
        if any(part.is_symlink() for part in (destination, *destination.parents)):
            raise ValueError(f"Publish destination contains a symlink: {name}")
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source, destination)
    if target == 'cloudflare':
        (output / '_headers').write_text(cloudflare_headers())
    actual = {str(path.relative_to(output)) for path in output.rglob('*') if path.is_file()}
    if actual != allowed:
        raise ValueError("Artifact does not match the publish allowlist")
    return allowed


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, default=ROOT / 'dist')
    parser.add_argument('--target', choices=['github', 'cloudflare'], default='github')
    args = parser.parse_args()
    try:
        files = package(args.output, args.target)
    except ValueError as error:
        raise SystemExit(str(error))
    print(f"Packaged {len(files)} approved files for {args.target} into {args.output}")
