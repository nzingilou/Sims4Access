'use strict';
const fs=require('fs'),path=require('path'),vm=require('vm'),assert=require('assert');
const src=fs.readFileSync(path.join(__dirname,'../flash/TooltipManager_patched.as'),'utf8');
const match=/public function A11yStepNativeFloor\(([^)]*)\)\s*:\s*void\s*\{/.exec(src);assert(match);
let start=match.index+match[0].length,end=start,depth=1;
while(depth){if(src[end]==='{')depth++;if(src[end]==='}')depth--;end++;}
const strip=s=>s.replace(/:\s*(?:Array|Object|String|Number|Boolean|Error|int|void)\b(?!\s*\()/g,'');
let count=0;
function fixture(){
 const calls=[],f={mode:2,now:1000,zone:'18446744073709551600',info:{curLevel:0,minLevel:-2,maxLevel:4}};
 const ui={mA11yKeyboard:true,mA11yKeyboardLease:2000,mA11yStartupActive:false,mA11yActiveModalRoot:null,mA11yPendingScope:null,mA11yFloorStepSequence:0,
 A11yModalFrame(){},A11yWorldHudMode(){return f.mode;},A11yEditing(){return false;},A11yIsModalScope(v){return !!v;},A11yBuildBlocked(){return !!(this.A11yEditing()||this.mA11yActiveModalRoot||this.mA11yPendingScope);}};
 const runtime={Math,Number,String,isFinite,int:Math.trunc,getTimer:()=>f.now,
 CommunicationManager:{CallGameService(name){calls.push([name]);return name==='BBGetCurrentZoneId'?f.zone:f.info;},SendUIMessage(name,data){calls.push([name,data]);}}};
 ui.step=vm.runInNewContext('(function('+strip(match[1])+'){'+strip(src.slice(start,end-1))+'})',runtime).bind(ui);
 return Object.assign(f,{ui,calls,args:['A11y','floorstep',f.zone,'0','1','3']});
}
function sent(f){return f.calls.filter(([n])=>n==='RequestControlPanelSetFloor');}
function test(name,fn){fn();count++;console.log('PASS '+name);}
test('native refresh and existing controller setter receive one explicit step',()=>{const f=fixture();f.ui.step(f.args);assert.equal(sent(f).length,1);assert.equal(sent(f)[0][1].floor,1);assert(f.calls.findIndex(([n])=>n==='BBRefreshLevelData')<f.calls.findIndex(([n])=>n==='RequestControlPanelSetFloor'));assert(!f.calls.some(([n])=>n==='BBSetLevel'));});
test('the same request is not delivered twice',()=>{const f=fixture();f.ui.step(f.args);f.ui.step(f.args);assert.equal(sent(f).length,1);});
test('old requests cannot change a floor after a newer request',()=>{const f=fixture();f.ui.mA11yFloorStepSequence=4;f.ui.step(f.args);assert.equal(sent(f).length,0);});
test('native current floor must still match the captured expected floor',()=>{const f=fixture();f.info.curLevel=2;f.ui.step(f.args);assert.equal(sent(f).length,0);});
test('zone identities are compared exactly without float conversion',()=>{const f=fixture();f.args[2]='18446744073709551601';f.ui.step(f.args);assert.equal(sent(f).length,0);});
test('live mode, startup and expired keyboard leases cannot change floors',()=>{for(const change of [f=>f.mode=1,f=>f.ui.mA11yStartupActive=true,f=>f.now=3000,f=>f.ui.mA11yKeyboard=false]){const f=fixture();change(f);f.ui.step(f.args);assert.equal(sent(f).length,0);}});
test('blocking, pending and editing UI retain ownership',()=>{for(const change of [f=>f.ui.mA11yActiveModalRoot={},f=>f.ui.mA11yPendingScope={},f=>f.ui.A11yEditing=()=>true]){const f=fixture();change(f);f.ui.step(f.args);assert.equal(sent(f).length,0);}});
test('fractional, nonfinite, multi-floor and stale sequence requests refuse',()=>{for(const [i,value] of [[3,'.5'],[4,'NaN'],[4,'3'],[5,'0'],[5,'1.5'],[5,'2147483648']]){const f=fixture();f.args[i]=value;f.ui.step(f.args);assert.equal(sent(f).length,0);}});
test('missing, boolean or inconsistent native bounds refuse',()=>{for(const info of [null,{}, {curLevel:false,minLevel:0,maxLevel:4},{curLevel:0,minLevel:1,maxLevel:4},{curLevel:0,minLevel:-2,maxLevel:0}]){const f=fixture();f.info=info;f.ui.step(f.args);assert.equal(sent(f).length,0);}});
test('a downward step uses the same native controller route',()=>{const f=fixture();f.args[4]='-1';f.ui.step(f.args);assert.equal(sent(f)[0][1].floor,-1);});
test('encoded bridge routes floor steps separately from scanner activation',()=>{assert(src.includes('if(_loc2_[1] == "floorstep") { this.A11yStepNativeFloor(_loc2_); return; }'));});
test('the existing Build guard can exempt an open native catalogue',()=>{const f=fixture();f.ui.mA11yActiveModalRoot={catalogue:true};f.ui.A11yBuildBlocked=()=>false;f.ui.step(f.args);assert.equal(sent(f).length,1);});
console.log(count+' native floor-step checks passed (native controller mocked).');
