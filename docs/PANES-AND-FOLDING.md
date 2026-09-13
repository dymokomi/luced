# Panes, scrolling and folding

- [x] Add a themed Pane border and reusable horizontal/vertical SplitView.
- [x] Respect pane minima, support live dragging and keyboard resizing, and keep
      divider behavior in luce-ui rather than application event handlers.
- [x] Normalize horizontal scrolling direction and clamp both axes to content,
      including after edits, window resizing and folding.
- [x] Add generic nested fold ranges and visible-line mapping to TextEditor.
- [x] Derive Luce/Luce Base folding from indentation and lexer state in luced;
      preserve fold state across unrelated edits and document switches.
- [x] Verify interactions, update the preview/docs, commit and push.

Qt's [QSplitter](https://doc.qt.io/qt-6/qsplitter.html) separates draggable handles
from pane content and constrains movement using pane sizes. Its
[SplitView](https://doc.qt.io/qt-6/qml-qtquick-controls-splitview.html) similarly
separates minimum/preferred sizes from handle presentation. Our first SplitView
composes two children and nests for larger layouts, with live resizing and
non-collapsing minima. Pane borders remain independent of the splitter.

Folds hide whole document lines below a header. Text and scalar offsets remain
unchanged; rendering, hit testing, navigation and scroll extents share one visible
line map. The widget accepts versioned ranges from any language service. Luce's
indentation and multiline-string rules stay in the editor's language module.
Entering a hidden position reveals it; explicit selections retain hidden text.

Scroll deltas describe content movement on each axis. The native window layer
normalizes platform wheel conventions; controls subtract those deltas from their
viewport offsets. End bounds come from the longest visible line and the number
of visible rows, with only the padding needed to display the caret.

## Validation

- UI consumers pass native optimization levels 0–3 and both C comparison modes.
- Splitter tests cover both axes, dragging, keyboard resizing, cancellation,
  minima/maxima, clipped overflow, border insets, and invalid child replacement.
- Text tests cover nested folds, gutter clicks, hidden-row navigation, explicit
  selection, boundary deletion, Unicode/tab widths, folding and resize clamps.
- Allocation failures preserve the previous fold set and projection without
  leaks; 300 deterministic edits plus undo/redo match independent complete line
  scans. The editor's 200 randomized highlighting edits also pass with folding.
- Editor tests pass at native optimization levels 0 and 2, including unchanged
  dirty state after folding and one-line retokenization after unrelated edits.
- Metal pixel tests pass in all six compiler modes with API and shader validation.
  Unfolded, folded and open-menu editor frames were inspected. The native app
  build leaves only `build/luced`.
- Base window contracts pass locally in native/C modes. The Windows wheel
  contract compiles to native Windows assembly locally; execution belongs to
  hosted Windows CI. Bootstrap snapshots were refreshed for all three targets.

The regular [preview](preview.png) and [folded view](folding.png) are actual Metal
captures. Dependency pins record the tested source; hosted Linux/Windows checks
run on push. Local interactive/rendering verification is macOS.

Windows horizontal wheel signs follow the platform's
[WM_MOUSEHWHEEL contract](https://learn.microsoft.com/en-us/windows/win32/inputdev/wm-mousehwheel)
and are normalized at the standard window boundary. UI controls use the same
content-displacement convention on every backend.
