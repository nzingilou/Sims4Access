# Away actions manifest

Base: Git fae26cf. Game 1.129.39.1030.

- Scripts/tyjokr_a11y_away.py: separate picker and PICK_SKEWER transport module; open_sim around 43 and open_away_actions around 78. Revalidates household, actor, zone and remote target before opening the native menu; logs requests/failures.
- Scripts/tyjokr_a11y_hub.py: lazy callback and a11y.away command around 123; Accessibility row around 718. Scripts/tyjokr_a11y_lang.py around 895: labels/feedback. CONTROLS.txt / CHEATS.txt: entry points.
- tools/test_away_actions.py / test_scanner_pick_bridge.js: target guards, native transport and hub wiring. docs/development/changes/away-actions.md: native API evidence and live test.

Validation: 114 suites / 1,547 reported checks passed with stable inputs. The compiled archive passed the 15 away-action checks. Only hub/lang bytecode replaced and the away module added; 56 archive entries and 44 existing hub functions match the previous build. In-game verification is pending.

Rollback: restore the previous TS4_Access.ts4script, or reverse CHANGES.patch and remove the away module. SOURCE-MANIFEST.json records exact source hashes.
