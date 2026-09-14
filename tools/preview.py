#!/usr/bin/env python3
"""Capture actual Metal output in an isolated test build, without screen access."""
import argparse
import json
from pathlib import Path
import shutil
import subprocess
import tempfile
import os
ROOT = Path(__file__).resolve().parents[1]
p = argparse.ArgumentParser(description=__doc__)
p.add_argument('--base', type=Path, default=ROOT.parent / 'luce-base/build/luce-base')
p.add_argument('--luce', type=Path, default=ROOT.parent / 'luce/build/luce')
p.add_argument('--source', type=Path, default=ROOT / 'src/main.luc')
p.add_argument('--fold', action='store_true', help='capture the selected file with code folded')
p.add_argument('--menu', action='store_true', help='capture the File popup through keyboard input')
p.add_argument('--palette', action='store_true', help='capture command search')
p.add_argument('--context', choices=['editor', 'files', 'output'], help='capture a right-click menu')
p.add_argument('--prompt', action='store_true', help='capture the new-file prompt')
p.add_argument('--run', action='store_true', help='capture after the selected source builds and runs')
p.add_argument('--output', type=Path, default=ROOT / 'build/preview.ppm')
a = p.parse_args()
a.output.resolve().parent.mkdir(parents=True, exist_ok=True)
with tempfile.TemporaryDirectory(prefix='luced-preview-') as temporary:
    work = Path(temporary)
    shutil.copytree(ROOT / 'src', work / 'src')
    (work / 'luce.toml').write_text('[package]\nname = "luced_preview"\nsource = "src"\n[dependencies]\nluce_ui = ' + json.dumps(str(ROOT.parent / 'luce-ui')) + '\n')
    native = (ROOT.parent / 'luce-base/tests/programs/gpu/native.lucb').read_text()
    native += '''
import files
import memory
import strings
pub func save(path: str) -> !:
    let texture = captured_texture else trap("no captured frame")
    let width = uint(texture, sel("width"))
    let height = uint(texture, sel("height"))
    let device = msg(texture, sel("device"))
    let queue = msg(device, sel("newCommandQueue"))
    defer invoke(queue, sel("release"))
    let row_bytes = (width * 4 + 255) & ~(u64)255
    let storage = buffer(device, sel("newBufferWithLength:options:"), row_bytes * height, 0)
    defer invoke(storage, sel("release"))
    let command = msg(queue, sel("commandBuffer"))
    let encoder = msg(command, sel("blitCommandEncoder"))
    blit(encoder, sel("copyFromTexture:sourceSlice:sourceLevel:sourceOrigin:sourceSize:toBuffer:destinationOffset:destinationBytesPerRow:destinationBytesPerImage:"), texture, 0, 0, GpuProbeOrigin(), GpuProbeExtent(width = width, height = height, depth = 1), storage, 0, row_bytes, row_bytes * height)
    invoke(encoder, sel("endEncoding"))
    invoke(command, sel("commit"))
    invoke(command, sel("waitUntilCompleted"))
    assert(uint(command, sel("status")) == 4)
    let bytes = (const u8*)msg(storage, sel("contents"))
    var header: u8[100]
    let prefix = try format(header, f"P6\\n{width} {height}\\n255\\n")
    let output = try alloc u8[prefix.length + (usize)(width * height * 3)]
    defer free(output)
    memory.copy(output, prefix.bytes, prefix.length)
    for y in 0..<height:
        for x in 0..<width:
            let source = y * row_bytes + x * 4
            let destination = prefix.length + (usize)((y * width + x) * 3)
            output[destination] = bytes[source + 2]
            output[destination + 1] = bytes[source + 1]
            output[destination + 2] = bytes[source]
    let name = try strings.copy(path)
    defer strings.release(name)
    try files.write((c.str)name, output)
'''
    (work / 'src/probe.lucb').write_text(native)
    main = work / 'src/main.luc'
    # Construct the public application component directly. The capture harness
    # no longer depends on variable names or source replacement in main.luc.
    source = """import probe
from editor.application import Editor
from editor.options import Options
pub func main(arguments: list[str]) -> int!:
    let editor = Editor(Options(arguments))
    var frames = 0
    var captured = false
    let observed = editor.app.on_frame(func (elapsed: float) -> unit!:
        frames += 1
        if captured:
            editor.app.stop()
        elif frames >= 12 and not editor.runner.busy():
            probe.begin("luced")
            captured = true)
"""
    if a.menu or a.palette or a.context:
        source = 'from ui import Event\nfrom input import EventKind' + (', Key' if a.menu or a.palette else '') + '\n' + source
    if a.menu:
        source = source.replace('        if captured:', """        if frames == 10:
            editor.app.dispatch(Event(cancelled = true))
            editor.app.dispatch(Event(kind = EventKind.key_down, key = Key.tab))
            editor.app.dispatch(Event(kind = EventKind.key_down, key = Key.down))
        if captured:""")
    if a.palette:
        source = source.replace('        if captured:', """        if frames == 10:
            editor.app.dispatch(Event(kind = EventKind.key_down, key = Key.p, meta = true))
            for scalar in [101, 100, 105, 116]:
                editor.app.dispatch(Event(kind = EventKind.text_input, codepoint = scalar))
        if captured:""")
    if a.context:
        target = {'editor': 'editor.view.editor.context', 'files': 'editor.view.sidebar.context', 'output': 'editor.view.output.context'}[a.context]
        source = source.replace('        if captured:', f"""        if frames == 10:
            let bounds = {target}.layout().bounds()
            editor.app.dispatch(Event(kind = EventKind.pointer_down, button = 1, x = bounds.x + 120.0, y = bounds.y + 30.0))
        if captured:""")
    if a.prompt:
        source = source.replace('        if captured:', """        if frames == 10:
            editor.actions.files.new_file.trigger()
        if captured:""")
    if a.fold:
        source = source.replace('        if captured:', """        if frames == 10:
            editor.workspace.fold_all()
        if captured:""")
    if a.run:
        source += '    editor.workspace.run()\n'
    source += '    editor.app.run()\n    observed.disconnect()\n    probe.save(' + json.dumps(str(a.output.resolve())) + ')\n    probe.end()\n    editor.close()\n    return 0\n'
    main.write_text(source)
    binary = work / 'preview'
    subprocess.run([str(a.luce.resolve()), 'build', str(main), '--native', '-o', str(binary)], check=True, env=dict(os.environ, LUCE_BASE=str(a.base.resolve())), timeout=180)
    subprocess.run([str(binary), str(a.source.resolve()), '--smoke', '--config-dir', str(work / 'configuration'), '--luce', str(a.luce.resolve()), '--base', str(a.base.resolve())], check=True, timeout=30)
print(a.output.resolve())
