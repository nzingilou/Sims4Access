"""Experimental native pool drawing; other water/terrain tools stay read-only."""
import json
import math
import threading
import time

SETTING = 'experimental_pool_construction'
POOL_TAG = 'BUILDTAG_BLOCK_POOL_TOOL'
_selection = None


def _modules():
    import tyjokr_a11y_plus_build as build
    import tyjokr_a11y_plus_core as core
    import tyjokr_a11y_build_helpers as helpers
    return build, core, helpers


def _log(kind, **data):
    import tyjokr_a11y_speech as speech
    speech.log_line('water tools: ' + json.dumps(dict(kind=kind, **data), sort_keys=True, default=str))


def _enabled():
    import tyjokr_a11y_settings as settings
    return bool(settings.get(SETTING, False))


def _context():
    import services
    build, core, helpers = _modules()
    state = helpers._state()
    state['household'] = int(services.active_household_id())
    return state


def _same(state):
    import services
    build, core, helpers = _modules()
    return (_enabled() and helpers._same_world(state)
            and int(services.active_household_id()) == state['household'])


def _bounds(box, frame):
    if (len(box) != 4 or any(isinstance(v, bool) or not isinstance(v, (int, float))
                            or not math.isfinite(v) or int(v) != v for v in box)):
        raise ValueError('Pool corners must be four whole-metre coordinates.')
    e, n, right, bottom = tuple(int(v) for v in box)
    if not (1 <= e < right <= frame.width - 1 and 1 <= n < bottom <= frame.depth - 1):
        raise ValueError('Keep the pool at least one metre inside the lot.')
    if not (2 <= right - e <= 20 and 2 <= bottom - n <= 20):
        raise ValueError('Choose a pool width and depth between 2 and 20 metres.')
    return e, n, right, bottom


def _survey(box, frame):
    """Simulation thread only; unknown native facts stop construction."""
    import services
    import build_buy
    import sims4.math
    build, core, helpers = _modules()
    lot = services.active_lot()
    if lot is None:
        raise RuntimeError('No active lot.')
    inside, border, heights = [], [], []
    for n in range(box[1] - 1, box[3] + 1):
        for e in range(box[0] - 1, box[2] + 1):
            x, z = frame.world(e + .5, n + .5)
            y = build.floor_height(x, z, 0)
            if y is None or not math.isfinite(y):
                raise RuntimeError('The game did not report a valid ground height.')
            point = sims4.math.Vector3(x, y, z)
            if not lot.is_position_on_lot(point):
                raise RuntimeError('The requested area is outside the editable lot.')
            pool = build_buy.is_location_pool(point, 0)
            if pool is None:
                raise RuntimeError('The game did not report pool geometry.')
            if box[0] <= e < box[2] and box[1] <= n < box[3]:
                ground = build_buy.is_location_natural_ground(point, 0)
                outside = build_buy.is_location_outside(point, 0)
                room = build_buy.get_room_id(services.current_zone_id(), point, 0)
                inside.append((e, n, bool(pool), ground, outside, room))
                heights.append(float(y))
            else:
                border.append((e, n, bool(pool)))
    rooms = build._room_ids()
    if rooms is None:
        raise RuntimeError('Existing building geometry is unavailable.')
    return {'inside': inside, 'border': border, 'heights': heights, 'rooms': rooms}


def _preflight(box, frame, survey):
    if any(row[2] for row in survey['inside'] + survey['border']):
        raise RuntimeError('An existing pool is in or next to this footprint. Pool extensions are not supported yet.')
    if any(row[3] is not True or row[4] is not True or row[5] != 0 for row in survey['inside']):
        raise RuntimeError('Choose clear natural ground outside buildings and flooring.')
    if max(survey['heights']) - min(survey['heights']) > .05:
        raise RuntimeError('This first pool tool requires flat ground; it will not reshape terrain.')
    import services
    for obj in services.object_manager().values():
        if getattr(obj, 'is_sim', False):
            continue
        try:
            if obj.is_in_inventory() or int(obj.level) != 0:
                continue
            e, n = frame.local(obj.position.x, obj.position.z)
        except Exception:
            # An uninspectable world object is not evidence of clear ground.
            raise RuntimeError('A world object could not be checked. Nothing was drawn.')
        if box[0] - 2 <= e <= box[2] + 2 and box[1] - 2 <= n <= box[3] + 2:
            raise RuntimeError('Furniture or landscaping is too close to the pool footprint. Choose a clearer area.')


