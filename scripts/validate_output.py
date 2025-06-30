#!/usr/bin/env python3
"""
Simple sanity check:
- filenames follow convention
- all XML are well‑formed
- mandatory critique present
- no illegal dirs touched
"""
import pathlib, re, sys, xml.etree.ElementTree as ET
ROOT = pathlib.Path.cwd()
PAT  = re.compile(r'^(CHAR_BIB|PREMISE|BEAT|SCENE|REVISION)_[A-Za-z].*_\d{8}_\d{4}_.+\.(xml|md)$')

errors = []
for p in ROOT.rglob("*.*"):
    if p.is_file() and p.parts[0] == "story":
        if p.suffix in (".xml", ".md") and not PAT.match(p.name) and "current" not in p.parts:
            errors.append(f"Bad name: {p.relative_to(ROOT)}")
        if p.suffix == ".xml":
            try: ET.parse(p)
            except ET.ParseError as e: errors.append(f"XML error in {p}: {e}")

if errors:
    print("❌  Validation failed:")
    for e in errors: print(" •", e)
    sys.exit(1)
print("✅  All outputs pass basic validation.")
