"""Additive surface-layer descriptions and safe object focus for the Build grid."""

import tyjokr_a11y_speech as speech


SETTING_KEY = "surface_layer_focus"
_mode = 3  # ground, six wall heights, ceiling; start at middle wall height.
_focus = {"obj_id": None, "tile": None, "level": None, "mode": None, "index": -1}
_original_detail = None
_original_sell_here = None
_original_change_height = None
_original_build_place = None
_original_finish = None
_surface_request = None


def _surface_slots(surface):
    try:
        return list(surface.get_runtime_slots_gen())
    except Exception:
        return []


def _finish_on_surface(obj, item, price, need, position, level, routing_surface, angle, key, exact=False):
    """Keep the baseline ownership/payment transaction and validate real slots."""
    global _surface_request
    import services
    import tyjokr_a11y_place as place
    request, _surface_request = _surface_request, None
    if request is None:
        return _original_finish(obj, item, price, need, position, level, routing_surface, angle, key, exact)
    serial, product, zone, target_id, target_key = request
    target = services.object_manager().get(target_id)
    if (place._pending['serial'] != serial or item['id'] != product
            or place._zone_id() != zone or key != target_key or target is None
            or target is not _focused_target()):
        place._destroy(obj)
        place._say_text("The selected surface changed. Nothing was bought.",
                        "Wybrana powierzchnia zmienila sie. Nic nie kupiono.")
        return False
    def selected_slot(candidate, _position, _level):
        if int(target.level) != int(_level) or target.is_in_inventory() or target.is_hidden():
            return None
        owner = target.get_household_owner_id()
        if owner and owner != place._household_id():
            return None
        if not services.active_lot().is_position_on_lot(target.position):
            return None
        for index, slot in enumerate(_surface_slots(target)):
            try:
                if not slot.empty:
                    _log("surface {} slot {} occupied".format(target_id, index))
                    continue
                # Decoration classification alone is not a compatibility
                # verdict. For an explicitly selected surface, ask the game.
                valid = slot.is_valid_for_placement(obj=candidate)
                _log("surface {} slot {} product {} validation={!r}".format(
                    target_id, index, product, valid))
                if valid:
                    return target, slot
            except Exception as ex:
                _log("surface {} slot {} validation error: {!r}".format(target_id, index, ex))
                continue
        return None
    if selected_slot(obj, position, level) is None:
        _log("focused surface {} has no compatible free slot for {}".format(target_id, product))
        place._destroy(obj)
        place._say_text("The focused surface has no compatible free slot for this object. Nothing was bought.",
                        "Wybrana powierzchnia nie ma zgodnego wolnego miejsca. Nic nie kupiono.")
        return False
    original_free_slot = place._free_slot
    try:
        place._free_slot = selected_slot
        return _original_finish(obj, item, price, 'slot', position, level, routing_surface, angle, key, exact)
    finally:
        place._free_slot = original_free_slot


def _enabled():
    try:
        import tyjokr_a11y_settings as settings
        return bool(settings.get(SETTING_KEY, True))
    except Exception:
        return True


def _log(message):
    try:
        speech.log_line("layers: " + message)
    except Exception:
        pass


def _text(en, pl):
    try:
        import tyjokr_a11y_grid as grid
        return grid._text(en, pl)
    except Exception:
        return en


def _mode_info():
    if _mode == 0:
        return "ground", _text("ground", "podloga"), None
    if _mode == 7:
        return "ceiling", _text("ceiling", "sufit"), None
    import tyjokr_a11y_wall as wall
    label, height = wall.HEIGHTS[_mode - 1]
    return "wall", _text("wall {}", "sciana {}").format(label), height


def _definition_id(obj):
    try:
        return int(obj.definition.id)
    except Exception:
        try:
            return int(obj.definition_id)
        except Exception:
            return None


def _kind(obj):
    try:
        import tyjokr_a11y_place as place
        need = place.requirement(_definition_id(obj))
    except Exception:
        need = None
    if need == "ceiling":
        return "ceiling"
    if need in ("wall", "fence"):
        return "wall"
    return "ground"


def _floor_y(frame, i, j, level):
    try:
        import tyjokr_a11y_tiles as tiles
        return float(tiles.position(frame, i, j, level).y)
    except Exception:
        return None


def _height(obj, floor_y):
    if floor_y is None:
        return None
    try:
        return max(0.0, float(obj.position.y) - floor_y)
    except Exception:
        return None


def _label(obj, frame=None, i=None, j=None, level=None):
    kind = _kind(obj)
    if kind == "ceiling":
        return _text("ceiling", "sufit")
    if kind == "wall":
        value = _height(obj, _floor_y(frame, i, j, level)) if frame is not None else None
        if value is not None:
            return _text("wall, {:.1f} metres", "sciana, {:.1f} metra").format(value)
        return _text("wall", "sciana")
    return _text("ground", "podloga")


