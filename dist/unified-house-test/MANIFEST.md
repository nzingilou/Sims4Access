# Changed code

- Scripts/tyjokr_a11y_house_workflow.py: around lines 25-55, fresh native floor bounds and simulation-thread room scanning; around 75-230, preserve native plan geometry while extending floors, editing individual rooms and reviewing construction; around 260, one Build helper row and integration hooks. New module.
- Scripts/tyjokr_a11y_basement.py: around line 145, post-camera tool confirmation and post-drag native floor/funds diagnostics; around 185, a thread-local failure reason for accurate house-worker feedback.
- contrib-reference/modules/tyjokr_a11y_contrib.py: final install hook after the basement adapter.
- CONTROLS.txt: unified flow instructions.
- tools/test_house_workflow.py and tools/test_basement_adapter.py: 46 focused checks, also run against compiled modules.

Script: replace tyjokr_a11y_contrib.pyc and tyjokr_a11y_basement.pyc; add tyjokr_a11y_house_workflow.pyc; preserve 62 other entries exactly. Source patch base: a227ff6. Revert with the reverse patch and pre-install script backup.
