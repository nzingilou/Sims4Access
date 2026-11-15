# Developer manifest

Base: upstream adb868c. CHANGES.patch contains the remaining local differences.

- Scripts/tyjokr_a11y_extensions.py: one queued startup for remaining local helpers. Old contrib/settings bootstrap modules and duplicate wall/layer/surface sources are removed.
- Scripts/tyjokr_a11y_layers.py, grid.py and place.py: attached-content focus and explicit surface targeting use native slot validation and the original placement/payment transaction.
- Scripts/tyjokr_a11y_rooms.py and room_bridge.py: custom labels take priority over cached inferred Plus room names; the bridge no longer patches grid functions.
- Scripts/tyjokr_a11y_settings.py and menu.py: chair-hint toggle and legacy-key migration alongside upstream settings.
- flash/TooltipManager_patched.as: scenario group/card traversal and narration; native apartment-marker focus/activation; rental region/building traversal. Earlier local UI repairs are retained.
- flash/extra-classes/PlexLotSelectOverlay.as: two helpers map the exact native clip to its lot data and call the existing validated selection handler. rebuild_all.ps1 adds this class to the existing GameEntryDock movie.
- Remaining house, basement, coordinate, roof, detached-building, lot-grid, chair, cleaning, away-action and event-goal modules retain their individual source files and tests.

- Native chair snapping: Scripts/tyjokr_a11y_chair_snap.py selects and revalidates native seat slots; grid.py (_fit_parts, _build_place) dispatches preview/placement; place.py (place, _finish, _after_payment) verifies attachment before payment. settings.py/menu.py expose the independent experimental toggle. chair_alignment.py suppresses duplicate hints. tools/test_chair_snapping.py covers 23 transaction and targeting cases.

- Speech lifecycle: Scripts/tyjokr_a11y_speech_process.py (SpeechJob) owns the child with KILL_ON_JOB_CLOSE. speech.py (_try_init_sapi, _dispose_sapi_locked, restart_sapi, stop, _speak_now) serializes ownership, reaps/closes on restart and registers exit cleanup. Ten lifecycle tests include real Windows parent exit/crash.

- Proactive native UI: TooltipManager_patched.as, A11yCollectFocusables (compound-row actions), A11yCompositeRow (restaurant courses/warning wrappers), A11yOptionsRowLabel (native business labels/employee context), A11yTextDecoration (jewelry visibility branches). Eighteen fixtures: tools/test_proactive_ui_native.js. Native audit: docs/development/audits/proactive-ui-20261115.md.

- Unbound right-click: TooltipManager_patched.as, A11yRightClickOwner/A11yTryRightClick/A11yMsgRightClick plus one native message listener. keys.py _send adds A11yRightClick to the existing activation-epoch fence; no key is bound. Native event and queue tests: test_ui_rightclick.js/test_ui_rightclick_queue.py.
