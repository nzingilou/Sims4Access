# Changed code

- Scripts/tyjokr_a11y_basement.py: around line 75, native catalog selection and matching acknowledgement; around 121, guarded ground-level drawing and exact floor-minus-one verification; around 181, negative-floor room-worker routing; around 196, standalone assistant and diagnostics; around 266, Alt+B menu extension; around 285, config/settings registration; around 307, integration hooks. New module.
- contrib-reference/modules/tyjokr_a11y_contrib.py: around line 473, load/install the basement adapter after the coordinate and floor adapters.
- CONTROLS.txt: basement assistant instructions.
- tools/test_basement_adapter.py: 24 focused checks, also run against compiled bytecode.

Script: replace tyjokr_a11y_contrib.pyc and add tyjokr_a11y_basement.pyc; preserve the other 62 entries exactly. Source patch base: 0fe03a8. Restore the pre-install script to revert the installed change.
