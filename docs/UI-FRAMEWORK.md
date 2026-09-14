# Editor and UI framework iteration

The editor is a client of the framework. Reusable styling, sizing, commands and
composition belong in luce-ui; workspace operations and Luce tokenization belong
in luced. Neither layer knows about Metal, Vulkan, or native window handles.

## Work checklist

- [x] Preserve highlight ranges across edits and expose versioned text changes.
- [x] Retokenize from the affected line until multiline lexical state converges;
      update only that highlight interval before another frame is drawn.
- [x] Test Unicode, multiline strings, inserted/deleted lines, undo/redo, stale
      updates and bounded work on ordinary edits.
- [x] Add inherited theme colors and font-relative control metrics to luce-ui.
- [x] Add reusable actions, compact toolbars and keyboard-operable menus.
- [x] Separate editor options, named views, actions and application lifetime;
      keep main a short composition entry point.
- [x] Verify portable contracts and actual rendered output, update documentation,
      commit and push the tested changes.

## Design

Text changes use half-open Unicode scalar ranges in the old and new revision.
The native editor transforms existing decorations immediately. The language
service caches line boundaries and outgoing lexer state; it scans changed lines
and continues only while the state differs from the cached suffix. Publication
is atomic and revision-checked. Syntax categories are independent of colors.

Controls use the font's line height as their vertical unit and its advance as
their horizontal unit. Compact chrome occupies one line; content remains a
continuous GPU surface and may include images or 3D viewports. A theme supplies
semantic colors and spacing, inherited through the widget tree with local
overrides. Themes do not encode editor commands or language tokens.

An action owns its label, enabled state and invocation. Menus, toolbar items and
application shortcuts invoke the same action. Editing operations stay in the
text editor; Save and Build are application actions. Named component classes
compose ordinary widgets instead of introducing another language or hidden
application-specific framework API.

## Reference designs

- [Qt Action](https://doc.qt.io/qt-6/qml-qtquick-controls-action.html): share command
  state between menus, buttons and shortcuts; separate presentation from logic.
- [SwiftUI environment](https://developer.apple.com/documentation/swiftui/environmentvalues):
  inherit presentation context through a composed view tree.
- [VS Code highlighting](https://code.visualstudio.com/api/language-extensions/syntax-highlight-guide):
  keep tokenization and token appearance separate.
- [Vim syntax synchronization](https://vimhelp.org/syntax.txt.html#%3Asyn-sync):
  multiline syntax requires a known prior state, not isolated changed-word coloring.
- [Emacs Font Lock](https://www.gnu.org/software/emacs/manual/html_node/emacs/Font-Lock.html):
  fontification is incremental work associated with changed/visible buffer regions.

Dynamic workspaces now extend these contracts through luce-ui's `Panel` and
`DStack`: stable content owners, tab selection, arbitrary split trees and reusable
drag/drop handling. Luced supplies document creation and close policy. Native OS
menus, a CSS engine and a full semantic language service remain future work.

## Validation

- UI contracts pass in native optimization levels 0–3 and both C comparison modes.
- Editor tests pass at native optimization levels 0 and 2, including 200
  deterministic randomized edits, multiline state propagation and undo/redo.
- A 1,000-line fixture verifies one scanned line for ordinary edits and unchanged
  colors outside the edited interval. Stale highlight publications are rejected.
- Shared actions, disabled commands, popup keyboard/mouse input, focus restoration,
  inherited/local themes and dynamically inserted controls have portable tests.
- Metal pixel readback passes with API and shader validation. Actual editor and
  open-menu frames were inspected; the screenshot is in `docs/preview.png`.

The bootstrap pins identify the tested source. Hosted Linux and Windows checks
run on push; the local rendering verification is macOS/Metal.
