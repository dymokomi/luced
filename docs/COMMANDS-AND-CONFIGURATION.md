# Commands, context and user configuration

- [x] Extend luce-ui popups with context placement, text input and reusable
  command search / text prompts; preserve focus and modal event handling.
- [x] Add editor/output/explorer context menus and file creation, folder creation,
  duplication, renaming and explicit deletion; keep filesystem policy in luced.
- [x] Give the folding gutter its own theme color and highlight the active pane.
- [x] Add user-wide `~/.luced/settings.toml` and `theme.toml`, validated loading,
  editable defaults, and reload commands without overwriting existing files.
- [x] Add Cmd/Ctrl+P command search, Edit Settings / Edit Theme, and F6/Shift+F6
  pane navigation using the same action objects as menus and shortcuts.
- [x] Test native and comparison modes, file operations and configuration errors;
  inspect actual rendered popups, document behavior, commit and push.

Reusable interaction and rendering belong in luce-ui. Luce editor components
own command meaning, open documents, filesystem changes and configuration schema.
OS home-directory resolution and filesystem primitives belong in luce-base.
Configuration uses the home directory, including the Windows user profile;
tests and preview captures use an isolated configuration directory.

## Interaction

`ContextMenu` decorates any widget. The layout tree routes a secondary click to
the closest context provider after the target has updated its selection. The
popup stays inside the window and takes keyboard input until it closes. The
originating pane retains its active border while a popup is open. Shift+F10 opens
the focused control's context menu without a pointer.

Luced supplies the actions and their availability:

| Area | Commands |
| --- | --- |
| Explorer | New File, New Folder, Duplicate File, Rename, Delete, Copy Path, Refresh Files |
| Editor | Undo, Redo, Cut, Copy, Paste, Select All, Save, folding |
| Output | Copy Output Selection, Select All Output, Clear Output |
| Other application chrome | Command Palette, Edit Settings, Edit Theme, Reload Configuration, Next Panel |

A secondary click on an explorer row selects without opening it. A secondary
click inside selected text preserves the selection. Read-only output never
enables destructive editing commands. `TextPrompt` provides reusable name entry
and explicit deletion confirmation; Escape or Cancel leaves files alone.

File creation, duplication and rename refuse existing destinations. Duplicate
copies the file's saved bytes into the first unused `name copy.ext` name; it does
not copy unsaved buffer contents or duplicate directories. Renaming directories
updates open descendant documents. Deletion refuses unsaved open documents,
including descendants, and asks for confirmation before removing a directory's
contents. Filesystem failures appear in the status bar.

`CommandPalette` searches the same action instances as menus and shortcuts.
Cmd+P on macOS, or Ctrl+P, opens it. Type words to filter, use arrows to select,
Enter to invoke and Escape to dismiss. Disabled commands remain visible but
cannot run. F6 and Shift+F6 cycle the explorer, editor and output; Cmd/Ctrl+1, 2
and 3 focus them directly. The focused pane has the `active_border` color.

![Command search in the native editor](palette.png)

## User files

The default directory is `$HOME/.luced` on macOS/Linux and
`%USERPROFILE%\.luced` on Windows. `--config-dir DIRECTORY` selects an isolated
profile. First launch creates missing files exclusively, preserving existing
files and comments. **Edit Settings** and **Edit Theme** open ordinary documents
with the same save and external-change protections as source files.

Default `settings.toml`:

```toml
[editor]
font_family = ""
font_size = 14.0

[window]
width = 1180
height = 800

[compiler]
luce = "luce"
luce_base = "luce-base"
```

An empty family uses the OS monospace face. Font sizes range from 8 to 40 points.
Window width ranges from 480 to 4096 and height from 300 to 4096; dimensions must
be whole numbers. `--luce` and `--base` override compiler settings for that run.

`theme.toml` accepts these optional colors; omitted values use defaults:

| Table | Keys |
| --- | --- |
| `colors` | `background`, `panel`, `foreground`, `muted`, `selection`, `accent`, `button`, `pressed`, `border`, `active_border`, `gutter`, `hover`, `hover_border`, `gutter_active`, `shadow` |
| `syntax` | `keyword`, `string`, `comment`, `number`, `type`, `other` |

Colors are quoted sRGB `#RRGGBB` values. For example:

```toml
[colors]
gutter = "#282F39"
active_border = "#598199"

[syntax]
keyword = "#C48BD3"
```

Popup appearance also accepts a `[popup]` table:

```toml
[popup]
shadow_offset = 4.0
shadow_opacity = 0.35
```

The shadow is a sharp translated rectangle, with no blur. Offset accepts 0–32
logical points, opacity accepts 0–1, and zero disables the shadow. Existing theme
files need no edits: omitted keys use defaults. Add these keys to customize them.

Hover uses `colors.hover` for controls and gutter rows, and `hover_border` for
panes. Keyboard focus uses `active_border` and takes precedence. The caret's
line-number row uses `gutter_active`, including while a menu is open.

The application checks for changed contents every half second and validates both
files before applying them. Font changes update the shared `Font` object used by
every control. Theme-only changes retain its glyph cache. Syntax colors replace
decorations without changing document text, selection or history. Compiler
changes affect future commands; window dimensions apply on the next launch.
**Reload Configuration** explicitly retries the current files.

Malformed changes stay on disk with an error in the status bar, leaving the
applied configuration in place. Startup uses defaults for an invalid file and
reports the problem. The configuration layer never rewrites user files to repair
them. Each file is limited to 64 KiB.

## Supported TOML forms

This is a small configuration reader, not a complete general TOML library. It
implements the forms needed by these schemas from the
[TOML 1.0 specification](https://toml.io/en/v1.0.0): bare table/key names,
single-line basic or literal strings, decimal numbers, and comments outside
strings. UTF-8 text can be written directly. Basic strings support `\\`, `\"`,
`\n`, `\r` and `\t`; literal strings preserve backslashes, useful for Windows
paths such as `'C:\dev\luce\build\luce.exe'`. Numbers support decimal fractions,
exponents and underscores between digits.

Quoted/dotted keys, multiline strings, Unicode escapes, arrays, inline tables,
booleans, dates and non-decimal integers are outside the current schema and are
rejected. Duplicate keys/tables and unknown settings are errors rather than
silently ignored typos. Missing keys use their documented defaults.

## Validation

`tests/configuration.luc` exercises isolated user files, invalid settings and
themes, command search, Unicode file prompts, file collisions, directory renames,
unsaved-document deletion protection, reload and pane navigation. It runs with
the existing editor suite in native modes 0 and 2.

Luce-ui separately tests popup placement, selection, dismissal, Unicode input,
focus restoration, shared font reconfiguration and detached widget reattachment
in native modes 0–3 and C comparison builds. Metal readback checks render the
actual app and popups; CI retains the resulting frames. Base tests exclusive
file creation/copy/move and owned home-directory paths across native and C modes.
