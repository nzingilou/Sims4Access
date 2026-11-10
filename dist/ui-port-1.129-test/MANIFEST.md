# Changed code

- flash/TooltipManager_patched.as: native card/input traversal, state readback and bounded event/photography focus; function starting lines: A11yEventGoalFind 3752, A11yEventGoals 3802, A11yPhotography 3846, A11yCompositeRow 6781, A11yCollectFocusables 5170, A11yAnnounceDisplay 8412, A11yCheckboxState 8019, A11yActivate 7864. Rebuilt all 29 shared definitions.
- Scripts/tyjokr_a11y_event_goals.py: native goal query/reply lifetime; hub.py: event action and photography panel entries; lang.py: their labels.
- Scripts/tyjokr_a11y_house_workflow.py and tyjokr_a11y_basement.py: unified plan review, fresh native floor ranges, basement tool confirmation and verification diagnostics.
- Scripts/tyjokr_a11y_build_coordinates.py, tyjokr_a11y_build_helpers.py and flash/extra-classes/ControlPanel.as: measured viewport/client coordinates, native floor query and verified floor/stair integration.
- contrib-reference/modules/tyjokr_a11y_contrib.py: adapter installation hooks. tools/test_*: focused regression fixtures.
- changed-source contains cumulative changed source; CHANGES.patch is reversible against 127ec613e8a430ee841cca54d617901f1409ea56. BUILD-HASHES.json identifies compiled files.