def _matches(obj, frame, i, j, level):
    kind, _label_text, selected_height = _mode_info()
    if _kind(obj) != kind:
        return False
    if kind != "wall":
        return True
    value = _height(obj, _floor_y(frame, i, j, level))
    # Wall presets are 0.5 m apart.  A quarter-metre window avoids silently
    # selecting an object that belongs to a neighboring preset.
    return value is not None and abs(value - selected_height) <= 0.26


def _objects_here():
    import tyjokr_a11y_grid as grid
    import tyjokr_a11y_tiles as tiles
    frame = tiles.frame()
    if frame is None:
        return None, []
    i, j = grid._tile
    objects = [
        obj for obj in tiles.objects_on(frame, i, j, grid._level)
        if not getattr(obj, "is_sim", False)
    ]
    return frame, objects


def _focus_objects(objects):
    """Return tile objects followed by their attached contents."""
    import tyjokr_a11y_tiles as tiles
    result, seen = [], set()

    def add(obj, depth):
        obj_id = getattr(obj, "id", None)
        if obj_id is None or obj_id in seen or getattr(obj, "is_sim", False):
            return
        seen.add(obj_id)
        result.append(obj)
        if depth >= 4:
            return
        try:
            children = list(tiles.children_on(obj))
        except Exception:
            children = []
        children.sort(key=lambda child: int(getattr(child, "id", 0)))
        for child in children:
            add(child, depth + 1)

    for obj in sorted(objects, key=lambda item: int(getattr(item, "id", 0))):
        add(obj, 0)
    return result


def _name_parts(obj):
    import tyjokr_a11y_grid as grid
    value = grid._name(obj)
    return list(value) if isinstance(value, list) else [value]


def _clear_focus():
    _focus.update({"obj_id": None, "tile": None, "level": None, "mode": None, "index": -1})


def _focus_detail():
    import tyjokr_a11y_grid as grid
    import tyjokr_a11y_scanner as scanner
    frame, objects = _objects_here()
    if frame is None:
        return _original_detail(1)
    i, j = grid._tile
    matches = [obj for obj in _focus_objects(objects)
               if _matches(obj, frame, i, j, grid._level)]
    context = (grid._tile, grid._level, _mode)
    same = (_focus["tile"], _focus["level"], _focus["mode"]) == context
    index = ((_focus["index"] + 1) % len(matches)) if same and matches else 0
    if not matches:
        _clear_focus()
        parts = [
            _text("Nothing at the selected {} layer. ", "Brak obiektow na wybranej warstwie {}. ").format(_mode_info()[1])
        ]
        if objects:
            parts.append(_text("Objects here: ", "Obiekty tutaj: "))
            parts.extend(grid._object_parts(frame, objects))
        else:
            parts.append(_text("Nothing here.", "Nic tu nie ma."))
        scanner._speak_parts(parts)
        return True
    obj = matches[index]
    _focus.update({"obj_id": obj.id, "tile": grid._tile, "level": grid._level,
                   "mode": _mode, "index": index})
    parts = [_text("Focused: ", "Wybrano: ")]
    parts.extend(_name_parts(obj))
    parent = getattr(obj, "parent", None)
    if parent is not None:
        parts.append(_text(", on ", ", na "))
        parts.extend(_name_parts(parent))
    parts.extend([", ", _label(obj, frame, i, j, grid._level), ". "])
    if len(matches) > 1:
        parts.append(_text("Object {} of {}; press 1 again for the next. ",
                           "Obiekt {} z {}; nacisnij ponownie 1, aby przejsc dalej. ").format(index + 1, len(matches)))
    # Preserve the baseline meaning of detail key 1 in full.  Its own helper
    # supplies child/contents and free surface-slot information for every
    # object on the tile; focus is additional state, not a replacement report.
    parts.append(_text("Objects here: ", "Obiekty tutaj: "))
    parts.extend(grid._object_parts(frame, objects))
    scanner._speak_parts(parts)
    return True


def _nearby_detail():
    import tyjokr_a11y_grid as grid
    import tyjokr_a11y_scanner as scanner
    import tyjokr_a11y_tiles as tiles
    frame = tiles.frame()
    if frame is None:
        return _original_detail(4)
    i, j = grid._tile
    nearby = []
    for di in range(-tiles.NEARBY_RADIUS, tiles.NEARBY_RADIUS + 1):
        for dj in range(-tiles.NEARBY_RADIUS, tiles.NEARBY_RADIUS + 1):
            if (di, dj) != (0, 0) and not frame.inside(i + di, j + dj):
                continue
            try:
                for obj in tiles.objects_on(frame, i + di, j + dj, grid._level):
                    nearby.append((di * di + dj * dj, di, dj, obj))
            except Exception:
                continue
    parts, seen, count = [], set(), 0
    for _distance, di, dj, obj in sorted(nearby, key=lambda item: item[0]):
        if obj.id in seen:
            continue
        seen.add(obj.id)
        parts.extend(_name_parts(obj))
        parts.extend([", ", _label(obj, frame, i + di, j + dj, grid._level), ", ",
                      tiles.relative(di, dj), ". "])
        count += 1
        if count >= 8:
            break
    if not count:
        parts = [_text("Nothing within {} tiles.", "Nic w promieniu {} pol.").format(tiles.NEARBY_RADIUS)]
    scanner._speak_parts(parts)
    return True


