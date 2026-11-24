"""Pool transaction refusals and geometry confirmation; never native input."""
import copy
import pathlib
import sys
import types
import unittest
from unittest.mock import Mock, patch

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / 'Scripts'))
import tyjokr_a11y_water_tools as water
REAL_SELECT_TOOL = water._select_tool


class PoolTests(unittest.TestCase):
    def setUp(self):
        self.box = (3, 4, 7, 8)
        self.frame = types.SimpleNamespace(width=30, depth=30,
                    world=lambda e,n:(100+e,200-n), local=lambda x,z:(x-100,200-z))
        self.before = {'inside': [(e,n,False,True,True,0) for e in range(3,7) for n in range(4,8)],
                       'border': [(2,4,False)], 'heights':[0.0]*16, 'rooms':set()}
        self.after = copy.deepcopy(self.before)
        self.after['inside'] = [r[:2]+(True,)+r[3:] for r in self.before['inside']]
        self.state = {'zone':9,'household':1}
        self.build = types.SimpleNamespace(on_main=lambda fn,*args:fn(*args), frame=lambda:self.frame,
                     set_floor=Mock(return_value=True), drag=Mock(), _last_error={'text':'old','at':-1},
                     _cat={'serial':1}, select_item=Mock(), fetch_catalog=Mock(return_value=[('Native tool',0,1)]),
                     _busy=[False])
        self.build.point_and_act=Mock(side_effect=lambda pts,level,act,*args,**kw: (act([(10,20),(30,40)]) or True))
        self.core = types.SimpleNamespace(speak=Mock(),post=lambda fn,*args:fn(*args))
        self.helpers = types.SimpleNamespace(_native_floor=Mock(return_value={'floor':0}))
        self.services=types.SimpleNamespace(object_manager=lambda:{})
        self.patches=[patch.object(water,'_modules',return_value=(self.build,self.core,self.helpers)),
                      patch.object(water,'_context',return_value=self.state),
                      patch.object(water,'_same',return_value=True),patch.object(water,'_log'),
                      patch.object(water,'_survey',side_effect=lambda *args:self.after if self.build.drag.called else self.before),
                      patch.object(water,'_select_tool',return_value=True),
                      patch.object(water.time,'sleep'),patch.dict(sys.modules,{'services':self.services})]
        for p in self.patches:
            p.start();self.addCleanup(p.stop)
        self.addCleanup(lambda:setattr(water,'_selection',None))

    def test_one_native_drag_then_exact_tile_confirmation(self):
        self.assertTrue(water._draw(self.box))
        self.build.drag.assert_called_once_with((10,20),(30,40))
        water._select_tool.assert_called_once_with(self.state)
        self.assertEqual(self.build.point_and_act.call_args[0][:2], ([(103,196),(107,192)],0))
        self.assertTrue(self.build.point_and_act.call_args[1]['overview'])

    def test_bad_sizes_and_coordinates_never_switch_floor(self):
        for box in [(0,4,7,8),(3,4,4,8),(3,4,27,8),(3,4,7,40),(3.5,4,7,8),(True,4,7,8),(3,4,float('nan'),8)]:
            with self.assertRaises((ValueError,RuntimeError)):water._draw(box)
        self.build.set_floor.assert_not_called();self.build.drag.assert_not_called()

    def test_context_change_and_failed_floor_never_draw(self):
        water._same.return_value=False
        with self.assertRaises(RuntimeError):water._draw(self.box)
        water._same.return_value=True;self.build.set_floor.return_value=False
        with self.assertRaises(RuntimeError):water._draw(self.box)
        self.build.drag.assert_not_called()

    def test_existing_pools_and_adjacent_pools_are_not_extended(self):
        self.before['border']=[(2,4,True)]
        with self.assertRaises(RuntimeError):water._draw(self.box)
        self.build.drag.assert_not_called();water._select_tool.assert_not_called()

    def test_unknown_ground_outside_room_and_slopes_stop_before_input(self):
        original=copy.deepcopy(self.before)
        for row in [(3,4,False,None,True,0),(3,4,False,False,True,0),
                    (3,4,False,True,None,0),(3,4,False,True,True,None),(3,4,False,True,True,42)]:
            self.before['inside']=[row]
            with self.assertRaises(RuntimeError):water._draw(self.box)
        self.before=original;self.before['heights'][0]=.3
        with self.assertRaises(RuntimeError):water._draw(self.box)
        self.build.drag.assert_not_called()

    def test_nearby_furniture_and_unknown_objects_are_refused(self):
        obj=types.SimpleNamespace(is_sim=False,is_in_inventory=lambda:False,level=0,
                                  position=types.SimpleNamespace(x=104,z=195))
        self.services.object_manager=lambda:{1:obj}
        self.assertFalse(water._can_draw(self.box,self.frame,self.before))
        self.services.object_manager=lambda:{1:object()}
        self.assertFalse(water._can_draw(self.box,self.frame,self.before))

    def test_changed_site_during_camera_preparation_refuses(self):
        changed=copy.deepcopy(self.before);changed['heights'][0]=.01
        water._survey.side_effect=[self.before,changed]
        with self.assertRaises(RuntimeError):water._draw(self.box)
        self.build.drag.assert_not_called()

    def test_native_floor_change_or_tool_failure_never_drag(self):
        self.helpers._native_floor.return_value={'floor':1}
        with self.assertRaises(RuntimeError):water._draw(self.box)
        self.helpers._native_floor.return_value={'floor':0};water._select_tool.return_value=False
        with self.assertRaises(RuntimeError):water._draw(self.box)
        self.build.drag.assert_not_called()

    def test_wrong_partial_or_oversized_geometry_is_not_success(self):
        for change in ['missing','border','rooms']:
            after=copy.deepcopy(self.after)
            if change=='missing':after['inside'][0]=self.before['inside'][0]
            elif change=='border':after['border']=[(2,4,True)]
            else:after['rooms']={((3,4,7,8),0)}
            self.assertFalse(water._verified(self.before,after))
        empty=copy.deepcopy(self.before);empty['inside']=[]
        self.assertFalse(water._verified(empty,empty))

    def test_unverified_result_does_not_retry_or_undo(self):
        self.after=self.before
        with self.assertRaises(RuntimeError):water._draw(self.box)
        self.build.drag.assert_called_once()
        water._select_tool.assert_called_once()

    def test_survey_timeout_never_draws(self):
        water._survey.return_value=None;water._survey.side_effect=None
        with self.assertRaises(RuntimeError):water._draw(self.box)
        self.build.drag.assert_not_called()

    def test_strict_text_parser_does_not_turn_decimals_into_two_dimensions(self):
        self.assertEqual(water._pair('6 4'),(6,4))
        for text in ['6.5 4','6 4 2','6,4','-2 5','6e2 4','']:
            with self.assertRaises(ValueError):water._pair(text)

    def test_disabled_toggle_and_busy_helper_do_not_start_a_worker(self):
        with patch.object(water,'_enabled',return_value=False),patch.object(water.threading,'Thread') as thread:
            water._start(self.box);thread.assert_not_called()
        self.build._busy[0]=True
        with patch.object(water.threading,'Thread') as thread:
            water._start(self.box);thread.assert_not_called()

    def test_stale_selection_replies_cannot_release_a_draw(self):
        done=Mock();water._selection={'index':0,'name':'Native tool','serial':1,'state':self.state,'done':done}
        for text in ['selected|1|Native tool','selected|0|Other tool','catend|1|1']:
            water.catalog_reply(text)
        done.set.assert_not_called()
        self.build._cat['serial']=2;water.catalog_reply('selected|0|Native tool');done.set.assert_not_called()
        self.build._cat['serial']=1;water._same.return_value=False
        water.catalog_reply('selected|0|Native tool');done.set.assert_not_called()
        water._same.return_value=True;water.catalog_reply('selected|0|Native tool');done.set.assert_called_once()

    def test_no_unknown_tool_is_silently_selected(self):
        # Run the real selection implementation for zero/multiple catalogue tools.
        for entries in [[],[('one',0,1),('two',0,1)]]:
            self.build.fetch_catalog.return_value=entries
            self.assertFalse(REAL_SELECT_TOOL(self.state))
        self.build.select_item.assert_not_called()

    def test_tool_selection_wait_stays_off_the_simulation_pump(self):
        pumping = [False]
        def on_main(fn, *args):
            pumping[0] = True
            try:
                return fn(*args)
            finally:
                pumping[0] = False
        def select(index, name):
            self.assertFalse(pumping[0], 'The worker selection wait must not block the game pump')
            self.assertTrue(self.build._cat['silent_select'])
            water.catalog_reply('selected|{}|{}'.format(index, name))
        self.build.on_main = on_main
        self.build.select_item.side_effect = select
        self.assertTrue(REAL_SELECT_TOOL(self.state))
        self.build.select_item.assert_called_once_with(0, 'Native tool')
        self.assertFalse(self.build._cat['silent_select'])
        self.assertIsNone(water._selection)

    def test_game_native_filter_and_no_terrain_or_money_bypass(self):
        src=pathlib.Path(water.__file__).read_text(encoding='utf-8')
        self.assertEqual(water.POOL_TAG,'BUILDTAG_BLOCK_POOL_TOOL')
        for forbidden in ['bb.moveobjects','modify_funds','motherlode','set_terrain_height','_buildbuy.']:
            self.assertNotIn(forbidden,src)


if __name__=='__main__':unittest.main()
