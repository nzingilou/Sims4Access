"""Native floor-key ownership and current Build-menu routing, without game input."""
import contextlib,pathlib,sys,types,unittest
from unittest.mock import Mock,patch
sys.path.insert(0,str(pathlib.Path(__file__).resolve().parents[1]/'Scripts'))
import tyjokr_a11y_build_helpers as h
class Tests(unittest.TestCase):
 def setUp(self):
  self.floor=0;self.events=[];self.released=False;self.geometry=(1,0,0,1920,1080,96);self.modifier=False;self.stall=False
  self.state={'zone':1,'floor':0,'center':(10,20),'grid':True,'owner':True}
  self.build=types.SimpleNamespace(current_floor=lambda:self.floor,on_main=lambda fn,*args:fn(*args))
  self.u=types.SimpleNamespace(GetAsyncKeyState=lambda k:0x8000 if self.modifier and k==17 else 0,keybd_event=self.key)
  @contextlib.contextmanager
  def physical(u):
   self.events.append('physical-on')
   try:yield
   finally:self.events.append('physical-restored')
  def measure(*args):self.events.append('roundtrip');self.released=True
  self.coords=types.SimpleNamespace(_api=lambda:self.u,physical_context=physical,window=lambda u:self.geometry,_measure=measure)
  h._build,h._coordinates=self.build,self.coords
  self.patches=[patch.object(h,'_state',side_effect=lambda:dict(self.state)),patch.object(h,'_same_world',return_value=True),patch.object(h,'_grid_message',side_effect=self.events.append),patch.object(h,'_grid_released',side_effect=lambda:self.released),patch.object(h,'_restore_grid',side_effect=lambda state:self.events.append('restore-grid') or True),patch.object(h,'_log'),patch.object(h.time,'sleep',return_value=None)]
  for p in self.patches:p.start();self.addCleanup(p.stop)
 def key(self,key,scan,flags,extra):
  self.events.append(('key',key,scan,flags))
  if flags==3 and not self.stall:self.floor += 1 if key==33 else -1
 def test_grid_releases_before_native_key_and_is_restored(self):
  self.assertTrue(h.set_floor(1));self.assertEqual(self.floor,1)
  self.assertLess(self.events.index('A11yBuildGridOff'),self.events.index('roundtrip'))
  self.assertLess(self.events.index('roundtrip'),self.events.index(('key',33,0x49,1)))
  self.assertEqual(self.events[-1],'restore-grid');self.assertIn('physical-restored',self.events)
 def test_downward_and_multiple_levels_follow_native_report(self):
  self.floor=2;self.state['floor']=2
  self.assertTrue(h.set_floor(-1));self.assertEqual(self.floor,-1)
  self.assertEqual(len([x for x in self.events if isinstance(x,tuple) and x[-1]==1]),3)
 def test_already_on_floor_emits_no_input_or_grid_messages(self):
  self.assertTrue(h.set_floor(0));self.assertEqual(self.events,[])
 def test_inactive_grid_is_not_reenabled(self):
  self.state.update(grid=False,owner=False);self.released=True
  self.assertTrue(h.set_floor(1));self.assertNotIn('restore-grid',self.events);self.assertNotIn('A11yBuildGridOff',self.events)
 def test_no_key_before_native_ack(self):
  self.coords._measure=lambda *a:self.events.append('roundtrip')
  with patch.object(h.time,'monotonic',side_effect=[0,3]):self.assertFalse(h.set_floor(1))
  self.assertFalse(any(isinstance(x,tuple) for x in self.events));self.assertIn('restore-grid',self.events)
 def test_native_context_change_refuses_input(self):
  h._same_world.return_value=False
  self.assertFalse(h.set_floor(1));self.assertFalse(any(isinstance(x,tuple) for x in self.events))
 def test_modifier_keys_are_never_borrowed(self):
  self.modifier=True;self.assertFalse(h.set_floor(1));self.assertFalse(any(isinstance(x,tuple) for x in self.events))
 def test_floor_boundary_stops_after_three_unchanged_attempts(self):
  self.stall=True;self.assertFalse(h.set_floor(1))
  self.assertEqual(len([x for x in self.events if isinstance(x,tuple) and x[-1]==1]),3)
 def test_key_up_survives_failure_after_key_down(self):
  h.time.sleep.side_effect=RuntimeError('interrupted')
  self.assertFalse(h.set_floor(1));self.assertIn(('key',33,0x49,3),self.events);self.assertIn('restore-grid',self.events)
 def test_invalid_floor_requests_are_safe(self):
  for value in [True,1.5,float('nan'),float('inf'),10**1000,'1',None]:self.assertFalse(h.set_floor(value))
  self.assertEqual(self.events,[])
 def test_alt_b_resolves_later_menu_wrappers(self):
  build=types.SimpleNamespace(open_menu=Mock(return_value='detached'))
  with patch.dict(sys.modules,tyjokr_a11y_plus_build=build):
   self.assertEqual(h._build_menu(),'detached');build.open_menu=Mock(return_value='colors');self.assertEqual(h._build_menu(),'colors')
if __name__=='__main__':unittest.main()
