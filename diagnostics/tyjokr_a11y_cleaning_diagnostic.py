"""Standalone read-only, bounded active-lot state inventory for cleaning research."""
import json
import time
from itertools import islice
import sims4.commands

_job = None
MAX_VISITED = 10000
MAX_STATES = 64
MAX_ACTIONS = 256


def _identity(resource):
    if resource is None:
        return None
    return {'name': getattr(resource, '__name__', None),
            'id': getattr(resource, 'guid64', None)}


def describe(obj):
    definition = getattr(obj, 'definition', None)
    hidden = getattr(obj, 'is_hidden', None)
    row = {'id': obj.id, 'definition_id': getattr(definition, 'id', None),
           'definition_name': getattr(definition, 'name', None),
           'class': type(obj).__name__, 'floor': getattr(obj, 'level', None),
           'position': [round(float(obj.position.x), 3), round(float(obj.position.z), 3)],
           'hidden': hidden() if callable(hidden) else hidden, 'states': []}
    component = getattr(obj, 'state_component', None)
    if component is not None:
        try:
            values = list(islice(component.values(), MAX_STATES + 1))
            row['states_truncated'] = len(values) > MAX_STATES
            for value in values[:MAX_STATES]:
                state = getattr(value, 'state', None)
                row['states'].append({'state': _identity(state), 'value': _identity(value),
                                      'linked_stat': _identity(getattr(state, 'linked_stat', None))})
        except Exception as ex:
            row['state_error'] = type(ex).__name__
    # Static affordances are hints, NOT proof of dirtiness or availability.
    # Never run potential_interactions, tests, enqueue, set_state or statistics.
    try:
        actions = list(islice(obj.super_affordances(), MAX_ACTIONS + 1))
        row['actions_truncated'] = len(actions) > MAX_ACTIONS
        row['cleaning_action_hints'] = [_identity(a) for a in actions[:MAX_ACTIONS]
                                        if any(k in (getattr(a, '__name__', '') or '').lower()
                                               for k in ('clean', 'mop', 'dust', 'trash', 'wash'))]
    except Exception as ex:
        row['action_error'] = type(ex).__name__
    return row


def _write(kind, data):
    import tyjokr_a11y_speech as speech
    speech.log_line('cleaning inspect: ' + kind + ' ' + json.dumps(data, sort_keys=True, default=str))


def _finish(job, reason):
    global _job
    if _job is not job:
        return
    _job = None
    summary = {k: job[k] for k in ('zone', 'visited', 'recorded', 'errors', 'limit')}
    summary['reason'] = reason
    _write('end', summary)
    job['output']('Cleaning snapshot: {} objects recorded; {}. See TS4 Access log.'.format(job['recorded'], reason))


def _tick(job):
    import services
    import tyjokr_a11y_pump as pump
    import tyjokr_a11y_speech as speech
    if _job is not job:
        return
    if not speech.log_enabled:
        _finish(job, 'logging disabled')
        return
    if services.current_zone_id() != job['zone']:
        _finish(job, 'zone changed')
        return
    deadline = time.monotonic() + 0.004
    count = 0
    manager, lot = services.object_manager(), services.active_lot()
    if manager is None or lot is None:
        _finish(job, 'lot unavailable')
        return
    while job['visited'] < len(job['ids']) and count < 10 and time.monotonic() < deadline:
        obj_id = job['ids'][job['visited']]
        job['visited'] += 1
        count += 1
        try:
            obj = manager.get(obj_id)
            if obj is None or getattr(obj, 'is_sim', False):
                continue
            inventory = getattr(obj, 'is_in_inventory', None)
            in_inventory = inventory() if callable(inventory) else bool(inventory)
            if in_inventory:
                continue
            if not lot.is_position_on_lot(obj.position):
                continue
            _write('object', describe(obj))
            job['recorded'] += 1
        except Exception as ex:
            job['errors'] += 1
            if job['errors'] <= 5:
                _write('error', {'id': obj_id, 'error': type(ex).__name__})
        if job['recorded'] >= job['limit']:
            _finish(job, 'object limit reached')
            return
    if job['visited'] >= len(job['ids']):
        _finish(job, 'visit cap reached' if job['capped'] else 'complete')
    elif not pump.post(_tick, job):
        _finish(job, 'simulation pump stopped')


@sims4.commands.Command('a11y.inspect_cleaning', command_type=sims4.commands.CommandType.Live)
def inspect_cleaning(limit: int = 500, _connection=None):
    """0 cancels; otherwise inspect up to 2000 world objects on the active lot."""
    global _job
    output = sims4.commands.CheatOutput(_connection)
    if limit == 0:
        if _job is not None:
            _finish(_job, 'cancelled')
        return True
    if _job is not None:
        output('A cleaning snapshot is already running. Use a11y.inspect_cleaning 0 to cancel.')
        return False
    import services
    import tyjokr_a11y_pump as pump
    import tyjokr_a11y_speech as speech
    if not speech.log_enabled:
        output('Run a11y.log on first, then repeat a11y.inspect_cleaning.')
        return False
    if services.active_lot() is None or not pump.alive():
        output('Load a household first.')
        return False
    ids = [obj.id for obj in islice(services.object_manager().values(), MAX_VISITED + 1)]
    job = {'zone': services.current_zone_id(), 'ids': ids[:MAX_VISITED],
           'capped': len(ids) > MAX_VISITED, 'limit': min(2000, max(1, limit)),
           'visited': 0, 'recorded': 0, 'errors': 0, 'output': output}
    _job = job
    _write('begin', {'zone': job['zone'], 'limit': job['limit'], 'manager_count_capped': len(ids)})
    if not pump.post(_tick, job):
        _finish(job, 'simulation pump stopped')
        return False
    output('Read-only cleaning snapshot started. Enable a11y.log on first to retain its records.')
    return True
