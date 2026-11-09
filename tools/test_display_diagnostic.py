"""Read-only, process-scoped display observations and transparent adapters."""
import importlib.util,json,os,pathlib,sys,tempfile,types,unittest
from unittest.mock import Mock,patch
ROOT=pathlib.Path(__file__).resolve().parents[1]
speech=types.SimpleNamespace(log_enabled=True,log_line=Mock(),LOG_PATH='')
commands=types.SimpleNamespace(Command=lambda *a,**k:lambda f:f,CommandType=types.SimpleNamespace(Live=1),CheatOutput=lambda c:lambda s:None)
sys.modules.update(tyjokr_a11y_speech=speech,sims4=types.SimpleNamespace(commands=commands))
sys.modules['sims4.commands']=commands
spec=importlib.util.spec_from_file_location('display',str(ROOT/'Scripts/tyjokr_a11y_display_diagnostic.py'))
d=importlib.util.module_from_spec(spec);spec.loader.exec_module(d)
class API:
 def GetForegroundWindow(self):return 2**40
 def GetWindowThreadProcessId(self,h,p):p._obj.value=os.getpid();return 1
 def GetClientRect(self,h,p):p._obj.left=p._obj.top=0;p._obj.right=1440;p._obj.bottom=900;return 1
 def GetWindowRect(self,h,p):return self.GetClientRect(h,p)
 def ClientToScreen(self,h,p):p._obj.x+=120;p._obj.y+=80;return 1
 def ScreenToClient(self,h,p):p._obj.x-=120;p._obj.y-=80;return 1
 def LogicalToPhysicalPointForPerMonitorDPI(self,h,p):p._obj.x*=2;p._obj.y*=2;return 1
 def GetCursorPos(self,p):p._obj.x=100;p._obj.y=200;return 1
 def GetPhysicalCursorPos(self,p):p._obj.x=200;p._obj.y=400;return 1
 def GetDpiForWindow(self,h):return 192
 def GetThreadDpiAwarenessContext(self):return 1
 def GetWindowDpiAwarenessContext(self,h):return 2
 def GetAwarenessFromDpiAwarenessContext(self,c):return c
 def GetSystemMetrics(self,n):return {0:1440,1:900,76:-100,77:0,78:2880,79:900}[n]
