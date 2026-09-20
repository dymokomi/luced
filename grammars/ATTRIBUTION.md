# Bundled grammar attribution

luced ships TextMate grammars for syntax highlighting. The Luce and Prism grammars are
authored here; the grammars below are vendored from third-party projects under their own
licenses. Each file was processed for bundling: `information_for_contributors` was removed
(its source is recorded here) and a `fileTypes` list was added for extension mapping; the
grammar rules are unchanged. Regenerate with tools/... (see the fetch/vendor scripts).

| grammar | scope | extensions | source | license |
|---|---|---|---|---|
| yaml | `source.yaml` | .yaml, .yml | https://github.com/microsoft/vscode/tree/main/extensions/yaml | MIT (microsoft/vscode; from textmate/yaml.tmbundle) |
| markdown | `text.html.markdown` | .md, .markdown | https://github.com/microsoft/vscode/tree/main/extensions/markdown-basics | MIT (microsoft/vscode) |
| c | `source.c` | .c, .h | https://github.com/microsoft/vscode/tree/main/extensions/cpp | MIT (microsoft/vscode; from jeff-hykin/cpp-textmate-grammar) |
| cpp | `source.cpp` | .cpp, .cc, .cxx, .hpp, .hh, .hxx, .ixx | https://github.com/microsoft/vscode/tree/main/extensions/cpp | MIT (microsoft/vscode; from jeff-hykin/cpp-textmate-grammar) |
| python | `source.python` | .py, .pyw, .pyi | https://github.com/microsoft/vscode/tree/main/extensions/python | MIT (microsoft/vscode; MagicPython) |
| javascript | `source.js` | .js, .mjs, .cjs, .jsx | https://github.com/microsoft/vscode/tree/main/extensions/javascript | MIT (microsoft/vscode) |
| typescript | `source.ts` | .ts, .mts, .cts | https://github.com/microsoft/vscode/tree/main/extensions/typescript-basics | Apache-2.0 (microsoft/TypeScript-TmLanguage) |
| html | `text.html.basic` | .html, .htm | https://github.com/microsoft/vscode/tree/main/extensions/html | MIT (microsoft/vscode) |
| css | `source.css` | .css | https://github.com/microsoft/vscode/tree/main/extensions/css | MIT (microsoft/vscode) |
| go | `source.go` | .go | https://github.com/microsoft/vscode/tree/main/extensions/go | MIT (microsoft/vscode; from go syntax) |
| rust | `source.rust` | .rs | https://github.com/microsoft/vscode/tree/main/extensions/rust | MIT (microsoft/vscode; from dustypomerleau/rust-syntax) |
| zig | `source.zig` | .zig, .zon | https://github.com/ziglang/vscode-zig | MIT (ziglang/vscode-zig) |
| toml | `source.toml` | .toml | https://github.com/tamasfe/taplo | MIT (tamasfe/taplo) |

The Luce (`luce.tmLanguage.json`) and Prism (`prism.tmLanguage.json`) grammars are original
to this project and covered by luced's own license.

