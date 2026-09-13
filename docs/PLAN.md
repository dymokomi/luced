# luced proof of concept

The application is written in Luce. Reusable controls belong to `luce-ui`, and
native text input, clipboard and process resources belong to the standard library.
Every build uses the native compiler and leaves only requested artifacts.

## Foundations

- [ ] Deliver committed Unicode text and complete keyboard modifiers through the
  standard window API and UI event routing.
- [ ] Add clipboard access behind the standard OS boundary.
- [ ] Complete the monospace font's source-code punctuation and batch text drawing.
- [ ] Add a reusable text document/editor with selection, navigation, insertion,
  deletion, indentation, undo/redo, scrolling, line numbers and colored ranges.
- [ ] Add reusable file-list/pane controls and preserve focus across editing.
- [ ] Provide owned file and asynchronous command APIs usable directly from Luce.

## Application

- [ ] Create the `luced` workspace, document and command controllers in Luce.
- [ ] Show a file explorer, an editing pane and a compiler/program output pane.
- [ ] Open and save real UTF-8 files; preserve unsaved documents when switching.
- [ ] Highlight Luce and Luce Base comments, strings, keywords, types and numbers.
- [ ] Run builds/programs without blocking the UI, and show diagnostics and status.
- [ ] Add a coherent dark theme, shortcuts, status information and a sample project.

## Verification and handoff

- [ ] Test document edits, Unicode boundaries, syntax, file persistence and commands.
- [ ] Run portable UI/interop regressions and native rendering/input smoke checks.
- [ ] Build and inspect the running editor, including its clean output directory.
- [ ] Document setup, controls and proof-of-concept limits; commit coherent changes
  promptly and publish the finished sources.
