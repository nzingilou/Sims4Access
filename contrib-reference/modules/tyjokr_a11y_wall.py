"""Experimental, additive wall support for the TS4 Access Build grid.

The baseline modules are patched only in memory.  Removing this module and its
single import from ``tyjokr_a11y_contrib`` restores the original behavior.
"""

import threading
import time

import tyjokr_a11y_speech as speech


HEIGHTS = (
    ("very low", 0.5),
    ("low", 1.0),
    ("middle", 1.5),
    ("high", 2.0),
    ("very high", 2.5),
    ("near the top", 3.0),
)
HEIGHT_UP_KEY = 85  # U; unused by the baseline Ctrl+Alt chord map.
HEIGHT_DOWN_KEY = 85  # Shift+U lowers; Ctrl+Alt+D is catalog search in the update.

_height_index = 2
_original_build_place = None
_original_checks = None
_original_fit_parts = None
_original_wall_parts = None
_key_running = False
_key_thread = None


def _log(message):
    try:
        speech.log_line("wall: " + message)
    except Exception:
        pass


def _text(en, pl):
    try:
        import tyjokr_a11y_grid as grid
        return grid._text(en, pl)
    except Exception:
        return en


def _selected_height():
    return HEIGHTS[_height_index]


def _wall_state():
    import tyjokr_a11y_grid as grid
    import tyjokr_a11y_tiles as tiles
    frame = tiles.frame()
    if frame is None:
        return None
    i, j = grid._tile
    sides = tiles.walls(frame, i, j, grid._level)
    doors = tiles.doors(frame, i, j, grid._level)
    return frame, sides, doors


def _selected_wall():
    import tyjokr_a11y_grid as grid
    state = _wall_state()
    if state is None:
        return None
    frame, sides, doors = state
    side = int(grid._facing) % 4
    if side in doors or sides.get(side) != "wall":
        return None
    return frame, side


def _separates_rooms(frame, side):
    """Use room topology to avoid treating an ordinary fence as a wall."""
    import tyjokr_a11y_grid as grid
    import tyjokr_a11y_tiles as tiles
    i, j = grid._tile
    di, dj = tiles.STEPS[side]
    try:
        here = tiles.room(frame, i, j, grid._level)
        there = tiles.room(frame, i + di, j + dj, grid._level)
    except Exception as ex:
        _log("room boundary check failed: {!r}".format(ex))
        return False
    return here is not None and there is not None and here != there


def _wall_anchor(frame, side):
    import sims4.math
    import tyjokr_a11y_grid as grid
    import tyjokr_a11y_tiles as tiles
    i, j = grid._tile
    di, dj = tiles.STEPS[side]
    center = tiles.position(frame, i, j, grid._level)
    neighbor = frame.world(i + di, j + dj)
    label, height = _selected_height()
    point = sims4.math.Vector3(
        (float(center.x) + float(neighbor[0])) / 2.0,
        float(center.y) + height,
        (float(center.z) + float(neighbor[1])) / 2.0,
    )
    # A wall object on the selected edge faces back into the cursor's room.
    inward = (side + 2) % 4
    return point, frame.yaw(inward), label, height


