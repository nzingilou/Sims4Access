"""Physical GDI capture and guaranteed roof-drag release, without screen input."""
import ast
import contextlib
import pathlib
import sys
import types
import unittest
from unittest.mock import Mock,patch

source=(pathlib.Path(__file__).resolve().parents[1]/'Scripts/tyjokr_a11y_plus_draw.py').read_text(encoding='utf-8')
tree=ast.parse(source)
functions=ast.Module(body=[n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name in ('_find_handle','_drag_screen','_park')])


class Tests(unittest.TestCase):
    def setUp(self):
        self.active=False;self.events=[]
        self.geometry=(1,0,0,2880,1800,192)
        self.api=types.SimpleNamespace(mouse_event=Mock())
        @contextlib.contextmanager
        def physical(u):
            self.active=True;self.events.append('physical')
            try:yield
            finally:self.active=False;self.events.append('restored')
        self.coordinates=types.SimpleNamespace(_api=lambda:self.api,physical_context=physical,window=Mock(side_effect=lambda u:self.geometry))
        self.patch=patch.dict(sys.modules,tyjokr_a11y_build_coordinates=self.coordinates)
        self.patch.start();self.addCleanup(self.patch.stop)
        self.build=types.SimpleNamespace(move_to=Mock(),_mouse=Mock(),LEFT_DOWN=2,LEFT_UP=4)
        self.capture=Mock(side_effect=self.pixels)
        self.ns={'build':self.build,'time':types.SimpleNamespace(sleep=Mock()),'core':types.SimpleNamespace(log=Mock()),'_grab_screen':self.capture}
        exec(compile(functions,'roof input functions','exec'),self.ns)

    def pixels(self,x,y,w,h):
        self.assertTrue(self.active,'GDI capture must share physical DPI context with projections')
        data=bytearray(w*h*4)
        for yy in range(h//2-1,h//2+2):
            for xx in range(w//2-1,w//2+2):data[(yy*w+xx)*4:(yy*w+xx)*4+3]=bytes([255,255,255])
        return bytes(data)

    def test_capture_uses_physical_context_at_200_percent_and_restores_it(self):
        self.assertEqual(self.ns['_find_handle'](100,100),(100,100))
        self.assertFalse(self.active);self.assertEqual(self.events,['physical','restored'])

    def test_search_never_captures_another_window_or_outside_game(self):
        self.assertIsNone(self.ns['_find_handle'](10,10));self.capture.assert_not_called()
        self.assertFalse(self.active)

    def test_changed_window_during_capture_is_refused(self):
        self.coordinates.window.side_effect=[self.geometry,(1,0,0,1920,1080,144)]
        with self.assertRaises(RuntimeError):self.ns['_find_handle'](100,100)
        self.assertFalse(self.active)

    def test_failed_capture_restores_dpi_context(self):
        self.capture.side_effect=RuntimeError('capture failed')
        with self.assertRaises(RuntimeError):self.ns['_find_handle'](100,100)
        self.assertFalse(self.active)

    def test_drag_releases_its_button_after_mid_drag_failure(self):
        self.build.move_to.side_effect=[None,None,RuntimeError('focus lost')]
        with self.assertRaises(RuntimeError):self.ns['_drag_screen']((100,100),(200,200))
        self.assertEqual([c[0][0] for c in self.build._mouse.call_args_list],[2,4])

    def test_drag_release_survives_guarded_release_refusal(self):
        def mouse(flag):
            if flag==4:raise RuntimeError('window lost')
        self.build._mouse.side_effect=mouse
        self.ns['_drag_screen']((100,100),(200,200))
        self.api.mouse_event.assert_called_once_with(4,0,0,0,0)

    def test_failed_mouse_down_still_releases_possible_partial_press(self):
        self.build._mouse.side_effect=[RuntimeError('partial input'),None]
        with self.assertRaises(RuntimeError):self.ns['_drag_screen']((100,100),(200,200))
        self.assertEqual([c[0][0] for c in self.build._mouse.call_args_list],[2,4])

    def test_roof_parking_uses_physical_game_client_with_window_origin(self):
        self.geometry=(1,100,50,1920,1080,144)
        def move(x,y):
            self.assertTrue(self.active)
            self.assertEqual((x,y),(1828,968))
        self.build.move_to.side_effect=move
        self.ns['_park']()
        self.build.move_to.assert_called_once_with(1828,968)
        self.assertFalse(self.active)


if __name__=='__main__':unittest.main()
