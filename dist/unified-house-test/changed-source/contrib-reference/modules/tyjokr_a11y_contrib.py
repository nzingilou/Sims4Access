"""Narrow contribution layer for TS4 Access.

This module is intentionally additive.  The packaged TS4 Access modules remain
byte-for-byte unchanged except for one import appended to the scanner module.
That makes removing this file (and the appended import) a complete rollback.
"""

import threading
import time

import tyjokr_a11y_speech as speech
import tyjokr_a11y_contrib_settings as contrib_settings


_SCOPE_MODES = (
    ("6 meters", 6.0, "distance"),
    ("12 meters", 12.0, "distance"),
    ("24 meters", 24.0, "distance"),
    ("40 meters", 40.0, "distance"),
    ("whole lot", None, "lot"),
    ("this floor", None, "floor"),
    ("this room", None, "room"),
)
_saved_scope = str(contrib_settings.value(contrib_settings.SCOPE_KEY) or "40 meters").lower()
_scope_index = next(
    (index for index, mode in enumerate(_SCOPE_MODES) if mode[0] == _saved_scope), 3
)
_original_scan = None
_original_scanner_on_key = None
_original_grid_on_key = None
_move = {"obj_id": None, "name": None}
_key_thread = None
_key_running = False


def _log(message):
    try:
        speech.log_line("contrib: " + message)
    except Exception:
        pass


def _scope():
    return _SCOPE_MODES[_scope_index]


def _object_for_entry(entry):
    try:
        import services
        obj = services.object_manager().get(entry.obj_id)
        if obj is not None:
            return obj
        info = services.sim_info_manager().get(entry.obj_id)
        if info is not None:
            return info.get_sim_instance()
    except Exception:
        return None


def _on_active_lot(obj):
    try:
        import services
        return bool(services.active_lot().is_position_on_lot(obj.position))
    except Exception:
        return False


def _room_id(obj):
    try:
        import build_buy
        import services
        return build_buy.get_room_id(
            services.current_zone_id(), obj.position, int(getattr(obj, "level", 0) or 0)
        )
    except Exception:
        return None


def _matches_scope(entry, active_room):
    _label, limit, kind = _scope()
    if limit is not None:
        # The baseline scanner deliberately lists every instantiated Sim,
        # regardless of its distance.  Preserve that accessibility behavior
        # for metre-based scopes while continuing to range-filter objects.
        if bool(getattr(entry, "is_sim", False)):
            return True
        return entry.distance <= limit
    obj = _object_for_entry(entry)
    if obj is None:
        return entry.distance == 0
    if not _on_active_lot(obj):
        return False
    if kind == "lot":
        return True
    if kind == "floor":
        return entry.level_delta == 0
    if entry.level_delta != 0 or active_room is None:
        return False
    return _room_id(obj) == active_room


def _apply_scope(scanner):
    active_room = None
    if _scope()[2] == "room":
        try:
            import services
            active_room = _room_id(services.get_active_sim())
        except Exception:
            active_room = None
    for key in list(scanner._by_group):
        entries = [entry for entry in scanner._by_group[key] if _matches_scope(entry, active_room)]
        if entries:
            scanner._by_group[key] = entries
        else:
            scanner._by_group.pop(key, None)
    scanner._groups = [key for key in scanner._groups if scanner._by_group.get(key)]
    scanner._group_index = min(scanner._group_index, max(0, len(scanner._groups) - 1))
    entries = scanner._entries()
    scanner._item_index = min(scanner._item_index, max(0, len(entries) - 1))


def _selection(scanner):
    """Read scanner focus without calling _current(), which can itself rescan."""
    groups = list(getattr(scanner, "_groups", ()))
    if not groups:
        return None, getattr(scanner, "_tree_level", "groups"), None, None, 0
    group_index = int(getattr(scanner, "_group_index", 0)) % len(groups)
    group = groups[group_index]
    entries = list(getattr(scanner, "_by_group", {}).get(group, ()))
    item_index = int(getattr(scanner, "_item_index", 0))
    entry = entries[item_index % len(entries)] if entries else None
    return (
        group,
        getattr(scanner, "_tree_level", "groups"),
        getattr(entry, "category", None),
        getattr(entry, "obj_id", None),
        item_index,
    )