def catalog_reply(encoded):
    """Observe the existing serial-scoped selection reply; never own other replies."""
    job = _selection
    if job is None:
        return
    try:
        from urllib.parse import unquote
        parts = unquote(str(encoded or '')).split('|')
        build, core, helpers = _modules()
        if (len(parts) == 3 and parts[0] == 'selected' and parts[1] == str(job['index'])
                and unquote(parts[2]) == job['name'] and build._cat['serial'] == job['serial']
                and _same(job['state'])):
            job['done'].set()
    except Exception as exc:
        _log('selection-reply-rejected', error=str(exc))


def _select_tool(state, choice=None):
    global _selection
    build, core, helpers = _modules()
    if not build.on_main(_same, state):
        return False
    items = build.fetch_catalog(16, POOL_TAG, 'tool') or []
    _log('native-pool-tools', entries=items, serial=build._cat['serial'])
    # This tag is EA's Pool Tool filter, not the catalogue of premade blocks.
    # Multiple tools require a user choice; never guess from a name or index.
    index = 0
    if choice is not None:
        if (not _same_choice(choice, items) or not build.on_main(_same, choice['state'])):
            return False
        index = choice['index']
    elif len(items) != 1:
        return False
    if not items or not build.on_main(_same, state):
        return False
    name = str(items[index][0])
    job = {'index': index, 'name': name, 'serial': build._cat['serial'],
           'state': state, 'done': threading.Event()}
    _selection = job
    previous = build._cat.get('silent_select', False)
    try:
        build._cat['silent_select'] = True
        # select_item is a worker helper: it posts its own game-thread message
        # and waits briefly. Never run that wait inside the simulation pump.
        build.select_item(index, name)
        return job['done'].wait(2.0) and bool(build.on_main(_same, state))
    finally:
        _selection = None
        build._cat['silent_select'] = previous


def _verified(before, after):
    return (bool(before['inside']) and len(before['inside']) == len(after['inside'])
            and [(r[0], r[1]) for r in before['inside']] == [(r[0], r[1]) for r in after['inside']]
            and all(row[2] for row in after['inside'])
            and before['border'] == after['border']
            and before['rooms'] == after['rooms'])


def _pair(text):
    parts = str(text).split()
    if len(parts) != 2 or not all(p.isdecimal() for p in parts):
        raise ValueError('Type two whole numbers separated by a space.')
    return tuple(int(p) for p in parts)


def _same_choice(choice, items):
    index = choice.get('index')
    return (isinstance(index, int) and not isinstance(index, bool)
            and 0 <= index < len(items)
            and choice.get('entries') == tuple(tuple(row) for row in items))


