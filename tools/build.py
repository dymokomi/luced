#!/usr/bin/env python3
"""Build the Luce application natively; keep only the requested executable."""
import argparse
import os
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parents[1]
SUFFIX = ".exe" if os.name == "nt" else ""
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("--base", type=Path, default=ROOT.parent / f"luce-base/build/luce-base{SUFFIX}")
parser.add_argument("--luce", type=Path, default=ROOT.parent / f"luce/build/luce{SUFFIX}")
parser.add_argument("--opt", type=int, choices=range(4), default=1)
parser.add_argument("-o", "--output", type=Path, default=ROOT / f"build/luced{SUFFIX}")
args = parser.parse_args()
args.output.resolve().parent.mkdir(parents=True, exist_ok=True)
subprocess.run([str(args.luce.resolve()), "build", str(ROOT / "src/main.luc"),
                "--native", "--opt", str(args.opt), "-o", str(args.output.resolve())],
               cwd=ROOT, env=dict(os.environ, LUCE_BASE=str(args.base.resolve())), check=True)
print(args.output.resolve())
