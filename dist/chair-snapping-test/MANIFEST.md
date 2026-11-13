# Changes from 432f0480794a8c08140901ea0c38cda3c5a22364

- chair_snap.py: native seat targeting, preview and exact-slot revalidation.
- grid.py: _fit_parts and _build_place dispatch.
- place.py: place, _finish, _after_payment integrate attachment validation before payment.
- settings.py/menu.py: experimental chair-snapping setting.
- chair_alignment.py: suppress duplicate orientation hints.
- Tests: 23 chair cases; ordinary cursor fixture delegates chair behavior to those tests.

Rollback: restore the base script. Live placement testing pending.
