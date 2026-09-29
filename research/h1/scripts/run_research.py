#!/usr/bin/env python3
import subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3]
steps=[
 ["python","research/h1/scripts/audit_data.py"],
 ["python","research/h1/scripts/build_dataset.py"],
 ["python","research/h1/scripts/research.py"],
 ["python","research/h1/scripts/mine_conditions.py"],
 ["python","research/h1/scripts/precursor_study.py"],
 ["python","research/h1/scripts/precursor_candidates.py"],
]
for cmd in steps:
    print("[RUN]"," ".join(cmd),flush=True)
    subprocess.run(cmd,cwd=ROOT,check=True)
