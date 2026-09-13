# luced proof of concept

The application is written in Luce. Reusable controls belong to `luce-ui`, and
native text input, clipboard and process resources belong to the standard library.
Every build uses the native compiler and leaves only requested artifacts.

## Foundations

- [x] Deliver committed Unicode text and complete keyboard modifiers through the
  standard window API and UI event routing.
- [x] Add clipboard access behind the standard OS boundary.
- [x] Complete the monospace font's source-code punctuation and batch text drawing.
- [x] Add a reusable text document/editor with selection, navigation, insertion,
  deletion, indentation, undo/redo, scrolling, line numbers and colored ranges.
- [x] Add reusable file-list/pane controls and preserve focus across editing.
- [x] Provide owned file and asynchronous command APIs usable directly from Luce.

## Application

- [x] Create the `luced` workspace, document and command controllers in Luce.
- [x] Show a file explorer, an editing pane and a compiler/program output pane.
- [x] Open and save real UTF-8 files; preserve unsaved documents when switching.
- [x] Highlight Luce and Luce Base comments, strings, keywords, types and numbers.
- [x] Run builds/programs without blocking the UI, and show diagnostics and status.
- [x] Add a coherent dark theme, shortcuts, status information and a sample project.

## Verification and handoff

- [x] Test document edits, Unicode boundaries, syntax, file persistence and commands.
- [x] Run portable UI/interop regressions and native rendering/input smoke checks.
- [x] Build and inspect the running editor, including its clean output directory.
- [x] Document setup, controls and proof-of-concept limits; commit coherent changes
  promptly and publish the finished sources.

## Typography

- [x] Load installed monospace fonts through `luce-ui.Font`.
- [x] Share one 14-point font across all editor controls and open documents.
- [x] Rasterize grayscale text at the display backing scale through standard GPU coverage.
- [x] Verify font metrics, transparent backgrounds, ownership, real Metal pixels and editor behavior.
- [x] Replace the preview with an actual capture of the updated editor.
