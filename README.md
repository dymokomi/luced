# luced

A small native code editor written in **Luce**, built with the **luce-ui** Base
library. It has a file explorer, editable monospace source pane, Luce/Luce Base
syntax highlighting, and a compiler/program output pane.

![luced running the example through its native compiler](docs/preview.png)

Open files retain their own selection, scrolling, unsaved edits and undo history.
Saves replace files atomically, preserve existing permissions and CRLF line
endings, and refuse to overwrite changes detected on disk. Build and Run use
cancellable background commands so the UI stays responsive.

## Build and open

Keep `luced`, `luce-ui`, `luce`, and `luce-base` as sibling checkouts. The tested
revisions are recorded in `bootstrap/`. Build the native compilers first:

```sh
(cd ../luce-base && ./build.sh)
(cd ../luce && LUCE_BASE_COMPILER=../luce-base/build/luce-base ./build.sh)
python3 tools/build.py
./build/luced examples/hello/main.luc \
  --luce ../luce/build/luce --base ../luce-base/build/luce-base
```

On Windows, use the repositories' `tools/build_windows.py` scripts to build the
compilers. The editor build script selects `.exe` automatically; launch
`build/luced.exe` and pass the corresponding compiler paths. Native Windows GUI
requires the existing Vulkan backend and loader. macOS uses Metal. Linux builds
and runs the portable tests; its native window backend is still pending.

A path may name a directory or a UTF-8 file. With no path, the explorer starts in
the working directory. Compiler names default to `luce` and `luce-base` on PATH;
explicit paths are useful when developing the language alongside the editor.
Only the requested executable is produced by the app build. Editor builds place
program binaries under the nearest package's `build/` directory.

## Controls

| Action | Control |
| --- | --- |
| Open a file or directory | Click its explorer row; arrows and Enter also work |
| Save current file | Save, Cmd/Ctrl+S |
| Save all open files | Save all |
| Build current source | Build, Cmd/Ctrl+B |
| Build and run current source | Run, F5, Cmd/Ctrl+Enter |
| Cancel compiler or program | Stop |
| Indent / outdent | Tab / Shift+Tab |
| Undo / redo | Cmd/Ctrl+Z / Cmd/Ctrl+Shift+Z; Ctrl+Y also works |
| Move focus out of the editor | Ctrl+Tab |
| Scroll | Wheel or touchpad; editor scrollbar also drags |

Closing with unsaved files keeps the window open and shows a status message.
Save all before closing again, or choose **Discard & close** after that message.
Build and Run save open documents first and compile the selected source as the
entry point. There is no shell expansion or implicit project task configuration.

## Structure and tests

- `src/workspace`: files, documents, navigation and application coordination.
- `src/language`: a tolerant source lexer producing scalar highlight ranges.
- `src/commands`: asynchronous compiler/program orchestration.
- `src/main.luc`: composition of the native controls.
- `luce-ui`: reusable text editor, list view, input, layout and drawing.
- Base standard library: native text input, clipboard, files and process resources.

```sh
python3 tests/run.py
./build/luced examples/hello/main.luc --smoke
# macOS: read back the editor's actual Metal frame in an isolated test build
python3 tools/preview.py --source examples/hello/main.luc
```

Tests cover Unicode highlighting offsets, editing and undo, CRLF persistence,
external-file conflicts, workspace focus, and real native build/run output.
The UI and standard-library repositories have their own control, ownership,
input, pixel, file and process regression suites. CI runs on all three hosts.

This is a proof of concept. The output pane displays captured compiler/program
output; it is not an interactive PTY shell. Every control shares a 14-point monospace font, including toolbar buttons and
output. `luce-ui` loads the native face and caches antialiased text at the display
resolution (Menlo on macOS, Consolas on Windows, system monospace on Linux).
Font shaping, grapheme navigation, accessibility, richer IME presentation,
resizable splitters, search, completion, debugging and language-server integration
remain future work. Files are bounded to 4 MiB on read and 1,048,576 editor
scalars; 32 documents may remain open. See [the checklist](docs/PLAN.md) and
[compiler follow-ups](docs/COMPILER-FOLLOWUPS.md).