def _wall_parts(frame, all_sides=False, objects=None):
    """Name wall sides explicitly while preserving door and edge distinctions."""
    import tyjokr_a11y_grid as grid
    import tyjokr_a11y_tiles as tiles
    i, j = grid._tile
    sides = tiles.walls(frame, i, j, grid._level)
    doors = tiles.doors(frame, i, j, grid._level, objects=objects)
    if all_sides:
        parts = []
        for index in range(4):
            if index in doors:
                state = _text("door", "drzwi")
            elif sides.get(index) == "blocked" and _separates_rooms(frame, index):
                state = _text("wall", "sciana")
            else:
                state = {
                    "blocked": _text("wall, or possibly a fence", "sciana lub prawdopodobnie plot"),
                    "object": _text("an object is in the way", "przeszkadza obiekt"),
                    "edge": _text("lot edge", "granica parceli"),
                    "open": _text("open", "wolne"),
                }.get(sides.get(index), _text("unknown", "nieznane"))
            parts.append("{}: {}. ".format(tiles.direction_name(index).capitalize(), state))
        return parts
    wall_dirs = [
        tiles.direction_name(index)
        for index in range(4)
        if sides.get(index) == "blocked"
        and index not in doors
        and _separates_rooms(frame, index)
    ]
    uncertain_dirs = [
        tiles.direction_name(index)
        for index in range(4)
        if sides.get(index) == "blocked"
        and index not in doors
        and not _separates_rooms(frame, index)
    ]
    door_dirs = [tiles.direction_name(index) for index in sorted(doors)]
    parts = []
    if wall_dirs:
        joined = _text(" and ", " i ").join(wall_dirs)
        if len(wall_dirs) == 1:
            parts.append(
                _text("Wall here, {} edge. ", "Sciana tutaj, krawedz {}. ").format(joined)
            )
        else:
            parts.append(
                _text("Walls here, {} edges. ", "Sciany tutaj, krawedzie {}. ").format(joined)
            )
    if uncertain_dirs:
        joined = _text(" and ", " i ").join(uncertain_dirs)
        parts.append(
            _text("Blocked edge here, {}, possibly a wall or fence. ",
                  "Zablokowana krawedz tutaj, {}, mozliwa sciana lub plot. ").format(joined)
        )
    if door_dirs:
        parts.append(
            _text("Door {}. ", "Drzwi: {}. ").format(_text(" and ", " i ").join(door_dirs))
        )
    return parts


def _wall_fit_parts(frame, with_facing=True):
    import tyjokr_a11y_grid as grid
    import tyjokr_a11y_place as place
    import tyjokr_a11y_tiles as tiles
    item = place.product()
    if item is None or place.requirement(item["id"]) != "wall":
        return _original_fit_parts(frame, with_facing=with_facing)
    side = int(grid._facing) % 4
    label, height = _selected_height()
    if _selected_wall() is None:
        return [
            _text(
                "Selected side has no wall. Turn with R or move to a tile beside a wall. Height {}, {:.1f} metres. ",
                "Po wybranej stronie nie ma sciany. Obracaj R albo przejdz obok sciany. Wysokosc {}, {:.1f} metra. ",
            ).format(label, height)
        ]
    return [
        _text(
            "Selected wall height {}, {:.1f} metres. Control Alt U raises and Control Alt Shift U lowers it. Enter places. ",
            "Wysokosc wybranej sciany {}, {:.1f} metra. Control Alt U podnosi, a Control Alt Shift U obniza. Enter umieszcza. ",
        ).format(label, height)
    ]


def _checks(position, level, key, guard):
    """Permit only the baseline's wall refusal to pass; retain every other check."""
    import tyjokr_a11y_place as place
    item = place.product()
    if item is None or place.requirement(item["id"]) != "wall":
        return _original_checks(position, level, key, guard)
    original_requirement = place.requirement
    try:
        place.requirement = lambda _def_id: None
        checked = _original_checks(position, level, key, guard)
    finally:
        place.requirement = original_requirement
    if checked is None:
        return None
    return checked[0], checked[1], "wall"


def _build_place():
    import tyjokr_a11y_grid as grid
    import tyjokr_a11y_place as place
    import tyjokr_a11y_tiles as tiles
    item = place.product()
    if item is None or place.requirement(item["id"]) != "wall":
        return _original_build_place()
    selected = _selected_wall()
    if selected is None:
        direction = tiles.direction_name(int(grid._facing) % 4)
        place._say_text(
            "There is no wall {}. Turn with R or move beside a wall.".format(direction),
            "Brak sciany w kierunku {}. Obracaj R albo przejdz obok sciany.".format(direction),
        )
        return False
    frame, side = selected
    try:
        point, angle, label, height = _wall_anchor(frame, side)
    except Exception as ex:
        _log("could not calculate wall anchor: {!r}".format(ex))
        place._say_text(
            "The wall anchor could not be calculated, so nothing was bought.",
            "Nie udalo sie obliczyc punktu na scianie, wiec nic nie kupiono.",
        )
        return False
    _log(
        "placing product {} on side {} at height {:.1f}".format(item["id"], side, height)
    )
    return place.place(point, grid._level, grid._surface(), angle=angle, exact=True)


