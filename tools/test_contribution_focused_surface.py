"""Verify explicit surface placement never falls back to floor or another object."""
import ast
import pathlib
import sys
import types

root = pathlib.Path(__file__).resolve().parents[1]
tree = ast.parse((root / 'contrib-reference/modules/tyjokr_a11y_layers.py').read_text(encoding='utf-8'))
nodes = [n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name in ('_surface_slots', '_finish_on_surface')]
slot = types.SimpleNamespace(empty=True, is_deco_slot=lambda:False, is_valid_for_placement=lambda **kw:True)
target = types.SimpleNamespace(id=9, level=0, position=None, get_runtime_slots_gen=lambda:[slot],
    is_in_inventory=lambda:False, is_hidden=lambda:False, get_household_owner_id=lambda:1)
services = types.ModuleType('services')
services.object_manager=lambda:types.SimpleNamespace(get=lambda ident:target)
services.active_lot=lambda:types.SimpleNamespace(is_position_on_lot=lambda p:True)
place = types.ModuleType('tyjokr_a11y_place')
place._pending={'serial':3}; place._zone_id=lambda:7; place._household_id=lambda:1
destroyed=[]; speech=[]
place._destroy=destroyed.append; place._say_text=lambda *a:speech.append(a[0])
baseline_slot=lambda *a:None; place._free_slot=baseline_slot
sys.modules.update({'services':services,'tyjokr_a11y_place':place})
finished=[]
def finish(obj,item,price,need,position,level,surface,angle,key,exact):
    assert need=='slot'
    assert place._free_slot(obj,position,level)==(target,slot)
    finished.append(obj)
    return True
ns={'_surface_request':None,'_original_finish':finish,'_focused_target':lambda:target,'_log':lambda text:None}
exec(compile(ast.Module(body=nodes),'focused-surface','exec'),ns)
def attempt():
    ns['_surface_request']=(3,42,7,9,'tile')
    return ns['_finish_on_surface']('new TV',{'id':42},100,None,None,0,None,0,'tile')
assert attempt() is True and len(finished)==1
assert place._free_slot is baseline_slot
slot.is_deco_slot=lambda:True
assert attempt() is True and len(finished)==2
finished.pop()
slot.empty=False
assert attempt() is False and len(finished)==1 and destroyed==['new TV']
assert 'no compatible free slot' in speech[-1]
slot.empty=True; slot.is_valid_for_placement=lambda **kw:False
assert attempt() is False and len(finished)==1
assert place._free_slot is baseline_slot
print('1 focused surface scenario checks passed: stand, slot refusal, transaction and helper restoration')
