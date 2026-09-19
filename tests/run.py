#!/usr/bin/env python3
"""Run editor behavior against temporary files and real native compiler processes."""
import argparse
import shutil
import json
import os
from pathlib import Path
import subprocess
import tempfile
ROOT = Path(__file__).resolve().parents[1]
p = argparse.ArgumentParser(description=__doc__)
p.add_argument('--base', type=Path, default=ROOT.parent / ('luce-base/build/luce-base.exe' if os.name == 'nt' else 'luce-base/build/luce-base'))
p.add_argument('--luce', type=Path, default=ROOT.parent / ('luce/build/luce.exe' if os.name == 'nt' else 'luce/build/luce'))
a = p.parse_args()
env = dict(os.environ, LUCE_BASE=str(a.base.resolve()))
with tempfile.TemporaryDirectory(prefix='luced-tests-') as temp:
    root = Path(temp)
    project = root / 'application'
    shutil.copytree(ROOT / 'src', project / 'src')
    shutil.copy2(ROOT / 'tests/main.luc', project / 'src/main.luc')
    shutil.copy2(ROOT / 'tests/configuration.luc', project / 'src/configuration_tests.luc')
    shutil.copy2(ROOT / 'tests/workspace_tabs.luc', project / 'src/workspace_tab_tests.luc')
    (project / 'luce.toml').write_text('[package]\nname = "luced_tests"\nsource = "src"\n[dependencies]\nluce_ui = ' + json.dumps(str(ROOT.parent / 'luce-ui')) + '\nluce_config = ' + json.dumps(str(ROOT.parent / 'luce-config')) + '\nluce_ai = ' + json.dumps(str(ROOT.parent / 'luce-ai')) + '\n')
    (root / 'luce.toml').write_text('[package]\nname = "luced_fixture"\nsource = "."\n')
    binary = root / ('tests.exe' if os.name == 'nt' else 'tests')
    for flags in [['--native', '--opt', '0'], ['--native', '--opt', '2']]:
        subprocess.run([str(a.luce.resolve()), 'build', str(project / 'src/main.luc'), *flags, '-o', str(binary)], env=env, check=True, timeout=180)
        subprocess.run([str(binary), str(root), str(a.luce.resolve()), str(a.base.resolve())], env=env, check=True, timeout=90)
