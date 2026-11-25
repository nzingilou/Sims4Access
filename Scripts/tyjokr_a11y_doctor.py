"""Read-only Get to Work patient findings through native accessibility pickers.

No illness guessing, discovery writes, examination automation or tuning changes.
Only a discovered diagnosis may be named. Observable activity is a whitelist
of currently running EP01 symptom animations, never the illness's symptom list.
All entry points/callbacks run on the simulation thread.
"""
import math
import tyjokr_a11y_speech as speech

_ACTIVITY = {
    'Dizzy': 'Dizzy symptom animation',
    'Headache': 'Headache symptom animation',
    'Itchy': 'Scratching',
    'CoughSneeze': 'Coughing or sneezing',
    'Giggly': 'Unusual giggling',
    'Fever': 'Fever symptom animation',
    'Nausea': 'Nausea symptom animation',
    'SteamyEars': 'Steam-from-ears symptom animation',
    'SeeingThings': 'Visual-disturbance symptom animation',
}
ACTIVITY_NAMES = {'idle_Buff_SickessSystem_Symptom_{}_{}'.format(kind, severity): label
                  for kind, label in _ACTIVITY.items()
                  for severity in ('mild', 'severe', 'ambient')}
SECTIONS = (
    ('symptoms', 'Discovered symptoms'),
    ('exams', 'Examinations recorded'),
    ('treatments', 'Treatments attempted'),
    ('ruled_out', 'Treatments ruled out'),
    ('activity', 'Current symptom activity'),
)


def _log(message):
    speech.log_line('doctor reader: ' + str(message))


def _say(message):
    speech.speak(message, explicit=True)


def available():
    try:
        from sims4.common import Pack, is_available_pack
        return bool(is_available_pack(Pack.EP01))
    except Exception:
        return False


def _context():
    import services
    import tyjokr_a11y_keys as keys
    import tyjokr_a11y_place as place
    if not available() or place.in_build_mode() or keys.blocking_active() or keys._editing_active:
        return None
    actor = services.get_active_sim()
    career_service = services.get_career_service()
    career = career_service.get_career_in_career_event() if career_service is not None else None
    if actor is None or career is None or career.sim_info.sim_id != actor.sim_info.sim_id:
        return None
    return (int(services.current_zone_id()), int(actor.sim_info.sim_id), int(career.guid64))


def _patients():
    import services
    from situations.complex.patient_situation_base import PatientSituationBase
    import tyjokr_a11y_scanner as scanner
    manager = services.get_zone_situation_manager()
    result = {}
    for situation in list(manager.values()) if manager is not None else ():
        if not isinstance(situation, PatientSituationBase):
            continue
        sim = situation.get_patient()
        if sim is None:
            continue
        try:
            if (services.object_manager().get(sim.id) is not sim
                    or sim.zone_id != services.current_zone_id() or sim.is_hidden()):
                continue
            state = type(getattr(situation, '_cur_state', None)).__name__
            result[int(sim.sim_info.sim_id)] = (sim, scanner.PATIENT_STAGES.get(state, 'patient'))
        except Exception as exc:
            _log('patient unavailable: {!r}'.format(exc))
    return result


def _patient(context, ident):
    if context is None or _context() != context:
        _say('The working Sim or hospital context changed. Open Doctor patients again.')
        return None
    row = _patients().get(int(ident))
    if row is None:
        _say('That patient is no longer available here.')
    return row


def _activity(sim):
    """Queue iteration includes queued work; require the native running flag."""
    found = set()
    for source in (getattr(sim, 'si_state', None), getattr(sim, 'queue', None)):
        if source is None:
            continue
        try:
            for interaction in tuple(source):
                if getattr(interaction, 'running', None) is not True:
                    continue
                kind = getattr(interaction, 'affordance', type(interaction))
                label = ACTIVITY_NAMES.get(getattr(kind, '__name__', ''))
                if label:
                    found.add(label)
        except Exception as exc:
            _log('activity unavailable: {!r}'.format(exc))
    return tuple(sorted(found))


def _facts(sim):
    tracker = getattr(sim.sim_info, 'sickness_tracker', None)
    if tracker is None:
        raise RuntimeError('The game did not provide a patient findings tracker.')
    facts = {'symptoms': tuple(tracker.discovered_symptoms),
             'exams': tuple(tracker.exams_performed),
             'treatments': tuple(tracker.treatments_performed),
             'ruled_out': tuple(tracker.ruled_out_treatments),
             'activity': _activity(sim), 'diagnosis': None}
    # Do not even read current_sickness until the native discovery flag is set.
    if tracker.has_discovered_sickness is True:
        facts['diagnosis'] = tracker.current_sickness
    return facts


def _raw(text):
    import tyjokr_a11y_menu as menu
    return menu._raw(text)


def _display(value, info, interaction=False):
    try:
        if interaction:
            import services
            from interactions.context import InteractionContext
            from interactions.priority import Priority
            context = InteractionContext(services.get_active_sim(), InteractionContext.SOURCE_SCRIPT, Priority.Low)
            result = value.get_name(target=info.get_sim_instance(), context=context, apply_name_modifiers=False)
        else:
            result = value.display_name(info)
        if result is not None and getattr(result, 'hash', 1):
            return result
    except Exception as exc:
        _log('localized label unavailable: {!r}'.format(exc))
    # Never narrate an internal tuning name as a clinical finding.
    return _raw('Recorded finding; game label unavailable')


def _guarded(context, ident, fn):
    try:
        patient = _patient(context, ident)
        if patient is None:
            return False
        return fn(*patient)
    except Exception as exc:
        _log('readout unavailable: {!r}'.format(exc))
        _say('Patient findings are unavailable. See the doctor-reader diagnostic log.')
        return False


