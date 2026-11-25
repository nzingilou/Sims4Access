"""Patient readouts: discovery boundaries, stale targets and native UI routing."""
import pathlib
import sys
import types
import unittest
from unittest.mock import Mock, patch

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / 'Scripts'))
speech = types.SimpleNamespace(speak=Mock(), log_line=Mock(), log_enabled=False)
with patch.dict(sys.modules, tyjokr_a11y_speech=speech):
    import tyjokr_a11y_doctor as doctor


class Tracker:
    has_discovered_sickness = False
    discovered_symptoms = ()
    exams_performed = frozenset()
    treatments_performed = frozenset()
    ruled_out_treatments = frozenset()

    @property
    def current_sickness(self):
        raise AssertionError('Hidden illness was accessed')


class Tests(unittest.TestCase):
    def setUp(self):
        speech.speak.reset_mock(); speech.log_line.reset_mock(); speech.log_enabled = False
        self.tracker = Tracker()
        self.info = types.SimpleNamespace(sim_id=42, first_name='Patient', last_name='Example',
                                         sickness_tracker=self.tracker, get_sim_instance=lambda:self.patient)
        self.patient = types.SimpleNamespace(id=42, sim_info=self.info, zone_id=8, level=0,
                  position=types.SimpleNamespace(x=1.0,y=2.0,z=3.0), is_hidden=lambda:False,
                  si_state=[], queue=[])
        self.actor_info = types.SimpleNamespace(sim_id=1)
        self.actor = types.SimpleNamespace(sim_info=self.actor_info)
        self.career = types.SimpleNamespace(sim_info=self.actor_info, guid64=77)
        self.services = types.SimpleNamespace(current_zone_id=lambda:8, get_active_sim=lambda:self.actor,
                get_career_service=lambda:types.SimpleNamespace(get_career_in_career_event=lambda:self.career),
                active_lot=lambda:types.SimpleNamespace(lot_id=123),
                object_manager=lambda:{42:self.patient}, get_zone_situation_manager=lambda:{})
        self.keys = types.SimpleNamespace(blocking_active=lambda:False, _editing_active=False)
        self.hub = types.SimpleNamespace(_window=Mock(return_value=True), _name=lambda info:'Patient Example', open_hub=Mock())
        self.scanner = types.SimpleNamespace(_send_ui=Mock(return_value=True), PATIENT_STAGES={'WaitingState':'patient waiting'})
        self.context = (8,1,77)
        self.patches = [patch.dict(sys.modules, services=self.services, tyjokr_a11y_keys=self.keys,
                       tyjokr_a11y_place=types.SimpleNamespace(in_build_mode=lambda:False),
                       tyjokr_a11y_hub=self.hub, tyjokr_a11y_menu=types.SimpleNamespace(_raw=lambda v:v),
                       tyjokr_a11y_lang=types.SimpleNamespace(t=lambda v:v), tyjokr_a11y_scanner=self.scanner,
                       **{'server.pick_info':types.SimpleNamespace(PickType=types.SimpleNamespace(PICK_SIM=2))}),
                        patch.object(doctor,'available',return_value=True),
                        patch.object(doctor,'_patients',return_value={42:(self.patient,'patient waiting')})]
        for p in self.patches:
            p.start();self.addCleanup(p.stop)

    def test_undiscovered_illness_is_never_read_even_for_empty_findings(self):
        facts = doctor._facts(self.patient)
        self.assertIsNone(facts['diagnosis'])
        self.assertEqual(facts['symptoms'],())
        self.assertTrue(doctor.show_patient(self.context,42))
        self.assertEqual(self.hub._window.call_args[0][2][1][1],'Not discovered')

    def test_only_explicit_boolean_discovery_reveals_diagnosis(self):
        self.tracker.has_discovered_sickness = Mock()
        self.assertIsNone(doctor._facts(self.patient)['diagnosis'])
        sickness=types.SimpleNamespace(display_name=lambda info:'Localized known diagnosis')
        self.info.sickness_tracker=types.SimpleNamespace(has_discovered_sickness=True,current_sickness=sickness,
                 discovered_symptoms=(),exams_performed=(),treatments_performed=(),ruled_out_treatments=())
        self.assertTrue(doctor.show_patient(self.context,42))
        self.assertEqual(self.hub._window.call_args[0][2][1][1],'Localized known diagnosis')

    def test_missing_tracker_fails_without_opening_a_bogus_readout(self):
        self.info.sickness_tracker=None
        self.assertFalse(doctor.show_patient(self.context,42));self.hub._window.assert_not_called()

    def test_known_symptoms_keep_native_localized_strings(self):
        localized=object()
        self.tracker.discovered_symptoms=(types.SimpleNamespace(display_name=lambda info:localized),)
        self.assertTrue(doctor.show_section(self.context,42,'symptoms'))
        self.assertIs(self.hub._window.call_args[0][2][0][0],localized)

    def test_refresh_reads_current_discoveries_instead_of_cached_facts(self):
        doctor.show_section(self.context,42,'symptoms')
        refresh=self.hub._window.call_args[0][2][-2][2]
        self.tracker.discovered_symptoms=(types.SimpleNamespace(display_name=lambda info:'New finding'),)
        refresh()
        self.assertEqual(self.hub._window.call_args[0][2][0][0],'New finding')

    def test_zone_actor_career_and_blocking_changes_refuse_stale_menus(self):
        for context in [(9,1,77),(8,2,77),(8,1,78)]:
            self.assertFalse(doctor.show_patient(context,42))
        self.keys.blocking_active=lambda:True
        self.assertFalse(doctor.show_patient(self.context,42))
        self.hub._window.assert_not_called()

    def test_departed_patient_refuses_readout_and_actions(self):
        doctor._patients.return_value={}
        self.assertFalse(doctor.show_patient(self.context,42))
        self.assertFalse(doctor.open_interactions(self.context,42))
        self.scanner._send_ui.assert_not_called()

    def test_other_household_sim_cannot_read_workday_findings(self):
        self.career.sim_info=types.SimpleNamespace(sim_id=7)
        self.assertFalse(doctor.open_patients());self.hub._window.assert_not_called()

    def test_missing_career_or_pack_refuses(self):
        self.career=None
        self.assertFalse(doctor.open_patients())
        doctor.available.return_value=False
        self.assertIsNone(doctor._context())

    def test_patient_selection_binds_its_id_and_context(self):
        doctor.open_patients()
        callback=self.hub._window.call_args[0][2][0][2]
        with patch.object(doctor,'show_patient') as show:
            callback();show.assert_called_once_with(self.context,42)

    def test_only_running_whitelisted_native_symptom_activity_is_reported(self):
        def activity(name,running):
            return types.SimpleNamespace(affordance=types.SimpleNamespace(__name__=name),running=running)
        cough=activity('idle_Buff_SickessSystem_Symptom_CoughSneeze_mild',True)
        self.patient.si_state=[cough,activity('idle_Buff_SickessSystem_Symptom_Dizzy_severe',False)]
        self.patient.queue=[cough,activity('unrelated_CoughSneeze',True)]
        self.assertEqual(doctor._activity(self.patient),('Coughing or sneezing',))

    def test_missing_activity_is_not_announced_as_no_symptoms(self):
        doctor.show_section(self.context,42,'activity')
        self.assertEqual(self.hub._window.call_args[0][2][0][0],'No mapped symptom animation is running now.')

    def test_unlabelled_findings_never_speak_internal_tuning_names(self):
        hidden=type('buff_SecretDiseaseAnswer',(),{})
        self.tracker.discovered_symptoms=(hidden,)
        doctor.show_section(self.context,42,'symptoms')
        self.assertEqual(self.hub._window.call_args[0][2][0][0],'Recorded finding; game label unavailable')
        self.assertNotIn('SecretDisease',repr(self.hub._window.call_args))

    def test_recorded_exam_uses_native_label_without_executing_it(self):
        context_module=types.SimpleNamespace(InteractionContext=Mock(return_value='label context'))
        context_module.InteractionContext.SOURCE_SCRIPT=1
        native=Mock();native.get_name.return_value='Localized exam'
        self.tracker.exams_performed=(native,)
        with patch.dict(sys.modules, **{'interactions.context':context_module,
                        'interactions.priority':types.SimpleNamespace(Priority=types.SimpleNamespace(Low=1))}):
            doctor.show_section(self.context,42,'exams')
        native.get_name.assert_called_once_with(target=self.patient,context='label context',apply_name_modifiers=False)
        self.assertEqual(self.hub._window.call_args[0][2][0][0],'Localized exam')
        self.assertEqual(native.method_calls,[unittest.mock.call.get_name(target=self.patient,context='label context',apply_name_modifiers=False)])

    def test_native_pick_opens_only_the_patient_menu_without_scanner_mutation(self):
        self.assertTrue(doctor.open_interactions(self.context,42))
        self.scanner._send_ui.assert_called_once_with('A11y|pick|42|2|123|Patient|1.000|2.000|3.000|0')

    def test_native_pick_preserves_large_lot_identity_using_existing_sentinel(self):
        self.services.active_lot=lambda:types.SimpleNamespace(lot_id=2**60)
        doctor.open_interactions(self.context,42)
        self.assertIn('|2|0|',self.scanner._send_ui.call_args[0][0])

    def test_invalid_position_does_not_send_a_pick(self):
        self.patient.position.x=float('nan')
        self.assertFalse(doctor.open_interactions(self.context,42));self.scanner._send_ui.assert_not_called()

    def test_diagnostics_require_logging_and_dont_speak_hidden_buff_names(self):
        self.assertFalse(doctor.inspect_patient(self.context,42))
        self.info.Buffs=[type('hiddenDiseaseBuff',(),{})()]
        speech.log_enabled=True
        self.assertTrue(doctor.inspect_patient(self.context,42))
        self.assertNotIn('hiddenDiseaseBuff',repr(speech.speak.call_args_list))
        self.assertIn('hiddenDiseaseBuff',repr(speech.log_line.call_args_list))

    def test_patient_discovery_uses_only_live_patient_situations(self):
        class PatientSituation:
            def get_patient(inner):return self.patient
        situation=PatientSituation();situation._cur_state=type('WaitingState',(),{})()
        self.services.get_zone_situation_manager=lambda:{1:situation,2:object()}
        # setUp patched this helper; obtain the original implementation explicitly.
        with patch.dict(sys.modules, **{'situations.complex.patient_situation_base':
                        types.SimpleNamespace(PatientSituationBase=PatientSituation)}):
            self.assertEqual(REAL_PATIENTS(),{42:(self.patient,'patient waiting')})
            self.patient.is_hidden=lambda:True
            self.assertEqual(REAL_PATIENTS(),{})

    def test_status_and_list_counts_do_not_mark_discovery_or_choose_treatment(self):
        before=vars(self.tracker).copy()
        self.assertTrue(doctor.show_patient(self.context,42))
        self.assertEqual(vars(self.tracker),before)
        self.scanner._send_ui.assert_not_called()


REAL_PATIENTS=doctor._patients
if __name__=='__main__':unittest.main()
