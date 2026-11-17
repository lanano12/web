#!/usr/bin/env python3
"""Read-only production checks. Missing live security headers are failures."""
from __future__ import annotations
import argparse
import urllib.request
import urllib.error
from security_policy import HEADERS


def inspect(base: str) -> list[str]:
    errors = []
    for path in ('/', '/engineering/', '/cra-readiness/', '/security/', '/.well-known/security.txt'):
        try:
            with urllib.request.urlopen(base + path, timeout=20) as response:
                if response.status != 200:
                    errors.append(f'{path}: HTTP {response.status}')
                for name, value in HEADERS.items():
                    if response.headers.get(name, '').strip() != value:
                        errors.append(f'{path}: {name} missing or differs from the reviewed policy')
                if path.endswith('security.txt'):
                    content = response.read().decode()
                    if 'Policy:' not in content or 'TODO' in content:
                        errors.append('security.txt: incomplete disclosure configuration')
        except (OSError, ValueError) as error:
            errors.append(f'{path}: {error}')
    for path in ('/tools/build.py', '/package.json', '/.git/config', '/SECURITY.md'):
        try:
            with urllib.request.urlopen(base + path, timeout=20) as response:
                errors.append(f'{path}: source-only file is publicly served (HTTP {response.status})')
        except urllib.error.HTTPError as error:
            if error.code != 404:
                errors.append(f'{path}: expected 404, got {error.code}')
        except OSError as error:
            errors.append(f'{path}: could not verify artifact boundary: {error}')
    try:
        with urllib.request.urlopen(base.replace('https://', 'http://', 1) + '/', timeout=20) as response:
            if not response.url.startswith(base + '/'):
                errors.append('HTTP does not redirect to the expected HTTPS origin')
    except OSError as error:
        errors.append(f'HTTP redirect: {error}')
    return errors


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--base', default='https://www.nexafusion.io')
    args = parser.parse_args()
    if not args.base.startswith('https://'):
        raise SystemExit('Use the HTTPS origin, without a path')
    errors = inspect(args.base.rstrip('/'))
    if errors:
        print('\n'.join(errors))
        raise SystemExit(1)
    print('PASS: live headers, HTTPS, disclosure route and artifact boundary')