def _detail(topic):
    if not _enabled():
        return _original_detail(topic)
    if topic == 1:
        return _focus_detail()
    if topic == 4:
        return _nearby_detail()
    return _original_detail(topic)


def _focused_target():
    import services
    import tyjokr_a11y_grid as grid
    if (_focus["obj_id"] is None or _focus["tile"] != grid._tile or
            _focus["level"] != grid._level or _focus["mode"] != _mode):
        return None
    obj = services.object_manager().get(_focus["obj_id"])
    if obj is None:
        _clear_focus()
        return None
    frame, objects = _objects_here()
    candidates = _focus_objects(objects) if frame is not None else []
    if frame is None or all(candidate.id != obj.id for candidate in candidates):
        _clear_focus()
        return None
    return obj


def _base_target():
    """Mirror this update's current _sell_here object ordering."""
    import tyjokr_a11y_grid as grid
    try:
        objects = [obj for obj in grid._objects_at_origin()
                   if not getattr(obj, "is_sim", False)]
        objects.sort(key=grid._parent_depth, reverse=True)
        return objects[0] if objects else None
    except Exception:
        return None


def _sell_target():
    if _enabled():
        obj = _focused_target()
        if obj is not None:
            return obj
    return _base_target()


def _sell_here():
    import tyjokr_a11y_place as place
    return place.sell(_sell_target())


def _build_place():
    """Refuse a wall placement when the announced target is not a wall band."""
    import tyjokr_a11y_place as place
    import tyjokr_a11y_grid as grid
    global _surface_request
    item = place.product()
    target = _focused_target() if _enabled() else None
    if item is not None and target is not None and place.requirement(item['id']) in (None, 'slot'):
        slots = _surface_slots(target)
        if slots:
            cursor = grid.cursor()
            if cursor is None:
                return False
            position, level, _ident = cursor
            # Capture the actual acknowledgement serial; never select a nearby
            # alternative or fall back to buying this object on the floor.
            if place._pending['args'] is not None:
                return place.place(position, level, grid._surface())
            _surface_request = (place._pending['serial'] + 1, item['id'], place._zone_id(),
                                target.id, place.tile_key(position, level))
            accepted = place.place(position, level, grid._surface())
            if not accepted:
                _surface_request = None
            return accepted
    _surface_request = None
    if (_enabled() and item is not None and place.requirement(item["id"]) == "wall"
            and _mode_info()[0] != "wall"):
        place._say_text(
            "Select a wall-height target with Control Alt U or Control Alt Shift U before placing this wall object.",
            "Przed umieszczeniem obiektu sciennego wybierz wysokosc sciany przez Control Alt U lub Control Alt Shift U.",
        )
        return False
    return _original_build_place()


def change_layer(delta):
    global _mode
    import tyjokr_a11y_grid as grid
    import tyjokr_a11y_place as place
    import tyjokr_a11y_wall as wall
    if not grid.build_cursor():
        return False
    if not _enabled():
        return _original_change_height(delta)
    _mode = max(0, min(7, _mode + (1 if delta > 0 else -1)))
    _clear_focus()
    kind, label, height = _mode_info()
    if kind == "wall":
        wall._height_index = _mode - 1
        place._say_text("Target layer: {}, {:.1f} metres. Press 1 to focus an object here.".format(label, height),
                        "Warstwa docelowa: {}, {:.1f} metra. Nacisnij 1, aby wybrac obiekt.".format(label, height))
    else:
        place._say_text("Target layer: {}. Press 1 to focus an object here.".format(label),
                        "Warstwa docelowa: {}. Nacisnij 1, aby wybrac obiekt.".format(label))
    return True


def install():
    global _original_detail, _original_sell_here, _original_change_height, _original_build_place
    import tyjokr_a11y_grid as grid
    import tyjokr_a11y_wall as wall
    import tyjokr_a11y_place as place
    global _original_finish
    if getattr(grid, "_layer_focus_installed", False):
        return
    _original_detail = grid._detail
    _original_sell_here = grid._sell_here
    _original_build_place = grid._build_place
    _original_change_height = wall.change_height
    _original_finish = place._finish
    place._finish = _finish_on_surface
    grid._detail = _detail
    grid._sell_here = _sell_here
    grid._sell_target = _sell_target
    grid._build_place = _build_place
    wall.change_height = change_layer
    grid._layer_focus_installed = True
    _log("surface-layer descriptions and guarded focus installed")


install()
