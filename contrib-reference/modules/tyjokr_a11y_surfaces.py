"""Experimental, independently switchable surface-placement adapters.

The original modules remain unchanged on disk. Each path reuses the baseline
transaction and requires the game's exact Build/Buy validator before the
object can be registered, owned, or paid for.
"""

import math

import tyjokr_a11y_speech as speech


SUPPORTED = frozenset(("terrain", "water", "ceiling", "fence"))
SETTING = {
    "terrain": "experimental_bare_ground",
    "water": "experimental_water",
    "ceiling": "experimental_ceiling",
    "fence": "experimental_fence",
}
_original_build_place = None
_original_checks = None
_original_fit_parts = None


def _log(message):
    try:
        speech.log_line("surfaces: " + message)
    except Exception:
        pass


def _text(en, pl):
    try:
        import tyjokr_a11y_grid as grid
        return grid._text(en, pl)
    except Exception:
        return en


def _selected():
    import tyjokr_a11y_place as place
    item = place.product()
    return (item, place.requirement(item["id"])) if item is not None else (None, None)


def _enabled(need):
    if need not in SUPPORTED:
        return False
    try:
        import tyjokr_a11y_settings as settings
        return bool(settings.get(SETTING[need], True))
    except Exception:
        return False


def _cursor_position():
    import tyjokr_a11y_grid as grid
    target = grid.cursor()
    return target[0] if target is not None else None


def _natural_ground(position, level):
    try:
        import build_buy
        return bool(build_buy.is_location_natural_ground(position, level))
    except Exception as ex:
        _log("natural-ground check failed: {!r}".format(ex))
        return None


def _water_point(position, level):
    """Return (surface point, depth, kind), or (None, depth, kind)."""
    import sims4.math
    depth, pool, pond = 0.0, False, False
    try:
        import build_buy
        pool = bool(build_buy.is_location_pool(position, level))
        pond = bool(build_buy.get_pond_id(position))
    except Exception as ex:
        _log("pool/pond check failed: {!r}".format(ex))
    try:
        import terrain
        depth = float(terrain.get_water_depth(float(position.x), float(position.z), int(level)) or 0.0)
    except Exception as ex:
        _log("water-depth check failed: {!r}".format(ex))
    if not (pool or pond or depth > 0.01):
        return None, depth, "water"
    # Grid Y is the terrain/bottom sample; water depth raises it to the surface.
    point = sims4.math.Vector3(
        float(position.x), float(position.y) + max(0.0, depth), float(position.z)
    )
    return point, depth, "pool" if pool else ("pond" if pond else "water")


def _ceiling_point(position, level):
    """The next routing level's plane is the best available ceiling anchor."""
    try:
        import routing
        import services
        import sims4.math
        import terrain
        surface = routing.SurfaceIdentifier(
            services.current_zone_id(), int(level) + 1,
            routing.SurfaceType.SURFACETYPE_WORLD,
        )
        height = float(terrain.get_terrain_height(
            float(position.x), float(position.z), routing_surface=surface
        ))
        if not math.isfinite(height) or height <= float(position.y) + 1.0:
            return None
        return sims4.math.Vector3(float(position.x), height, float(position.z))
    except Exception as ex:
        _log("ceiling sample failed: {!r}".format(ex))
        return None


def _fence_point():
    """Select an edge geometrically; exact validation proves whether it is a fence."""
    import sims4.math
    import tyjokr_a11y_grid as grid
    import tyjokr_a11y_tiles as tiles
    frame = tiles.frame()
    if frame is None:
        return None
    i, j = grid._tile
    sides = tiles.walls(frame, i, j, grid._level)
    doors = tiles.doors(frame, i, j, grid._level)
    side = int(grid._facing) % 4
    if side in doors or sides.get(side) not in ("wall", "blocked"):
        return None
    di, dj = tiles.STEPS[side]
    center = tiles.position(frame, i, j, grid._level)
    neighbor = frame.world(i + di, j + dj)
    point = sims4.math.Vector3(
        (float(center.x) + float(neighbor[0])) / 2.0,
        float(center.y),
        (float(center.z) + float(neighbor[1])) / 2.0,
    )
    return frame, side, point, frame.yaw((side + 2) % 4)


