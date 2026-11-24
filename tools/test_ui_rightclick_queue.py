"""The unbound right-click message uses the existing activation epoch fence."""
import unittest
from unittest.mock import patch
import test_scanner_v5 as env
keys=env.keys
class RightClickQueueTests(unittest.TestCase):
 def setUp(self):
  keys._input_epoch=0
  env.queue.clear();env.messages.clear()
  self.state=patch.multiple(keys,_enabled=True,_modal_active=True,_editing_active=False)
  self.state.start();self.addCleanup(self.state.stop)
 def test_shift_enter_routes_only_the_explicit_ui_action(self):
  self.assertEqual(keys._plain_message(0x0D,shift=True),'A11yRightClick')
  self.assertEqual(keys._plain_message(0x0D),'A11yActivate')
 def test_shift_enter_never_places_or_opens_scanner_rows(self):
  keys._modal_active=False
  self.assertIsNone(keys._plain_message(0x0D,shift=True))
 def test_typing_and_control_or_alt_enter_are_not_right_click(self):
  for kwargs in ({'ctrl':True,'shift':True},{'alt':True,'shift':True}):
   self.assertIsNone(keys._plain_message(0x0D,**kwargs))
  keys._editing_active=True
  self.assertIsNone(keys._plain_message(0x0D,shift=True))
 def test_keyboard_disabled_never_right_clicks(self):
  keys._enabled=False
  self.assertIsNone(keys._plain_message(0x0D,shift=True))
 def test_explicit_request_uses_current_epoch(self):
  keys._send('A11yRightClick');env.drain()
  self.assertEqual(env.messages,['A11yRightClick'])
 def test_changed_owner_drops_queued_request(self):
  keys._send('A11yRightClick');keys._input_epoch+=1;env.drain()
  self.assertEqual(env.messages,[])
 def test_ordinary_activation_unchanged(self):
  keys._send('A11yActivate');env.drain()
  self.assertEqual(env.messages,['A11yActivate'])
if __name__=='__main__':unittest.main()