def open_patients():
    import tyjokr_a11y_hub as hub
    import tyjokr_a11y_lang as lang
    try:
        context = _context()
        if context is None:
            _say('In Live mode, select the Sim attending the active hospital workday and close other dialogs.')
            return False
        patients = _patients()
        if not patients:
            _say('No hospital patients are available here right now.')
            return False
        rows = [(_raw(hub._name(sim.sim_info)), _raw(lang.t(stage)),
                 lambda ident=ident: show_patient(context, ident))
                for ident, (sim, stage) in sorted(patients.items(), key=lambda row: (hub._name(row[1][0].sim_info).casefold(), row[0]))]
        return hub._window('Doctor patients', 'Choose a patient to read known findings or open their ordinary interactions.', rows)
    except Exception as exc:
        _log('patient list unavailable: {!r}'.format(exc))
        _say('The hospital patient list is unavailable.')
        return False


def show_patient(context, ident):
    import tyjokr_a11y_hub as hub
    import tyjokr_a11y_lang as lang
    def show(sim, stage):
        facts = _facts(sim)
        refresh = lambda: show_patient(context, ident)
        diagnosis = (_display(facts['diagnosis'], sim.sim_info) if facts['diagnosis'] is not None
                     else _raw('Not discovered'))
        rows = [(_raw('Patient status'), _raw(lang.t(stage)), refresh),
                (_raw('Discovered diagnosis'), diagnosis, refresh)]
        for key, label in SECTIONS:
            count = len(facts[key])
            description = '{} recorded'.format(count)
            if key == 'activity':
                description = '{} mapped animations running. This is a current observation, not an examination result.'.format(count)
            rows.append((_raw(label), _raw(description),
                         lambda section=key: show_section(context, ident, section)))
        rows += [(_raw('Patient interactions'), _raw('Open the normal game menu; choose examinations and treatment yourself.'),
                  lambda: open_interactions(context, ident)),
                 (_raw('Refresh patient findings'), None, refresh),
                 (_raw('Log patient presentation for research'), _raw('Read-only diagnostic; requires a11y.log on.'),
                  lambda: inspect_patient(context, ident)),
                 (_raw('Other patients'), None, open_patients),
                 (_raw('Back to Accessibility menu'), None, hub.open_hub)]
        return hub._window('Doctor patient findings',
                           'Refresh after an examination or to sample current symptom activity.', rows,
                           localized_title=_raw(hub._name(sim.sim_info)))
    return _guarded(context, ident, show)


def show_section(context, ident, section):
    import tyjokr_a11y_hub as hub
    labels = dict(SECTIONS)
    if section not in labels:
        return False
    def show(sim, stage):
        values = _facts(sim)[section]
        back = lambda: show_patient(context, ident)
        rows = []
        for value in sorted(values, key=lambda item: str(getattr(item, 'guid64', item))):
            name = (_raw(value) if section == 'activity' else
                    _display(value, sim.sim_info, interaction=section in ('exams', 'treatments', 'ruled_out')))
            rows.append((name, None, back))
        if not rows:
            text = 'No mapped symptom animation is running now.' if section == 'activity' else 'None recorded by the game.'
            rows.append((_raw(text), None, back))
        rows += [(_raw('Refresh this list'), None, lambda: show_section(context, ident, section)),
                 (_raw('Back to patient findings'), None, back)]
        return hub._window(labels[section], 'Read-only findings for ' + hub._name(sim.sim_info), rows)
    return _guarded(context, ident, show)


def open_interactions(context, ident):
    """Reuse the native client pick protocol; never generate/choose treatments."""
    import services
    import tyjokr_a11y_scanner as scanner
    def request(sim, stage):
        from server.pick_info import PickType
        p = sim.position
        if not all(math.isfinite(float(v)) for v in (p.x, p.y, p.z)):
            raise ValueError('Patient position is unavailable')
        lot_id = int(services.active_lot().lot_id)
        if not 0 <= lot_id <= 0xffffffff:
            lot_id = 0
        first = str(sim.sim_info.first_name or '').replace('|', ' ')
        sent = scanner._send_ui('A11y|pick|{}|{}|{}|{}|{:.3f}|{:.3f}|{:.3f}|{}'.format(
            int(sim.id), int(PickType.PICK_SIM), lot_id, first, float(p.x), float(p.y), float(p.z), int(sim.level)))
        if not sent:
            _say('The patient interaction menu could not be requested.')
        return bool(sent)
    return _guarded(context, ident, request)


def inspect_patient(context, ident):
    """Explicit diagnostic only; no hidden clinical answers enter speech."""
    if not speech.log_enabled:
        _say('Enable diagnostic logging with a11y.log on first.')
        return False
    def inspect(sim, stage):
        facts = _facts(sim)
        _log('presentation zone={} patient={} stage={} known_counts={} activity={}'.format(
            context[0], ident, stage, {key: len(facts[key]) for key, _ in SECTIONS}, facts['activity']))
        buffs = getattr(sim.sim_info, 'Buffs', None)
        for buff in tuple(buffs) if buffs is not None else ():
            fields = {name: repr(getattr(buff, name, None))[:200] for name in
                      ('visible', 'vfx', 'cas_vfx', 'appearance_modifier', 'walkstyle', '_vfx')}
            effect = getattr(buff, '_vfx', None)
            fields['active_effect_name'] = getattr(effect, 'effect_name', None)
            fields['active_effect_joint'] = getattr(effect, 'joint_name', None)
            _log('presentation buff={} fields={}'.format(type(buff).__name__, fields))
        _say('Patient presentation logged for research. No examination or treatment was performed.')
        return True
    return _guarded(context, ident, inspect)