def _restore_selection(scanner, saved):
    """Keep the same tree level/category/item after the scope filter is applied."""
    group, tree_level, category, obj_id, old_index = saved
    groups = list(getattr(scanner, "_groups", ()))
    if not groups:
        scanner._group_index = 0
        scanner._item_index = 0
        scanner._tree_level = "groups"
        return
    if group in groups:
        scanner._group_index = groups.index(group)
    else:
        scanner._group_index = min(int(getattr(scanner, "_group_index", 0)), len(groups) - 1)
    selected_group = groups[scanner._group_index]
    entries = list(getattr(scanner, "_by_group", {}).get(selected_group, ()))
    if not entries:
        scanner._item_index = 0
        scanner._tree_level = "groups"
        return
    wanted = next((index for index, entry in enumerate(entries) if entry.obj_id == obj_id), None)
    if wanted is None and category is not None:
        wanted = next((index for index, entry in enumerate(entries) if entry.category == category), None)
    scanner._item_index = wanted if wanted is not None else min(old_index, len(entries) - 1)
    # Never promote the user to a parent level merely because a refresh removed
    # or reordered entries.  The baseline scanner owns all other tree behavior.
    scanner._tree_level = tree_level
    entry = entries[scanner._item_index]
    try:
        scanner._tree_groups[selected_group] = entry.category
        scanner._tree_items[(selected_group, entry.category)] = entry.obj_id
    except Exception:
        pass


def _scoped_scan(preserve=False):
    import tyjokr_a11y_scanner as scanner
    saved = _selection(scanner) if preserve else None
    _label, limit, _kind = _scope()
    scanner.MAX_DISTANCE = limit if limit is not None else 1000000.0
    result = _original_scan(preserve)
    if result:
        _apply_scope(scanner)
        if preserve and saved is not None:
            _restore_selection(scanner, saved)
    return result


def cycle_scope(delta):
    global _scope_index
    import tyjokr_a11y_scanner as scanner
    if not scanner.enabled():
        speech.speak("Scanner is off.", explicit=True)
        return False
    _scope_index = (_scope_index + (1 if delta > 0 else -1)) % len(_SCOPE_MODES)
    try:
        import tyjokr_a11y_settings as settings
        settings.set(contrib_settings.SCOPE_KEY, _scope()[0])
    except Exception as ex:
        _log("scanner range could not be saved: {!r}".format(ex))
    if not scanner._scan(preserve=True):
        speech.speak("No lot loaded.", explicit=True)
        return False
    label = _scope()[0]
    parts = ["Scanner range: {}. ".format(label)]
    parts.extend(scanner._tree_parts())
    scanner._speak_parts(parts)
    _log("scanner range changed to {}".format(label))
    return True


def set_scope(label, refresh=False):
    global _scope_index
    wanted = str(label or "").strip().lower()
    index = next((i for i, mode in enumerate(_SCOPE_MODES) if mode[0] == wanted), None)
    if index is None:
        return False
    _scope_index = index
    if refresh:
        try:
            import tyjokr_a11y_scanner as scanner
            if scanner.enabled():
                scanner._scan(preserve=True)
        except Exception as ex:
            _log("saved scanner range refresh failed: {!r}".format(ex))
    return True


def _scanner_on_key(intent, on_simulation_thread=False):
    if intent == "scopeprev":
        return cycle_scope(-1)
    if intent == "scopenext":
        return cycle_scope(1)
    return _original_scanner_on_key(intent, on_simulation_thread=on_simulation_thread)


def _object_name(obj):
    try:
        import tyjokr_a11y_grid as grid
        value = grid._name(obj)
        if isinstance(value, list):
            return "".join(str(part) for part in value)
        return str(value)
    except Exception:
        return "object"


def _clear_move():
    _move["obj_id"] = None
    _move["name"] = None


