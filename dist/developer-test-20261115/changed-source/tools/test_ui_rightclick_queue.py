"""The unbound right-click message uses the existing activation epoch fence."""
import unittest
from unittest.mock import patch
import test_scanner_v5 as env
keys=env.keys
class RightClickQueueTests(unittest.TestCase):
 def setUp(self):
  keys._input_epoch=0
  env.queue.clear();env.messages.clear()
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
