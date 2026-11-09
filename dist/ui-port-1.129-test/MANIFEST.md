# Changed code

- `Scripts/tyjokr_a11y_build_coordinates.py`: coordinate mapping, native input guards and diagnostic command. New module.
- `contrib-reference/modules/tyjokr_a11y_contrib.py`: adapter install hook around line 463 in `install()`.
- `flash/TooltipManager_patched.as`: `A11yCoordinate*` methods and marker fields around line 307; one `coords` branch in `A11yHandleEncoded` around line 4052.
- `flash/TooltipManager_patched.as`: `A11yGraphicsRowLabel` and one call from `A11yOptionsRowLabel` around line 6213; `A11yCheckboxState` recognizes the native Graphics LeftLabelCheckBox class.
- `CHEATS.txt`: diagnostic command.

Compiled archive: replace `tyjokr_a11y_contrib.pyc`, add `tyjokr_a11y_build_coordinates.pyc`; 60 existing entries preserved. Install the script and both UI packages as a matching set. BUILD-HASHES.json identifies the input and output files. Source patch is anchored to commit 127ec613e8a430ee841cca54d617901f1409ea56.