def _move_key():
    import services
    import tyjokr_a11y_grid as grid
    import tyjokr_a11y_place as place
    if not grid.build_cursor():
        return False
    if _move["obj_id"] is None:
        obj = grid._sell_target()
        if obj is None:
            place._say_text("Nothing here to move.", "Nie ma tu nic do przesuniecia.")
            return False
        refusal = place.sell_refusal(obj)
        if refusal is not None:
            place._say_text(*place._CANNOT_SELL[refusal])
            return False
        if getattr(obj, "parent", None) is not None:
            place._say_text(
                "Objects attached to another object cannot be moved from the grid yet.",
                "Obiektow przymocowanych do innego obiektu nie mozna jeszcze przesuwac z siatki.",
            )
            return False
        _move["obj_id"] = obj.id
        _move["name"] = _object_name(obj)
        place._say_text(
            "{} selected to move. Navigate to a new tile and press M again. Escape cancels.".format(_move["name"]),
            "Wybrano {} do przesuniecia. Przejdz do nowego pola i ponownie nacisnij M. Escape anuluje.".format(_move["name"]),
        )
        return True
    obj = services.object_manager().get(_move["obj_id"])
    name = _move["name"] or "Object"
    if obj is None:
        _clear_move()
        place._say_text("The selected object is no longer available.", "Wybrany obiekt nie jest juz dostepny.")
        return False
    target = grid.cursor()
    if target is None:
        place._say_text("This tile cannot take the object.", "To pole nie moze przyjac obiektu.")
        return False
    position, level, _ident = target
    try:
        old_position = obj.position
        old_orientation = obj.orientation
        old_surface = obj.routing_surface
        spot = place._good_location(obj, position, old_orientation, grid._surface(), ignore=(obj.id,))
        if spot is None:
            place._say_text("No valid position was found here.", "Nie znaleziono tutaj prawidlowej pozycji.")
            return False
        obj.move_to(translation=spot[0], orientation=spot[1], routing_surface=grid._surface())
        if int(getattr(obj, "level", level)) != int(level):
            raise RuntimeError("object stayed on another floor")
    except Exception as ex:
        restored = False
        try:
            obj.move_to(translation=old_position, orientation=old_orientation, routing_surface=old_surface)
            restored = True
        except Exception as rollback_error:
            _log("move rollback failed: {!r}".format(rollback_error))
        _log("move failed for {}: {!r}".format(_move["obj_id"], ex))
        if restored:
            place._say_text("The object could not be moved; its original position was restored.", "Nie udalo sie przesunac obiektu; przywrocono pierwotne polozenie.")
        else:
            _clear_move()
            place._say_text("The move failed and its original position could not be restored. Check the object before continuing.", "Przesuniecie i przywrocenie polozenia nie powiodlo sie. Sprawdz obiekt przed kontynuowaniem.")
        return False
    _clear_move()
    place._say_text("{} moved.".format(name), "Przesunieto {}.".format(name))
    return True


def _grid_on_key(intent):
    if intent == "moveobject":
        return _move_key()
    if intent in ("back", "off"):
        was_moving = _move["obj_id"] is not None
        _clear_move()
        if was_moving:
            try:
                import tyjokr_a11y_place as place
                place._say_text("Move cancelled.", "Anulowano przesuwanie.")
            except Exception:
                pass
    return _original_grid_on_key(intent)


def _post_scope(delta):
    try:
        import tyjokr_a11y_keys as keys
        if keys._editing_active or keys._modal_active:
            return
        import tyjokr_a11y_pump as pump
        pump.post(cycle_scope, delta)
    except Exception as ex:
        _log("could not queue scanner range change: {!r}".format(ex))


