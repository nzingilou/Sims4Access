"""Bridge TS4 Access Plus room names into the standard Build grid."""
import time
import tyjokr_a11y_speech as speech

_original_room_parts = None
_original_wall_parts = None
_cache_at = 0.0
_cache = {}
_cache_zone = None

def _log(message):
    try: speech.log_line("room bridge: " + message)
    except Exception: pass

def _room_map(refresh=False):
    global _cache_at, _cache, _cache_zone
    import services
    zone = services.current_zone_id()
    if zone != _cache_zone:
        _cache, _cache_at, _cache_zone = {}, 0.0, zone
    now = time.monotonic()
    if refresh or now - _cache_at > 2.0:
        try:
            import tyjokr_a11y_plus_rooms as plus_rooms
            _cache = {(int(room.rid), int(room.level)): room.name for room in plus_rooms.scan_rooms()}
            _cache_at = now
        except Exception as ex: _log("lookup failed: {!r}".format(ex))
    return _cache

def _at(frame, i, j, level, names):
    import tyjokr_a11y_tiles as tiles
    try:
        if tiles.ground(frame, i, j, level).get("outside"): return "outside"
        rid = tiles.room(frame, i, j, level)
        return names.get((int(rid), int(level)), "room") if rid is not None else "room"
    except Exception: return "room"

def _room_parts(frame):
    import tyjokr_a11y_grid as grid
    before = tuple(grid._last_room)
    parts, facts = _original_room_parts(frame)
    previous_room, previous_outside = before
    current_room, current_outside = grid._last_room
    changed = ((previous_outside is not None and current_outside is not None and current_outside != previous_outside)
               or (previous_room is not None and current_room is not None and current_room != previous_room and not current_outside))
    if changed and not current_outside and current_room is not None:
        name = _room_map(refresh=True).get((int(current_room), int(grid._level)))
        if name: parts = [grid._text("Entering {}. ", "Wchodzisz do: {}. ").format(name)]
    return parts, facts

def _wall_parts(frame, all_sides=False, objects=None):
    import tyjokr_a11y_grid as grid
    import tyjokr_a11y_tiles as tiles
    import inspect
    arguments = {"all_sides": all_sides}
    if "objects" in inspect.signature(_original_wall_parts).parameters:
        arguments["objects"] = objects
    parts = list(_original_wall_parts(frame, **arguments))
    if all_sides: return parts
    i, j = grid._tile
    sides, doors, names = tiles.walls(frame, i, j, grid._level), tiles.doors(frame, i, j, grid._level), _room_map()
    here = _at(frame, i, j, grid._level, names)
    for side in range(4):
        if sides.get(side) != "wall" or side in doors: continue
        di, dj = tiles.STEPS[side]
        there = _at(frame, i + di, j + dj, grid._level, names)
        direction = tiles.direction_name(side).capitalize()
        if here != there:
            parts.append(grid._text("{} wall, {} side facing {}. ", "Sciana {}, strona {} w kierunku {}. ").format(direction, here, there))
        else:
            parts.append(grid._text("{} wall, {} side. ", "Sciana {}, strona {}. ").format(direction, here))
    return parts

def install():
    global _original_room_parts, _original_wall_parts
    import tyjokr_a11y_grid as grid
    if getattr(grid, "_plus_room_bridge_installed", False): return
    _original_room_parts, _original_wall_parts = grid._room_parts, grid._wall_parts
    grid._room_parts, grid._wall_parts = _room_parts, _wall_parts
    grid._plus_room_bridge_installed = True
    _log("native Plus room names connected to Build grid")

install()