def _draw(box, choice=None):
    build, core, helpers = _modules()
    state = build.on_main(_context)
    if state is None or not build.on_main(_same, state):
        raise RuntimeError('Pool construction is disabled or the Build context changed.')
    if choice is not None and not build.on_main(_same, choice['state']):
        raise RuntimeError('The pool-tool choice belongs to another Build context.')
    frame = build.on_main(build.frame)
    box = _bounds(box, frame)
    if not build.set_floor(0):
        raise RuntimeError('The game did not confirm the ground floor.')
    before = build.on_main(_survey, box, frame)
    if before is None:
        raise RuntimeError('Pool survey timed out.')
    # on_main converts exceptions into None, so require an explicit success.
    if build.on_main(_can_draw, box, frame, before) is not True:
        raise RuntimeError('The footprint failed its safety checks. See the water-tools log.')
    started = time.monotonic()
    def action(screen):
        if not build.on_main(_same, state) or helpers._native_floor(state)['floor'] != 0:
            raise RuntimeError('The lot, household, input owner or floor changed.')
        fresh = build.on_main(_survey, box, frame)
        if fresh is None or fresh != before or build.on_main(_can_draw, box, frame, fresh) is not True:
            raise RuntimeError('The footprint changed while preparing the camera.')
        selected = _select_tool(state) if choice is None else _select_tool(state, choice)
        if not selected:
            raise RuntimeError('One native Pool Tool could not be confirmed. Its catalogue entries were logged.')
        _log('drag', box=box, zone=state['zone'])
        build.drag(screen[0], screen[1])
    performed = build.point_and_act([frame.world(box[0], box[1]), frame.world(box[2], box[3])],
                                    0, action, 'experimental rectangular pool', overview=True)
    if not performed:
        raise RuntimeError('The measured screen corners could not be used safely.')
    for attempt in range(20):
        if not build.on_main(_same, state):
            raise RuntimeError('Build context changed while verifying the pool. Inspect the result.')
        after = build.on_main(_survey, box, frame)
        if after is not None and _verified(before, after):
            _log('verified', box=box, tiles=len(after['inside']), zone=state['zone'])
            return True
        time.sleep(.25)
    reason = build._last_error.get('text', '') if build._last_error.get('at', 0) >= started else ''
    _log('unverified', box=box, game_reason=reason, after=after)
    raise RuntimeError('The game did not confirm the complete pool footprint. '
                       + (reason + ' ' if reason else '') + 'Inspect the result before Undo or another attempt.')


def _can_draw(box, frame, survey):
    try:
        _preflight(box, frame, survey)
        return True
    except Exception as exc:
        _log('preflight-refused', box=box, reason=str(exc))
        return False


def _start(box, choice=None):
    build, core, helpers = _modules()
    if build._busy[0]:
        core.speak('Another build helper is working.'); return
    if not _enabled():
        core.speak('Turn on experimental pool construction in accessibility settings first.'); return
    build._busy[0] = True
    def work():
        try:
            if _draw(box, choice):
                core.post(core.speak, 'The game confirmed the rectangular pool. Press Escape to leave the Pool Tool. Add pool access and test swimming before saving.')
        except Exception as exc:
            _log('stopped', box=box, reason=str(exc))
            core.post(core.speak, 'Pool construction stopped. ' + str(exc))
        finally:
            build._busy[0] = False
    try:
        threading.Thread(target=work, name='a11y_pool', daemon=True).start()
    except Exception:
        build._busy[0] = False
        raise


def _ask_pool():
    build, core, helpers = _modules()
    def size(text):
        try:
            values = _pair(text)
        except ValueError as exc:
            core.speak(str(exc)); return
        if any(v < 2 or v > 20 for v in values):
            core.speak('Type width and depth between 2 and 20 metres, for example 6 4.'); return
        width, depth = values
        def position(text):
            try:
                values = _pair(text)
            except ValueError as exc:
                core.speak(str(exc)); return
            box = (values[0], values[1], values[0] + width, values[1] + depth)
            try:
                box = _bounds(box, build.frame())
            except Exception as exc:
                core.speak(str(exc)); return
            _offer_pool_tools(box)
        core.ask_text('Pool position', 'Metres from the west edge, then the north edge of the lot.', '', position)
    core.ask_text('Pool size', 'Width west to east and depth north to south. Equal values make a square.', '', size)


def _offer_pool_tools(box):
    """Two native tools are legitimate: require an explicit, rechecked choice."""
    build, core, helpers = _modules()
    if build._busy[0] or not _enabled():
        core.speak('Enable experimental pool construction and wait for other build helpers first.'); return
    build._busy[0] = True
    def work():
        offer = None
        try:
            state = build.on_main(_context)
            if state is None or not build.on_main(_same, state):
                raise RuntimeError('Build context changed.')
            items = build.fetch_catalog(16, POOL_TAG, 'tool') or []
            if not items or not build.on_main(_same, state):
                raise RuntimeError('No native pool tools were returned.')
            offer = (state, tuple(tuple(row) for row in items))
        except Exception as exc:
            _log('tool-chooser-failed', reason=str(exc))
            core.post(core.speak, 'Pool tools are unavailable. ' + str(exc))
        finally:
            build._busy[0] = False
        if offer is not None:
            state, entries = offer
            rows = [(row[0], 'Choose the rectangular Pool Tool for a single drag; the custom outline tool uses a different workflow.', index)
                    for index, row in enumerate(entries)]
            core.post(core.choose, 'Choose native pool tool',
                      'The game has more than one pool tool. Choose the rectangular tool, then confirm the size and cost.',
                      rows, lambda index: _confirm_pool(box, {'state': state, 'entries': entries, 'index': index}), 'build')
    try:
        threading.Thread(target=work, name='a11y_pool_tools', daemon=True).start()
    except Exception:
        build._busy[0] = False
        raise


