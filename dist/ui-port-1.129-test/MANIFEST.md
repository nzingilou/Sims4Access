# Settings fix manifest

Base: Git 4ce00a4. Game 1.129.39.1030.

- flash/TooltipManager_patched.as: A11yOptionsControl / A11yOptionsRowLabel (around 6102): native control targeting and visible row text. A11yActionProxy (6765) and A11yActivate (7570): native activation and settled checkbox reread. A11yCheckboxState (7717): current visible checkbox state only.
- tools/test_options_simplified.js: option types, disabled targets, values, states, descriptions and subclasses. tools/test_event_activation_v13.js: inspect the complete proxy branch instead of a fixed character count; retain disabled/refused-click and single-dispatch checks.
- docs/development/changes/options-settings.md: reproduction and focused test instructions.

Validation: 113 suites / 1,531 reported checks passed with stable inputs; standard and compatibility fidelity gates passed. Class sets and non-code tags retained. Settings/routing helpers match across 29 compiled copies. Source review limits changes to four existing manager methods and one addition.

Rollback: restore the previous paired UI packages, or reverse CHANGES.patch against its recorded source state. SOURCE-MANIFEST.json records exact source hashes. In-game settings verification remains pending.
