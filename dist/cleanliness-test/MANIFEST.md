# Scanner cleanliness manifest

Base: Git 0766e12. Game 1.129.39.1030.

- Scripts/tyjokr_a11y_cleanliness.py, suffix around 14: bounded, read-only state recognition; visual dirtiness takes precedence over commodity state; dust is independent. Unknown/missing states give no suffix; read failures are contained and logged.
- Scripts/tyjokr_a11y_scanner.py: _entry_parts around 755 and _group_parts around 778 add status to speech. Scripts/tyjokr_a11y_lang.py around 16: dirty/dusty labels. CONTROLS.txt: announcement documentation.
- tools/test_cleanliness.py: native snapshot cases, state changes, bounded reads/failures and both announcement paths. docs/development/changes/scanner-cleanliness.md: verified state IDs and live check.

Validation: 115 suites / 1,561 reported checks passed with stable inputs; 14 compiled helper/announcement checks passed. The installed scanner's contribution bootstrap is preserved exactly, with only the two announcement code objects replaced. Its other 69 code objects and 57 other archive entries match the prior build. In-game speech verification remains pending.

Rollback: restore the previous TS4_Access.ts4script, or reverse CHANGES.patch and remove the cleanliness module. SOURCE-MANIFEST.json records exact source hashes.