def change_height(delta):
    global _height_index
    import tyjokr_a11y_grid as grid
    import tyjokr_a11y_place as place
    import tyjokr_a11y_tiles as tiles
    if not grid.build_cursor():
        return False
    item = place.product()
    if item is None or place.requirement(item["id"]) != "wall":
        return False
    _height_index = max(0, min(len(HEIGHTS) - 1, _height_index + (1 if delta > 0 else -1)))
    label, height = _selected_height()
    direction = tiles.direction_name(int(grid._facing) % 4)
    available = _selected_wall() is not None
    place._say_text(
        "Height {}, {:.1f} metres. {} {}.".format(
            label, height, "Wall" if available else "No wall", direction
        ),
        "Wysokosc {}, {:.1f} metra. {} {}.".format(
            label, height, "Sciana" if available else "Brak sciany", direction
        ),
    )
    return True


def _post_height(delta):
    try:
        import tyjokr_a11y_keys as keys
        if keys._editing_active or keys._modal_active:
            return
        import tyjokr_a11y_pump as pump
        pump.post(change_height, delta)
    except Exception as ex:
        _log("could not queue wall height change: {!r}".format(ex))


def _game_is_foreground(user32, kernel32, ctypes):
    try:
        hwnd = user32.GetForegroundWindow()
        if not hwnd:
            return False
        pid = ctypes.c_ulong()
        user32.GetWindowThreadProcessId(hwnd, ctypes.byref(pid))
        return pid.value == kernel32.GetCurrentProcessId()
    except Exception:
        return False


def _key_loop():
    try:
        import ctypes
        user32 = ctypes.WinDLL("user32")
        kernel32 = ctypes.WinDLL("kernel32")
    except Exception as ex:
        _log("wall height keys unavailable: {!r}".format(ex))
        return
    vk_control, vk_menu, vk_shift, vk_height = 17, 18, 16, HEIGHT_UP_KEY
    previous = False
    while _key_running:
        try:
            foreground = _game_is_foreground(user32, kernel32, ctypes)
            ctrl = bool(user32.GetAsyncKeyState(vk_control) & 32768)
            alt = bool(user32.GetAsyncKeyState(vk_menu) & 32768)
            shift = bool(user32.GetAsyncKeyState(vk_shift) & 32768)
            down = bool(user32.GetAsyncKeyState(vk_height) & 32768)
            if foreground and ctrl and alt and down and not previous:
                _post_height(-1 if shift else 1)
            previous = down
        except Exception as ex:
            _log("wall key polling failed: {!r}".format(ex))
        time.sleep(0.02)


def install():
    global _key_running
    global _key_thread
    global _original_build_place
    global _original_checks
    global _original_fit_parts
    global _original_wall_parts
    import tyjokr_a11y_grid as grid
    import tyjokr_a11y_place as place
    if getattr(grid, "_wall_contribution_installed", False):
        return
    _original_build_place = grid._build_place
    _original_fit_parts = grid._fit_parts
    _original_checks = place._checks
    grid._build_place = _build_place
    grid._fit_parts = _wall_fit_parts
    place._checks = _checks
    grid._wall_contribution_installed = True
    _key_running = True
    _key_thread = threading.Thread(target=_key_loop, name="ts4_access_wall_keys")
    _key_thread.daemon = True
    _key_thread.start()
    _log("wall contribution installed")


install()