class Tests(unittest.TestCase):
 def setUp(self):
  speech.log_enabled=True;speech.log_line.reset_mock();d._window_start=0;d._count=0
 def snapshot(self,u=None):
  with patch.object(d,'_monitor_scale',return_value=200):return d.windows_snapshot(u or API())
 def test_scaled_offset_client_and_roundtrip(self):
  r=self.snapshot();self.assertEqual(r['hwnd'],2**40)
  self.assertEqual(r['client_size_reported'],[1440,900]);self.assertEqual(r['monitor_scale_percent'],200)
  self.assertEqual(r['samples'][1],{'client':[720,450],'screen_reported':[840,530],
   'client_roundtrip':[720,450],'screen_physical_for_window':[1680,1060]})
  self.assertIsNone(r['game_ui_stage_size'])
 def test_dpi_context_and_cursor_units_are_separate(self):
  r=self.snapshot();self.assertEqual((r['thread_awareness'],r['window_awareness']),(1,2))
  self.assertEqual(r['cursor_reported'],[100,200]);self.assertEqual(r['cursor_physical'],[200,400])
 def test_non_game_foreground_refused_before_reading_metrics(self):
  u=API();u.GetWindowThreadProcessId=lambda h,p:1;u.GetClientRect=Mock()
  self.assertIn('refused',self.snapshot(u));u.GetClientRect.assert_not_called()
 def test_foreground_change_invalidates_snapshot(self):
  u=API();u.GetForegroundWindow=Mock(side_effect=[2**40,9]);self.assertIn('refused',self.snapshot(u))
 def test_optional_apis_and_failed_reads_are_explicit(self):
  u=API();u.GetDpiForWindow=Mock(side_effect=AttributeError);u.GetClientRect=lambda *a:0
  r=self.snapshot(u);self.assertIn('client_rect_reported',r['errors']);self.assertIn('window_dpi',r['errors'])
 def test_options_whitelist_and_no_write(self):
  with tempfile.TemporaryDirectory() as td:
   root=pathlib.Path(td);p=root/'Options.ini';p.write_text('fullscreen=1\nuiscale=100\nprivate_setting=secret\n')
   speech.LOG_PATH=str(root/'Mods/TS4_Access/TS4_Access.log');before=p.read_bytes()
   self.assertEqual(d.saved_options(),{'fullscreen':1,'uiscale':100});self.assertEqual(p.read_bytes(),before)
 def test_logging_off_never_queries_windows(self):
  speech.log_enabled=False
  with patch.object(d,'windows_snapshot') as read:self.assertFalse(d.record('test'));read.assert_not_called()
 def test_options_also_supports_script_at_mods_root(self):
  with tempfile.TemporaryDirectory() as td:
   root=pathlib.Path(td);(root/'Options.ini').write_text('fullscreen=0\n')
   speech.LOG_PATH=str(root/'Mods/TS4_Access.log')
   self.assertEqual(d.saved_options(),{'fullscreen':0})
 def test_options_does_not_search_unrelated_ancestors(self):
  speech.LOG_PATH='C:/unrelated/project/log.txt'
  self.assertEqual(d.saved_options(),{'error':'ValueError'})
 def test_rate_limit_caps_snapshots(self):
  with patch.object(d,'windows_snapshot',return_value={'errors':{}}) as read,patch.object(d,'saved_options',return_value={}):
   for _ in range(40):d.record('test')
   self.assertEqual(read.call_count,30)
 def test_wrappers_preserve_return_values_and_call_counts(self):
  b=types.SimpleNamespace(project=Mock(return_value=(1,2)),_to_screen=Mock(return_value=(3,4)),_stage_size=lambda:(1440,900))
  project,convert=b.project,b._to_screen
  with patch.object(d,'record') as record:
   d.install(b);wrapped=b.project;d.install(b);self.assertIs(b.project,wrapped)
   self.assertEqual(b.project(5,6,1),(1,2));self.assertEqual(b._to_screen(1,2),(3,4))
   project.assert_called_once_with(5,6,1);convert.assert_called_once_with(1,2);self.assertEqual(record.call_count,2)
 def test_wrappers_preserve_original_exceptions(self):
  b=types.SimpleNamespace(project=Mock(side_effect=ValueError('native')), _to_screen=Mock())
  d.install(b)
  with self.assertRaises(ValueError):b.project(1,2,0)
 def test_diagnostic_failure_cannot_change_build_results_or_errors(self):
  b=types.SimpleNamespace(project=Mock(return_value=(1,2)),_to_screen=Mock(side_effect=ValueError('original')))
  d.install(b)
  with patch.object(d,'record',side_effect=RuntimeError('diagnostic')):
   self.assertEqual(b.project(1,2,0),(1,2))
   with self.assertRaisesRegex(ValueError,'original'):b._to_screen(1,2)
 def test_manual_command_uses_delayed_worker_and_no_build_action(self):
  timer=Mock();b=types.SimpleNamespace(_stage_size=lambda:(1,1),project=Mock(),_to_screen=Mock())
  project,convert=b.project,b._to_screen
  with patch.object(d.threading,'Timer',return_value=timer) as make,patch.dict(sys.modules,tyjokr_a11y_plus_build=b),patch.object(d,'record') as record:
   self.assertTrue(d.inspect_display(5));self.assertEqual(make.call_args[0][0],5)
   make.call_args[0][1]();record.assert_called_once_with('manual',build=b)
   project.assert_not_called();convert.assert_not_called();self.assertTrue(b._display_diagnostic_installed)
 def test_private_win32_pointer_signatures(self):
  api=d._api();self.assertIs(api.GetForegroundWindow.restype,d.ctypes.c_void_p)
  self.assertEqual(d.ctypes.sizeof(d.POINT),8);self.assertEqual(d.ctypes.sizeof(d.RECT),16)
 def test_no_input_or_dpi_mutation_apis(self):
  source=(ROOT/'Scripts/tyjokr_a11y_display_diagnostic.py').read_text()
  for forbidden in ['SetCursorPos','SendInput','mouse_event','SetThreadDpiAwarenessContext','SetProcessDpiAwareness']:
   self.assertNotIn(forbidden,source)
if __name__=='__main__':unittest.main()
