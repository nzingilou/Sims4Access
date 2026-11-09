# Display diagnostic manifest

Base: Git f7a85d5. Python 3.7.9.

- Scripts/tyjokr_a11y_display_diagnostic.py: Windows read-only snapshot (windows_snapshot), bounded display-option reader (saved_options), capped JSON logger (record), transparent project/conversion wrappers (install), and delayed a11y.inspect_display command. The command enables passive wrappers on the current build module; original results/errors are preserved even if diagnostics fail.
- tools/test_display_diagnostic.py: DPI/offset examples, process/focus guards, unavailable APIs, pointer-width bindings, options privacy/root layouts, rate limits and transparent/no-action command behavior. CHEATS.txt / docs/development/changes/display-diagnostic.md: usage and API references.

Validation: 116 suites / 1,577 reported checks passed with stable inputs; 16 compiled diagnostic checks passed. The package adds one diagnostic module; all 60 existing archive entries remain byte-identical. Live measurements are pending.

The installed planner lacks the checkout's coordinate overrides. This package preserves it for diagnosis. Game UI-stage size is explicitly unknown; no conversion correction is inferred from saved resolution.

Rollback: restore the previous script archive, or remove the added diagnostic module and cheat documentation. SOURCE-MANIFEST.json records exact before/after hashes.
