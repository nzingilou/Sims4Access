# Changes

- Add experimental dining/desk chair snapping to native seats, with attachment verification before payment and a separate settings toggle.

- Update to upstream adb868c (12 November): native contribution integration, wall-tool improvements, revised controls/settings and holiday announcements.
- Retire duplicate scanner, wall, layer, surface and settings adapters. Keep remaining local extensions behind one simulation-thread startup hook.
- Preserve attached-object cycling, focused-surface placement, chair hints and inferred/custom room names in the integrated modules.
- Expose scenario cards and native Play controls; read native descriptions, difficulty, requirements, roles and goals.
- Add native apartment-map selection and traverse nested rental-property region/building controls.
- Retain the house/roof/lot helpers, coordinate and floor fixes, cleaning/away actions, event-goal reader and earlier UI repairs.

- Speech fallback: prevent orphaned PowerShell helpers on parent exit/crash; serialize startup and reap/close children on restart.
