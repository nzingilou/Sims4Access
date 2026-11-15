"""Read-only cleaning inspection: execute the module with native-service stubs."""
import importlib.util
import pathlib
import sys
import types
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]
commands = types.ModuleType('sims4.commands')
commands.Command = lambda *a, **kw: lambda f: f
commands.CommandType = types.SimpleNamespace(Live=1)
messages, logs, pending = [], [], []
commands.CheatOutput = lambda connection: messages.append
sims4 = types.ModuleType('sims4'); sims4.commands = commands
sys.modules['sims4'] = sims4; sys.modules['sims4.commands'] = commands
speech = types.ModuleType('tyjokr_a11y_speech'); speech.log_enabled = True; speech.log_line = logs.append
pump = types.ModuleType('tyjokr_a11y_pump'); pump.alive = lambda: True
pump.post = lambda f, *args: pending.append((f, args)) or True
services = types.ModuleType('services')
sys.modules.update(tyjokr_a11y_speech=speech, tyjokr_a11y_pump=pump, services=services)
spec = importlib.util.spec_from_file_location('cleaning', str(ROOT/'diagnostics/tyjokr_a11y_cleaning_diagnostic.py'))
mod = importlib.util.module_from_spec(spec); spec.loader.exec_module(mod)


def resource(name, number, **kw):
    return types.SimpleNamespace(__name__=name, guid64=number, **kw)


class Object:
    is_sim = False
    level = 0
    def __init__(self, number=1, on_lot=True):
        self.id = number; self.position = types.SimpleNamespace(x=number, z=2)
        self.position.on_lot = on_lot
        self.definition = types.SimpleNamespace(id=100, name='Counter')
        state = resource('Cleanliness', 10, linked_stat=resource('Dirt', 20))
        self.state_component = types.SimpleNamespace(values=lambda: iter([resource('Dirty', 11, state=state)]))
        self.inventory = False
    def is_hidden(self): return True
    def is_in_inventory(self): return self.inventory
    def super_affordances(self): return iter([resource('counter_Clean', 30), resource('Use', 31)])
    def set_state(self, *a): raise AssertionError('Must not mutate')
    def potential_interactions(self, *a): raise AssertionError('Must not test interactions')


class Tests(unittest.TestCase):
    def setUp(self):
        mod._job = None; messages.clear(); logs.clear(); pending.clear()
        speech.log_enabled = True
        pump.alive = lambda: True
        pump.post = lambda f, *args: pending.append((f, args)) or True
        self.objects = {n: Object(n) for n in range(1, 31)}
        services.object_manager = lambda: types.SimpleNamespace(values=lambda: self.objects.values(), get=self.objects.get)
        services.active_lot = lambda: types.SimpleNamespace(is_position_on_lot=lambda p: p.on_lot)
        services.current_zone_id = lambda: 123
    def drain(self):
        for _ in range(100):
            if not pending: return
            f,args=pending.pop(0); f(*args)
        self.fail('Unbounded work')
    def test_state_and_hints_are_read_only(self):
        r=mod.describe(Object())
        self.assertEqual(r['states'][0]['value']['id'],11)
        self.assertEqual(r['states'][0]['linked_stat']['id'],20)
        self.assertEqual([a['name'] for a in r['cleaning_action_hints']],['counter_Clean'])
        self.assertTrue(r['hidden'])
    def test_static_action_is_not_classified_as_dirty(self):
        o=Object(); o.state_component=None
        self.assertEqual(mod.describe(o)['states'],[])
        self.assertNotIn('dirty',mod.describe(o))
    def test_objects_without_optional_visibility_inventory_methods_are_retained(self):
        self.objects={1:Object()};self.objects[1].is_hidden=None;self.objects[1].is_in_inventory=None
        self.assertIsNone(mod.describe(self.objects[1])['hidden'])
        mod.inspect_cleaning();self.drain();self.assertTrue(any('object {' in s for s in logs))
    def test_state_limit(self):
        o=Object();o.state_component=types.SimpleNamespace(values=lambda: (resource('Unknown',x) for x in range(100)))
        r=mod.describe(o);self.assertEqual(len(r['states']),64);self.assertTrue(r['states_truncated'])
    def test_state_error_keeps_object(self):
        o=Object();o.state_component=types.SimpleNamespace(values=lambda: 1/0)
        self.assertEqual(mod.describe(o)['state_error'],'ZeroDivisionError')
    def test_tick_is_batched(self):
        mod.inspect_cleaning(); f,a=pending.pop(0);f(*a)
        self.assertLessEqual(mod._job['visited'],10);self.assertTrue(pending)
        self.drain();self.assertIsNone(mod._job)
    def test_scope_excludes_sims_inventory_and_other_lots(self):
        self.objects[1].is_sim=True;self.objects[2].inventory=True;self.objects[3].position.on_lot=False
        mod.inspect_cleaning();self.drain()
        self.assertEqual(sum('object {' in s for s in logs),27)
    def test_limit_and_cap(self):
        mod.inspect_cleaning(2);self.drain()
        self.assertEqual(sum('object {' in s for s in logs),2)
        mod.inspect_cleaning(99999);self.assertEqual(mod._job['limit'],2000)
    def test_zone_change_stops(self):
        mod.inspect_cleaning();services.current_zone_id=lambda:999;self.drain()
        self.assertIsNone(mod._job);self.assertIn('zone changed',messages[-1])
    def test_cancel_and_busy(self):
        mod.inspect_cleaning();self.assertFalse(mod.inspect_cleaning())
        mod.inspect_cleaning(0);self.drain();self.assertIsNone(mod._job)
        self.assertFalse(any('object {' in s for s in logs))
    def test_no_logging_does_not_start_or_change_setting(self):
        speech.log_enabled=False;self.assertFalse(mod.inspect_cleaning());self.assertFalse(pending)
        self.assertFalse(speech.log_enabled)
    def test_stopped_pump(self):
        pump.post=lambda *a:False
        self.assertFalse(mod.inspect_cleaning());self.assertIsNone(mod._job)
    def test_turning_logging_off_stops_job(self):
        mod.inspect_cleaning();speech.log_enabled=False;self.drain();self.assertIsNone(mod._job)


if __name__ == '__main__': unittest.main()
