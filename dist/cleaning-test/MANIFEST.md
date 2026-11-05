# Developer manifest

- Scripts/tyjokr_a11y_ground.py: native floor pick, current story and floor-height query, input guards and request/error logging.
- Scripts/tyjokr_a11y_hub.py, around lines 174 and 704: one callback and one menu row.
- diagnostics/tyjokr_a11y_cleaning_diagnostic.py: separate command, object-state metadata, bounds, batching and cancellation.
- tools/test_ground_actions.py, test_cleaning_diagnostic.py and test_scanner_pick_bridge.js: guards, read-only behavior, menu integration and native transport.

113 suites, 1525 reported checks: passed, stable inputs. Compiled package import checks passed. The installed hub matched the reviewed source under release optimization; 43 other hub functions match. Only hub bytecode changes in the main archive; ground bytecode is added; all 56 other existing entries are identical. Exact hashes are in BUILD-HASHES.json.

Floor-menu vacuum scope and diagnostic execution still require in-game confirmation. Dirty scanner labels follow after actual cleaning-state identities are verified. Rollback details are in README.txt and CHANGES.patch.