def _confirm_pool(box, choice):
    build, core, helpers = _modules()
    if not _same(choice['state']) or not _same_choice(choice, choice['entries']):
        core.speak('The pool-tool choice expired. Open the pool assistant again.'); return
    name = choice['entries'][choice['index']][0]
    core.choose('Confirm experimental pool',
                '{}: {} by {} metres, {} from west and {} from north. Clear flat natural ground; the game decides cost and placement.'.format(
                    name, box[2]-box[0], box[3]-box[1], box[0], box[1]),
                [('Build this pool', 'May spend household funds if the game accepts the drag.', True),
                 ('Cancel', None, False)], lambda yes: _start(box, choice) if yes else None, tag='build')


def _diagnostics():
    build, core, helpers = _modules()
    import tyjokr_a11y_speech as speech
    if not speech.log_enabled:
        core.speak('Turn diagnostic logging on with a11y.log on, then run water-tool inspection again.'); return
    if build._busy[0]:
        core.speak('Another build helper is working.'); return
    build._busy[0] = True
    def work():
        try:
            state = build.on_main(_context)
            for name, product_type, tags in (
                    ('pool tools', 16, POOL_TAG), ('pool presets', 16, 'BUILDTAG_BLOCK_POOL'),
                    ('fountain tools', 16, 'BUILDTAG_BLOCK_FOUNTAIN_TOOL'),
                    ('fountain presets', 16, 'BUILDTAG_BLOCK_FOUNTAIN'), ('pond tools', 36, ''),
                    ('terrain tools', 33, '')):
                if state is None or not build.on_main(helpers._same_world, state):
                    raise RuntimeError('Build context changed.')
                entries = build.fetch_catalog(product_type, tags, 'none') or []
                _log('catalog-discovery', category=name, entries=entries, zone=state['zone'])
            core.post(core.speak, 'Logged native pool, fountain, pond and terrain catalogues. No tool was selected and nothing was built.')
        except Exception as exc:
            _log('diagnostic-failed', reason=str(exc))
            core.post(core.speak, 'Water-tool diagnostics stopped. ' + str(exc))
        finally:
            build._busy[0] = False
    try:
        threading.Thread(target=work, name='a11y_water_diagnostic', daemon=True).start()
    except Exception:
        build._busy[0] = False
        raise


def open_assistant():
    build, core, helpers = _modules()
    if not build.in_build_mode():
        core.speak('Enter Build mode first.'); return
    rows = [('Build a square or rectangular pool (experimental)', 'Choose size and position on clear flat ground. Enable pool construction in accessibility settings first.', _ask_pool),
            ('Inspect native water and terrain tools', 'Read-only catalogue discovery for curved pools, fountains, ponds and terrain; selects and builds nothing.', _diagnostics),
            ('Fountain decorations', 'Choose a normal catalogue object, then use the existing placement controls.', lambda: build.request_catalog('Fountain decorations', 2, 'BUYCAT_BUILD_FOUNTAIN_DECOR', 'object')),
            ('Fountain emitters', 'Native water-jet objects; the ordinary game placement validator decides where they fit.', lambda: build.request_catalog('Fountain emitters', 2, 'BUYCAT_LD_FOUNTAINEMITTER', 'object'))]
    core.choose('Water and terrain assistant', 'Pools are experimental. Curved-pool assembly, fountain basins, ponds and terrain reshaping are currently diagnostic-only.', rows, lambda fn: fn(), tag='build')
