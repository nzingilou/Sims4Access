/* Execute the unbound right-click action; no game or cheat commands run. */
'use strict';
const fs=require('fs'),path=require('path'),vm=require('vm');
const fixture=fs.readFileSync(path.join(__dirname,'test_flash_navigation_v10.js'),'utf8');
const head=fixture.slice(0,fixture.indexOf('let passed = 0;'));
const checks=String.raw`
let passed=0;
function test(name,run){run();passed++;console.log('PASS '+name);}
const cls={};for(const n of ['GenericCheatsExtension','ProgressBarCheatExtension','BuffCheatsExtension','MoneyAndBucksCheatsExtension','MilestonesCheatsExtension'])cls[n]=function(){};
runtime.MouseEvent={CLICK:'click'};
runtime.MouseEventEx=function(type,bubbles,cancelable){Object.assign(this,{type,bubbles,cancelable,buttonIdx:0,localX:0,localY:0});};runtime.MouseEventEx.RIGHT_BUTTON=1;
runtime.Point=function(x,y){this.x=x;this.y=y;};runtime.isFinite=Number.isFinite;
const adapted=tooltip.replace(/:MouseEventEx\b/g,':Object').replace(/:Class\b/g,':Object').replace(/\s+as\s+Class\b/g,'');
function fixture(kind='GenericCheatsExtension'){
 const u=manager(),scope=new MovieClip('panel'),target=scope.add(new MovieClip('target','NativeCheatControl')),messages=[],events=[],lookups=[];
 Object.assign(u,{mA11yKeyboard:true,mA11yKeyboardLease:999999,mA11yStartupActive:false,mA11yPendingScope:null,mA11yIdxDir:0,mA11yScope:scope,mA11yFocused:target,mA11yActiveModalRoot:null,mA11yActivating:false,A11yModalFrame(){},A11yWorldHudMode:()=>1,A11yIntersectsStage:()=>true,A11yEditing:()=>false,A11yPostToPython:(channel,payload)=>messages.push([channel,payload])});
 u.A11yIsLive=method(tooltip,'A11yIsLive');
 for(const n of ['A11yRightClickOwner','A11yTryRightClick','A11yMsgRightClick'])u[n]=method(adapted,n);
 runtime.getDefinitionByName=name=>{const c=cls[name.split('.').pop()];if(!c)throw Error('absent');return c;};
 const extension=kind==='GenericCheatsExtension'?{cheatType:'time'}:kind==='ProgressBarCheatExtension'?{mID:'native-commodity'}:{buff_id:'native-buff'};
 target.GetExtension=(c,create)=>{lookups.push([c,create]);assert.equal(create,false);return c===cls[kind]?extension:null;};
 target.enabled=true;target.mouseEnabled=true;
 target.getBounds=()=>({x:10,y:20,width:100,height:40});target.localToGlobal=p=>({x:p.x+200,y:p.y+300});target.globalToLocal=p=>({x:p.x-200,y:p.y-300});target.hitTestPoint=(x,y)=>x>=210&&x<=310&&y>=320&&y<=360;
 target.dispatchEvent=event=>{event.stageX=event.localX+200;event.stageY=event.localY+300;events.push(event);};
 return {u,scope,target,messages,events,lookups,extension};
}
test('one native right CLICK is dispatched with no down/up, left click or bubbling',()=>{const f=fixture();assert.equal(f.u.A11yTryRightClick(),true);assert.equal(f.events.length,1);const e=f.events[0];assert.equal(e.type,'click');assert.equal(e.buttonIdx,1);assert.equal(e.bubbles,false);assert.equal(e.stageX,260);assert.equal(e.stageY,340);assert.equal(f.u.mA11yActivating,false);assert(f.lookups.every(x=>x[1]===false));assert(f.messages.some(x=>x[1].startsWith('right-click|sent|')));});
test('native progress bar supplies click coordinates; only the owner gets an event',()=>{const f=fixture('ProgressBarCheatExtension'),bar=f.target.add(new MovieClip('mcBar'));f.extension.mcProgressBar=bar;bar.getBounds=()=>({x:0,y:0,width:80,height:12});bar.localToGlobal=p=>({x:p.x+220,y:p.y+320});bar.hitTestPoint=()=>true;bar.dispatchEvent=()=>{throw Error('Do not trigger the second bar listener');};assert.equal(f.u.A11yTryRightClick(),true);assert.equal(f.events.length,1);assert.equal(f.events[0].stageX,260);assert.equal(f.events[0].stageY,326);});
test('missing UI Cheats class refuses without constructing extensions or clicking',()=>{const f=fixture();runtime.getDefinitionByName=()=>{throw Error('not installed');};assert.equal(f.u.A11yTryRightClick(),false);assert.equal(f.events.length,0);assert.equal(f.lookups.length,0);});
test('unsupported control does not acquire a cheat extension',()=>{const f=fixture();f.target.GetExtension=(c,create)=>{assert.equal(create,false);return null;};assert.equal(f.u.A11yTryRightClick(),false);assert.equal(f.events.length,0);});
for(const [name,change] of [['keyboard off',f=>f.u.mA11yKeyboard=false],['expired lease',f=>f.u.mA11yKeyboardLease=1],['startup',f=>f.u.mA11yStartupActive=true],['Build Mode',f=>f.u.A11yWorldHudMode=()=>2],['typing',f=>f.u.A11yEditing=()=>true],['pending scope',f=>f.u.mA11yPendingScope=new MovieClip()],['pending grid navigation',f=>f.u.mA11yIdxDir=1],['hidden target',f=>f.target.visible=false],['hidden ancestor',f=>f.scope.visible=false],['disabled owner',f=>f.target.enabled=false],['mouse-disabled owner',f=>f.target.mouseEnabled=false],['different scope',f=>f.u.mA11yScope=new MovieClip()],['covering modal',f=>f.u.mA11yActiveModalRoot=new MovieClip()]])test(name+' refuses safely',()=>{const f=fixture();change(f);assert.equal(f.u.A11yTryRightClick(),false);assert.equal(f.events.length,0);});
test('modal refresh occurs before selecting a target',()=>{const f=fixture();f.u.A11yModalFrame=()=>{f.u.mA11yFocused=null;};assert.equal(f.u.A11yTryRightClick(),false);assert.equal(f.events.length,0);});
test('progress bar must belong to its owner and have a native ID',()=>{const f=fixture('ProgressBarCheatExtension');f.extension.mcProgressBar=new MovieClip('unrelated');assert.equal(f.u.A11yTryRightClick(),false);const bar=f.target.add(new MovieClip('mcBar'));f.extension.mcProgressBar=bar;f.extension.mID='';assert.equal(f.u.A11yTryRightClick(),false);assert.equal(f.events.length,0);});
test('hidden and off-stage progress bars refuse',()=>{const f=fixture('ProgressBarCheatExtension'),bar=f.target.add(new MovieClip('mcBar'));f.extension.mcProgressBar=bar;bar.visible=false;assert.equal(f.u.A11yTryRightClick(),false);bar.visible=true;f.u.A11yIntersectsStage=()=>false;assert.equal(f.u.A11yTryRightClick(),false);assert.equal(f.events.length,0);});
test('invalid geometry refuses before event dispatch',()=>{const f=fixture();f.target.getBounds=()=>({x:0,y:0,width:0,height:5});assert.equal(f.u.A11yTryRightClick(),false);f.target.getBounds=()=>({x:0,y:0,width:10,height:10});f.target.localToGlobal=()=>({x:NaN,y:10});assert.equal(f.u.A11yTryRightClick(),false);assert.equal(f.events.length,0);});
test('an existing ancestor extension is used once without bubbling',()=>{const f=fixture();const label=f.target.add(new TextField('label','Native value'));f.u.mA11yFocused=label;assert.equal(f.u.A11yTryRightClick(),true);assert.equal(f.events.length,1);assert.equal(f.events[0].bubbles,false);});
test('lookup never crosses the owned scope',()=>{const f=fixture();f.u.mA11yScope=f.target;f.target.GetExtension=()=>null;f.scope.GetExtension=()=>{throw Error('Do not inspect outside scope');};assert.equal(f.u.A11yTryRightClick(),false);assert.equal(f.events.length,0);});
test('failed extended event construction cannot fall back to a left click',()=>{const f=fixture();const saved=runtime.MouseEventEx;runtime.MouseEventEx=function(){throw Error('unavailable');};assert.equal(f.u.A11yTryRightClick(),false);assert.equal(f.events.length,0);runtime.MouseEventEx=saved;});
test('dispatcher errors reset activation state and report unavailable',()=>{const f=fixture();f.target.dispatchEvent=()=>{throw Error('unloaded');};f.u.A11yMsgRightClick();assert.equal(f.u.mA11yActivating,false);assert(f.messages.some(x=>x[1]==='right-click|blocked'));assert(f.messages.some(x=>x[0]==='a11y.widget_enc'));});
test('invalid inverse transform refuses',()=>{const f=fixture();f.target.globalToLocal=()=>({x:NaN,y:1});assert.equal(f.u.A11yTryRightClick(),false);assert.equal(f.events.length,0);});
test('off-stage hit point refuses',()=>{const f=fixture();f.target.localToGlobal=()=>({x:2000,y:340});f.target.hitTestPoint=()=>true;assert.equal(f.u.A11yTryRightClick(),false);assert.equal(f.events.length,0);});
test('empty native cheat type refuses',()=>{const f=fixture();f.extension.cheatType='';assert.equal(f.u.A11yTryRightClick(),false);assert.equal(f.events.length,0);});
test('currency listener uses the focused child receiver, once',()=>{const f=fixture('MoneyAndBucksCheatsExtension'),label=f.target.add(new MovieClip('currency'));f.u.mA11yFocused=label;label.hasEventListener=type=>type==='click';Object.assign(label,{getBounds:f.target.getBounds,localToGlobal:f.target.localToGlobal,globalToLocal:f.target.globalToLocal,hitTestPoint:f.target.hitTestPoint,dispatchEvent:f.target.dispatchEvent});f.target.hasEventListener=()=>true;f.target.dispatchEvent=()=>{throw Error('Do not dispatch again to parent');};assert.equal(f.u.A11yTryRightClick(),true);assert.equal(f.events.length,1);assert.equal(f.events[0].bubbles,false);});
test('milestone setup without a click receiver refuses',()=>{const f=fixture('MilestonesCheatsExtension');f.target.hasEventListener=()=>false;assert.equal(f.u.A11yTryRightClick(),false);assert.equal(f.events.length,0);});
console.log(passed+' native right-click checks passed (not live-game verification).');
`;
vm.runInNewContext(head+checks,{require,console,__dirname},{filename:"rightclick-fixtures"});
