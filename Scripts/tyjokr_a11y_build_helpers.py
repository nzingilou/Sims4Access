"""Narrow integration fixes for the existing house/structure helpers."""
import contextlib
import math
import time

_build = None
_coordinates = None


def _log(kind, **data):
    import tyjokr_a11y_speech as speech
    import json
    speech.log_line('build helpers: ' + json.dumps(dict(kind=kind, **data), sort_keys=True, default=str))


def _state():
    import services
    import tyjokr_a11y_grid as grid
    import tyjokr_a11y_keys as keys
    if not _build.in_build_mode() or keys.blocking_active() or keys._editing_active:
        raise RuntimeError('Close the game dialog before changing floors')
    lot = services.active_lot()
    if lot is None: raise RuntimeError('No active lot')
    floor = _build.current_floor()
    if floor is None: raise RuntimeError('The game has not reported its current floor')
    return {'zone': int(services.current_zone_id()), 'floor': int(floor),
            'center': (float(lot.center.x), float(lot.center.z)),
            'grid': bool(grid.build_cursor()), 'owner': bool(keys._build_grid_owner)}


def _same_world(state):
    import services
    import tyjokr_a11y_keys as keys
    return (_build.in_build_mode() and int(services.current_zone_id()) == state['zone']
            and not keys.blocking_active() and not keys._editing_active)


def _grid_message(message):
    import tyjokr_a11y_grid as grid
    grid._flash(message)


def _grid_released():
    import tyjokr_a11y_keys as keys
    return not keys._build_grid_owner


def _restore_grid(state):
    import services
    import tyjokr_a11y_grid as grid
    if (state['grid'] and _build.in_build_mode() and
            int(services.current_zone_id()) == state['zone'] and grid.build_cursor()):
        grid._flash('A11yBuildGridOn')
        return True
    return False


@contextlib.contextmanager
def _floor_input(state):
    u = _coordinates._api()
    sent_off = False
    try:
        with _coordinates.physical_context(u):
            geometry = _coordinates.window(u)
            if state['grid'] or state['owner']:
                # Only release native key ownership. Preserve the Python grid's
                # tile, height, room focus, orientation and enabled setting.
                sent_off = True
                _build.on_main(_grid_message, 'A11yBuildGridOff')
                # A fresh native request is an ordered UI round trip after Off.
                # It does not move any cursor or click. Never inject a floor key
                # before the native guard and script owner have both released.
                _coordinates._measure(state['center'][0], state['center'][1], state['floor'])
                deadline = time.monotonic() + 2.0
                while not _build.on_main(_grid_released):
                    if time.monotonic() >= deadline: raise RuntimeError('Grid ownership did not release')
                    time.sleep(.02)
                _log('floor-ownership-released', zone=state['zone'])
            yield u, geometry
    finally:
        if sent_off:
            restored = _build.on_main(_restore_grid, state)
            _log('floor-ownership-restored', zone=state['zone'], restored=bool(restored))


def set_floor(level):
    """Change the native floor without feeding Page Up/Down to the grid."""
    try:
        if isinstance(level, bool) or not isinstance(level, (int, float)) or not math.isfinite(level) or int(level) != level:
            return False
        level = int(level)
    except (ValueError, OverflowError):
        return False
    try:
        state = _build.on_main(_state)
        if state is None: raise RuntimeError('Simulation thread did not answer')
        if state['floor'] == level: return True
        with _floor_input(state) as (u, geometry):
            unchanged = 0
            previous = state['floor']
            for _ in range(min(64, 3 * (abs(level - previous) + 1))):
                if _coordinates.window(u) != geometry or not _build.on_main(_same_world, state):
                    raise RuntimeError('Game focus, window or Build context changed')
                if not _build.on_main(_grid_released):
                    raise RuntimeError('The grid reclaimed the floor keys')
                if any(u.GetAsyncKeyState(key) & 0x8000 for key in (16,17,18,91,92)):
                    raise RuntimeError('Release modifier keys before changing floors')
                current = _build.on_main(_build.current_floor)
                if current is None: raise RuntimeError('Native floor unavailable')
                if current == level:
                    _log('floor-confirmed', wanted=level, actual=current)
                    return True
                key, scan = (33, 0x49) if current < level else (34, 0x51)
                if (not _build.on_main(_same_world, state) or _coordinates.window(u) != geometry
                        or u.GetAsyncKeyState(key) & 0x8000):
                    raise RuntimeError('Input context changed before the floor key')
                pressed = False
                try:
                    u.keybd_event(key, scan, 1, 0); pressed = True
                    time.sleep(.05)
                finally:
                    if pressed: u.keybd_event(key, scan, 3, 0)
                time.sleep(1.25)
                actual = _build.on_main(_build.current_floor)
                _log('floor-step', wanted=level, before=current, actual=actual)
                unchanged = unchanged + 1 if actual == current else 0
                if actual == level: return True
                if actual is None or unchanged >= 3: return False
            return False
    except Exception as exc:
        _log('floor-refused', wanted=level, error=str(exc))
        return False


def _build_menu():
    import tyjokr_a11y_plus_build as build
    return build.open_menu()


def install():
    global _build, _coordinates
    import tyjokr_a11y_plus_build as build
    import tyjokr_a11y_plus_core as core
    import tyjokr_a11y_build_coordinates as coordinates
    if getattr(build, '_helper_integration_installed', False): return
    _build, _coordinates = build, coordinates
    build.set_floor = set_floor
    # Roof tools registered Alt+B before the detached wrapper loaded. Resolve
    # the final menu when invoked, so every later wrapper is included once.
    current = core.HOTKEYS.get(ord('B'))
    if current is not None:
        core.HOTKEYS[ord('B')] = (_build_menu, current[1])
    build._helper_integration_installed = True
    _log('installed')
