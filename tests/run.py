#!/usr/bin/env python3
"""Run editor behavior against temporary files and real native compiler processes."""
import argparse
import shutil
import json
import re
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
    # The application's own dependencies, each taken from the checkout beside this one.
    manifest = (ROOT / 'package.prisma').read_text()
    dependencies = ''.join('    def dependency "%s" {\n        str owner = "dymokomi"\n        str version = "%s"\n        str path = %s\n    }\n' % (name, version, json.dumps(str(ROOT.parent / name)))
                           for name, version in re.findall(r'def dependency "([^"]+)" \{\s*str owner = "[^"]*"\s*str version = "([^"]+)"', manifest))
    (project / 'package.prisma').write_text('#prisma 4.0\ndef package "luced-tests" {\n    str owner = "dymokomi"\n    str version = "0.0.0"\n    str kind = "tool"\n    str language = "luce"\n    str entry = "src/main.luc"\n' + dependencies + '}\n')
    (root / 'package.prisma').write_text('#prisma 4.0\ndef package "luced-fixture" {\n    str owner = "dymokomi"\n    str version = "0.0.0"\n    str kind = "tool"\n    str language = "luce"\n    str entry = "main.luc"\n}\n')
    binary = root / ('tests.exe' if os.name == 'nt' else 'tests')
    for flags in [['--native', '--opt', '0'], ['--native', '--opt', '2']]:
        subprocess.run([str(a.luce.resolve()), 'build', str(project / 'src/main.luc'), *flags, '-o', str(binary)], env=env, check=True, timeout=180)
        subprocess.run([str(binary), str(root), str(a.luce.resolve()), str(a.base.resolve())], env=env, check=True, timeout=90)
