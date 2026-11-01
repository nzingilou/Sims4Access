# Developer manifest

Baseline: the supplied updated release. Python changes are additive except the existing appended contribution import in `tyjokr_a11y_scanner.pyc`.

- `tyjokr_a11y_contrib.py` (scanner scopes, move integration, optional-module loader).
- `tyjokr_a11y_contrib_settings.py` (saved contribution settings and flags).
- `tyjokr_a11y_wall.py`, `tyjokr_a11y_room_bridge.py` (wall anchors, wall sides, named rooms).
- `tyjokr_a11y_surfaces.py`, `tyjokr_a11y_layers.py` (validated surface requirements and layer focus; focus includes `tiles.children_on` contents, announces their parent, and exposes the selected parent or child to sell/move targeting).
- `tyjokr_a11y_chair_alignment.py` (announcement-only dining/desk chair relationship hints; `_fit_parts` wrapper and install marker).
- `tyjokr_a11y_roof_tools.py`, `tyjokr_a11y_house_planner.py`, `tyjokr_a11y_lot_grid.py`, `tyjokr_a11y_detached.py` (separate Build Helper additions; the runtime wrapper filters only the two superseded baseline labels, without modifying their functions).
- `TS4_Access_UI.package` is the update's original file; the experimental patch rebase is excluded because it broke scanner-to-pie-menu activation in game.

Rollback: restore the supplied `tyjokr_a11y_scanner.pyc` and UI package, then remove the eleven `tyjokr_a11y_*` contribution modules listed above.
