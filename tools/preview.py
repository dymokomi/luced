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
p.add_argument('--hover', choices=['edit-menu', 'divider', 'gutter', 'output'], help='capture hover feedback or top-level menu switching')
p.add_argument('--run', action='store_true', help='capture after the selected source builds and runs')
p.add_argument('--wrap', action='store_true', help='capture with soft word wrap toggled on')
p.add_argument('--diff', action='store_true', help='capture gutter change bars after editing the file')
p.add_argument('--tabs', action='store_true', help='open additional source files as tabs')
p.add_argument('--dock', choices=['menu', 'preview', 'merge', 'left', 'right', 'top', 'bottom'], help='capture dynamic workspace interaction')
p.add_argument('--output', type=Path, default=ROOT / 'build/preview.ppm')
a = p.parse_args()
a.output.resolve().parent.mkdir(parents=True, exist_ok=True)
with tempfile.TemporaryDirectory(prefix='luced-preview-') as temporary:
    work = Path(temporary)
    shutil.copytree(ROOT / 'src', work / 'src')
    (work / 'luce.toml').write_text('[package]\nname = "luced_preview"\nsource = "src"\n[dependencies]\nluce_ui = ' + json.dumps(str(ROOT.parent / 'luce-ui')) + '\nluce_config = ' + json.dumps(str(ROOT.parent / 'luce-config')) + '\n')
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
    if a.menu or a.palette or a.context or a.hover or a.dock or a.wrap:
        source = 'from ui import Event\nfrom input import EventKind' + (', Key' if a.menu or a.palette or a.wrap else '') + '\n' + source
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
        target = {'editor': 'context', 'files': 'editor.view.sidebar.context', 'output': 'editor.view.output.context'}[a.context]
        setup = ''
        if a.context == 'editor':
            source = 'from ui import invalid\n' + source
            setup = '            let context = editor.workspace.current_context() else error(invalid, "preview needs an editor panel")\n'
        source = source.replace('        if captured:', f"""        if frames == 10:
{setup}            let bounds = {target}.layout().bounds()
            editor.app.dispatch(Event(kind = EventKind.pointer_down, button = 1, x = bounds.x + 120.0, y = bounds.y + 30.0))
        if captured:""")
    if a.prompt:
        source = source.replace('        if captured:', """        if frames == 10:
            editor.actions.files.new_file.trigger()
        if captured:""")
    if a.hover:
        if a.hover == 'edit-menu':
            events = '''            let file = editor.view.menu.layout().child(0).layout().bounds()
            let edit = editor.view.menu.layout().child(1).layout().bounds()
            editor.app.dispatch(Event(kind = EventKind.pointer_down, x = file.x + 2.0, y = file.y + 2.0))
            editor.app.dispatch(Event(kind = EventKind.pointer_up, x = file.x + 2.0, y = file.y + 2.0))
            editor.app.dispatch(Event(kind = EventKind.pointer_moved, x = edit.x + 2.0, y = edit.y + 2.0))
'''
        elif a.hover == 'divider':
            events = '''            let bounds = editor.view.sidebar.body.layout().bounds()
            editor.app.dispatch(Event(kind = EventKind.pointer_moved, x = bounds.x + bounds.width + 2.0, y = bounds.y + 40.0))
'''
        elif a.hover == 'gutter':
            source = 'from ui import invalid\n' + source
            events = '''            let control = editor.workspace.current_editor() else error(invalid, "preview needs an open document")
            let bounds = control.layout().bounds()
            editor.app.dispatch(Event(kind = EventKind.pointer_moved, x = bounds.x + 4.0, y = bounds.y + 50.0))
'''
        else:
            events = '''            let bounds = editor.view.output.output.layout().bounds()
            editor.app.dispatch(Event(kind = EventKind.pointer_moved, x = bounds.x + 12.0, y = bounds.y + 12.0))
'''
        source = source.replace('        if captured:', '        if frames == 10:\n' + events + '        if captured:')
    if a.fold:
        source = source.replace('        if captured:', """        if frames == 10:
            editor.workspace.fold_all()
        if captured:""")
    if a.wrap:
        source = source.replace('        if captured:', """        if frames == 10:
            editor.app.dispatch(Event(kind = EventKind.key_down, key = Key.z, control = true, alt = true))
        if captured:""")
    if a.diff:
        source = 'from ui import invalid\n' + source
        source = source.replace('        if captured:', """        if frames == 10:
            let control = editor.workspace.current_editor() else error(invalid, "preview needs an editor")
            control.set_selection(0, 0)
            control.insert("pub let added_by_preview = 1\\n")
            let middle = control.length() // 2
            control.set_selection(middle, middle)
            control.insert("EDITED ")
            let victim = control.line_start(control.length() // 3)
            let past = control.line_end(victim) + 1
            if past <= control.length():
                control.set_selection(victim, past)
                control.insert("")
        if captured:""")
    if a.dock:
        source = 'from ui import invalid\n' + source
        events = '''            let panel = editor.workspace.current_panel() else error(invalid, "preview needs a document panel")
            let root = editor.view.dock.layout().bounds()
'''
        if a.dock == 'menu':
            events += '''            let bounds = editor.view.dock.add_bounds(panel)
            editor.app.dispatch(Event(kind = EventKind.pointer_down, x = root.x + bounds.x + bounds.width * 0.5, y = root.y + bounds.y + 5.0))
            editor.app.dispatch(Event(kind = EventKind.pointer_up, x = root.x + bounds.x + bounds.width * 0.5, y = root.y + bounds.y + 5.0))
'''
        else:
            x, y = {'merge': ('0.5', '0.5'), 'preview': ('0.1', '0.5'), 'left': ('0.1', '0.5'), 'right': ('0.9', '0.5'), 'top': ('0.5', '0.3'), 'bottom': ('0.5', '0.9')}[a.dock]
            events += f'''            let origin = editor.view.dock.tab_bounds(panel)
            let destination = editor.view.dock.panel_bounds(editor.view.output.body)
            let x = root.x + destination.x + destination.width * {x}
            let y = root.y + destination.y + destination.height * {y}
            editor.app.dispatch(Event(kind = EventKind.pointer_down, x = root.x + origin.x + 8.0, y = root.y + origin.y + 5.0))
            editor.app.dispatch(Event(kind = EventKind.pointer_moved, x = x, y = y))
'''
            if a.dock != 'preview':
                events += '            editor.app.dispatch(Event(kind = EventKind.pointer_up, x = x, y = y))\n'
        source = source.replace('        if captured:', '        if frames == 10:\n' + events + '        if captured:')
    if a.tabs:
        for path in [ROOT / 'src/editor/panel.luc', ROOT / 'src/editor/views.luc']:
            source += '    editor.workspace.open(' + json.dumps(str(path)) + ')\n'
    if a.run:
        source += '    editor.workspace.run()\n'
    source += '    editor.app.run()\n    observed.disconnect()\n    probe.save(' + json.dumps(str(a.output.resolve())) + ')\n    probe.end()\n    editor.close()\n    return 0\n'
    main.write_text(source)
    binary = work / 'preview'
    subprocess.run([str(a.luce.resolve()), 'build', str(main), '--native', '-o', str(binary)], check=True, env=dict(os.environ, LUCE_BASE=str(a.base.resolve())), timeout=180)
    subprocess.run([str(binary), str(a.source.resolve()), '--smoke', '--config-dir', str(work / 'configuration'), '--luce', str(a.luce.resolve()), '--base', str(a.base.resolve())], check=True, timeout=30)
print(a.output.resolve())