def _fit_parts(frame, with_facing=True):
    import tyjokr_a11y_grid as grid
    item, need = _selected()
    if item is None or need not in SUPPORTED or not _enabled(need):
        return _original_fit_parts(frame, with_facing=with_facing)
    position = _cursor_position()
    if position is None:
        return [_text("Experimental placement: this tile cannot be checked. ", "Umieszczanie eksperymentalne: nie mozna sprawdzic pola. ")]
    if need == "terrain":
        if _natural_ground(position, grid._level) is True:
            return [_text("Experimental bare-ground placement. Natural ground detected; Enter asks the game to validate it. ", "Eksperymentalne umieszczanie na ziemi. Wykryto naturalny teren; Enter prosi gre o sprawdzenie. ")]
        return [_text("Experimental bare-ground placement. This tile has flooring or is not natural ground. ", "Eksperymentalne umieszczanie na ziemi. To pole ma podloge albo nie jest naturalnym terenem. ")]
    if need == "water":
        point, depth, kind = _water_point(position, grid._level)
        if point is None:
            return [_text("Experimental water placement. No water surface detected here. ", "Eksperymentalne umieszczanie w wodzie. Nie wykryto tutaj powierzchni wody. ")]
        return [_text("Experimental water placement. {} detected, depth {:.1f} metres; Enter asks the game to validate it. ", "Eksperymentalne umieszczanie w wodzie. Wykryto {}, glebokosc {:.1f} metra; Enter prosi gre o sprawdzenie. ").format(kind, depth)]
    if need == "ceiling":
        point = _ceiling_point(position, grid._level)
        if point is None:
            return [_text("Experimental ceiling placement. No ceiling anchor could be sampled here. ", "Eksperymentalne umieszczanie na suficie. Nie znaleziono punktu sufitu. ")]
        return [_text("Experimental ceiling placement. Sampled height {:.1f} metres; Enter asks the game to validate it. ", "Eksperymentalne umieszczanie na suficie. Wysokosc {:.1f} metra; Enter prosi gre o sprawdzenie. ").format(float(point.y) - float(position.y))]
    if _fence_point() is None:
        return [_text("Experimental fence placement. Selected side has no blocked edge; turn with R. ", "Eksperymentalne umieszczanie na plocie. Po wybranej stronie nie ma krawedzi; obroc R. ")]
    return [_text("Experimental fence placement. Enter asks the game to validate the selected edge as a fence. ", "Eksperymentalne umieszczanie na plocie. Enter prosi gre o sprawdzenie wybranej krawedzi jako plotu. ")]


def _checks(position, level, key, guard):
    """Permit one enabled requirement while retaining every baseline gate."""
    import tyjokr_a11y_place as place
    item, need = _selected()
    if item is None or need not in SUPPORTED or not _enabled(need):
        return _original_checks(position, level, key, guard)
    original_requirement = place.requirement
    original_pool_check = None
    try:
        place.requirement = lambda _def_id: None
        if need == "water":
            try:
                import build_buy
                original_pool_check = build_buy.is_location_pool
                # The baseline rejects every pool before its exact validator.
                # Only this water-required transaction may reach that validator.
                build_buy.is_location_pool = lambda _position, _level: False
            except Exception:
                original_pool_check = None
        checked = _original_checks(position, level, key, guard)
    finally:
        place.requirement = original_requirement
        if original_pool_check is not None:
            build_buy.is_location_pool = original_pool_check
    if checked is None:
        return None
    return checked[0], checked[1], need


def _build_place():
    import tyjokr_a11y_grid as grid
    import tyjokr_a11y_place as place
    import tyjokr_a11y_tiles as tiles
    item, need = _selected()
    if item is None or need not in SUPPORTED or not _enabled(need):
        return _original_build_place()
    frame, position = tiles.frame(), _cursor_position()
    if frame is None or position is None:
        place._say_text("Experimental placement could not check this tile. Nothing was bought.", "Nie mozna sprawdzic tego pola. Nic nie kupiono.")
        return False
    angle, point = frame.yaw(int(grid._facing) % 4), position
    if need == "terrain":
        if _natural_ground(position, grid._level) is not True:
            place._say_text("This object needs natural ground with no floor tiles.", "Ten obiekt wymaga naturalnego terenu bez podlogi.")
            return False
    elif need == "water":
        point, depth, kind = _water_point(position, grid._level)
        if point is None:
            place._say_text("This object needs water, and no water surface was detected here.", "Ten obiekt wymaga wody, a tutaj jej nie wykryto.")
            return False
        _log("water product {} kind {} depth {:.2f}".format(item["id"], kind, depth))
    elif need == "ceiling":
        point = _ceiling_point(position, grid._level)
        if point is None:
            place._say_text("No ceiling anchor could be sampled here.", "Nie znaleziono punktu sufitu w tym miejscu.")
            return False
    else:
        selected = _fence_point()
        if selected is None:
            place._say_text("No fence-like edge is selected. Turn with R or move beside a fence.", "Nie wybrano krawedzi plotu. Obroc R albo przejdz obok plotu.")
            return False
        frame, side, point, angle = selected
    _log("product {} requirement {} sent to exact validation".format(item["id"], need))
    return place.place(point, grid._level, grid._surface(), angle=angle, exact=True)


def install():
    global _original_build_place, _original_checks, _original_fit_parts
    import tyjokr_a11y_grid as grid
    import tyjokr_a11y_place as place
    if getattr(grid, "_surface_contribution_installed", False):
        return
    _original_build_place = grid._build_place
    _original_fit_parts = grid._fit_parts
    _original_checks = place._checks
    grid._build_place = _build_place
    grid._fit_parts = _fit_parts
    place._checks = _checks
    grid._surface_contribution_installed = True
    _log("experimental bare-ground, water, ceiling, and fence adapters installed")


install()
