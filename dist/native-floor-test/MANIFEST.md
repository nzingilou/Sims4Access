# Changed code

- Scripts/tyjokr_a11y_build_helpers.py, around lines 93-189: native floor reply/query and verified one-key-at-a-time floor switching; around 191-213: per-worker plan/stair isolation; around 219: registration and hooks.
- flash/extra-classes/ControlPanel.as, around line 397: read-only query listener; around 2135: BBGetLevelInfo reply. Only GameTray is rebuilt; the other 24 main-package resources and the compatibility package are unchanged.
- tools/test_build_helpers.py and tools/test_native_floor_bridge.js: regression checks.

Script: replace tyjokr_a11y_build_helpers.pyc only; preserve 62 other entries. Revert source with the reverse patch based on 16d0a54, and restore both pre-install script and main UI backups together.