def _post_move():
    try:
        import tyjokr_a11y_keys as keys
        if keys._editing_active or keys._modal_active:
            return
        import tyjokr_a11y_grid as grid
        if not grid.build_cursor():
            return
        import tyjokr_a11y_pump as pump
        pump.post(grid.on_key, "moveobject")
    except Exception as ex:
        _log("could not queue object move: {!r}".format(ex))


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
    global _key_running
    try:
        import ctypes
        user32 = ctypes.WinDLL("user32")
        kernel32 = ctypes.WinDLL("kernel32")
    except Exception as ex:
        _log("contribution keys unavailable: {!r}".format(ex))
        return
    VK_CONTROL, VK_MENU = 17, 18
    VK_COMMA, VK_PERIOD, VK_M = 188, 190, 77
    previous = {VK_COMMA: False, VK_PERIOD: False, VK_M: False}
    while _key_running:
        try:
            foreground = _game_is_foreground(user32, kernel32, ctypes)
            ctrl = bool(user32.GetAsyncKeyState(VK_CONTROL) & 32768)
            alt = bool(user32.GetAsyncKeyState(VK_MENU) & 32768)
            for vk in previous:
                down = bool(user32.GetAsyncKeyState(vk) & 32768)
                if foreground and down and not previous[vk]:
                    if ctrl and not alt and vk == VK_COMMA:
                        _post_scope(-1)
                    elif ctrl and not alt and vk == VK_PERIOD:
                        _post_scope(1)
                    elif not ctrl and not alt and vk == VK_M:
                        _post_move()
                previous[vk] = down
        except Exception as ex:
            _log("contribution key polling failed: {!r}".format(ex))
        time.sleep(0.02)


def install():
    global _key_running
    global _key_thread
    global _original_grid_on_key
    global _original_scan
    global _original_scanner_on_key
    import tyjokr_a11y_grid as grid
    import tyjokr_a11y_scanner as scanner
    if getattr(scanner, "_contribution_installed", False):
        return
    _original_scan = scanner._scan
    _original_scanner_on_key = scanner.on_key
    _original_grid_on_key = grid.on_key
    scanner._scan = _scoped_scan
    scanner.on_key = _scanner_on_key
    grid.on_key = _grid_on_key
    scanner._contribution_installed = True
    _key_running = True
    _key_thread = threading.Thread(target=_key_loop, name="ts4_access_contribution_keys")
    _key_thread.daemon = True
    _key_thread.start()
    try:
        import tyjokr_a11y_wall
    except Exception as ex:
        _log("wall contribution did not load: {!r}".format(ex))
    try:
        import tyjokr_a11y_room_bridge
    except Exception as ex:
        _log("room label contribution did not load: {!r}".format(ex))
    try:
        import tyjokr_a11y_surfaces
    except Exception as ex:
        _log("experimental surface placement did not load: {!r}".format(ex))
    try:
        import tyjokr_a11y_layers
    except Exception as ex:
        _log("surface-layer focus did not load: {!r}".format(ex))
    try:
        import tyjokr_a11y_chair_alignment
    except Exception as ex:
        _log("chair alignment hints did not load: {!r}".format(ex))
    try:
        import tyjokr_a11y_roof_tools
    except Exception as ex:
        _log("roof and build-description tools did not load: {!r}".format(ex))
    try:
        import tyjokr_a11y_house_planner
    except Exception as ex:
        _log("stacked house planner did not load: {!r}".format(ex))
    try:
        import tyjokr_a11y_lot_grid
    except Exception as ex:
        _log("lot planning grid did not load: {!r}".format(ex))
    try:
        import tyjokr_a11y_detached
    except Exception as ex:
        _log("detached structure planner did not load: {!r}".format(ex))
    try:
        import tyjokr_a11y_build_coordinates
        tyjokr_a11y_build_coordinates.install()
    except Exception as ex:
        _log("measured build coordinates did not load: {!r}".format(ex))
    try:
        import tyjokr_a11y_build_helpers
        tyjokr_a11y_build_helpers.install()
    except Exception as ex:
        _log("build helper integration did not load: {!r}".format(ex))
    try:
        import tyjokr_a11y_basement
        tyjokr_a11y_basement.install()
    except Exception as ex:
        _log("experimental basement adapter did not load: {!r}".format(ex))
    try:
        import tyjokr_a11y_house_workflow
        tyjokr_a11y_house_workflow.install()
    except Exception as ex:
        _log("unified house workflow did not load: {!r}".format(ex))
    _log("narrow contribution layer installed")


install()
