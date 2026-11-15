CURRENT CUMULATIVE DEVELOPER TEST BUILD - 15 November 2026

For testing, close the game and back up the current mod. Copy TS4_Access contents into Mods/TS4_Access. With UI Cheats installed, use the matching _Overrides compatibility package in the configured late-loading folder. Do not install a second script copy. Keep your existing speech pack and settings.

For review, read CHANGELOG.md and MANIFEST.md; source changes are under changed-source and in CHANGES.patch against upstream adb868c. The script includes the upstream update and all retained contributions. No PR has been opened.

Validation: 134 suites passed; no failed suites; one optional prelaunch-helper suite skipped because PowerShell startup is unavailable. Source inputs stayed stable. Eighteen proactive UI fixtures and 33 right-click/queue checks passed. The script only adds the unbound right-click message to the activation-epoch fence. Both UI fidelity gates, movie structure and shared-handler parity passed. UI files are prepared for testing, not installed by this audit. In-game UI confirmation remains pending.
