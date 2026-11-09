# Build coordinate adapter

- Measure native world projection and UI dimensions instead of assuming a screen resolution or multiplying by Windows scaling.
- Map through the current game window, including window offsets and multiple monitors.
- Stop pointer operations when focus, window geometry, DPI or Build Mode changes.
- Add `a11y.buildcoords 5`, a read-only projection diagnostic.
- Announce localized names for all twelve Graphics dropdowns and checked/unchecked for the native Graphics checkboxes.
