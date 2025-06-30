#!/usr/bin/env python3
"""
Moves unaccepted variations & critique into story/archive/<Stage>/.
Keeps story/<Stage>/ nearly empty after each iteration.
"""
import sys, shutil, pathlib
STAGE, accepted_file = sys.argv[1], sys.argv[2]
stage_dir = pathlib.Path("story")/STAGE
arch_dir  = pathlib.Path("story")/"archive"/STAGE
arch_dir.mkdir(parents=True, exist_ok=True)

for p in stage_dir.iterdir():
    if p.name != accepted_file:
        shutil.move(str(p), arch_dir/ p.name)
print(f"Archived other variations for {STAGE}.")
