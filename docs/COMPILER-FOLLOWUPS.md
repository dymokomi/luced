# Compiler findings during the editor proof of concept

- Native value constructors such as `gpu.Color(...)` are accepted in top-level
  Luce constants, but their generated boundary adapter is a function call, which
  Base correctly rejects as a constant initializer. The editor creates its palette
  in the syntax theme. The compiler should either emit a valid constant
  representation or diagnose unsupported native initialization at the Luce source.
  Reproduce: `from gpu import Color` followed by a top-level
  `let accent = Color(0.2, 0.4, 0.8)` and a main that reads it.
- Empty list literals passed to optional list parameters need an explicit list
  type. Nonempty lists and explicitly typed empty lists work. Contextual typing
  should unwrap the optional parameter before checking the literal.

Borrowed native value arrays and optional borrowed list code generation were
fixed with interop regressions in Luce commits `1facc96` and `0bdca38`.
