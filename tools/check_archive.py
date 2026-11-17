#!/usr/bin/env python3
"""Verify the actual Pages upload archive, including .well-known/security.txt."""
import hashlib
from pathlib import PurePosixPath
import sys
import tarfile
from package_site import ROOT, public_files


def verify(archive):
    expected = public_files()
    directories = {'.'} | {str(parent) for name in expected for parent in PurePosixPath(name).parents}
    actual = set()
    with tarfile.open(archive) as tar:
        for member in tar:
            path = PurePosixPath(member.name)
            if path.is_absolute() or '..' in path.parts:
                raise ValueError('Unsafe archive path')
            name = str(path)
            if member.isdir() and name in directories:
                continue
            if not member.isfile() or name not in expected or name in actual:
                raise ValueError(f'Unexpected archive entry: {name}')
            source = ROOT / name
            if member.size != source.stat().st_size:
                raise ValueError(f'Archive size differs from reviewed source: {name}')
            content = tar.extractfile(member).read()
            if hashlib.sha256(content).digest() != hashlib.sha256(source.read_bytes()).digest():
                raise ValueError(f'Archive content differs from reviewed source: {name}')
            actual.add(name)
    if actual != expected:
        raise ValueError('Missing archive entries: ' + ', '.join(sorted(expected - actual)))
    print(f'PASS: uploaded archive contains exactly {len(expected)} reviewed files, including security.txt')


if __name__ == '__main__':
    verify(sys.argv[1])
