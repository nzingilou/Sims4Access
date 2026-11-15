/* Execute production AS3 against native-shaped display trees. */
'use strict';
const fs=require('fs'),path=require('path'),vm=require('vm');
const fixture=fs.readFileSync(path.join(__dirname,'test_flash_navigation_v10.js'),'utf8');
const head=fixture.slice(0,fixture.indexOf('let passed = 0;'));
const checks=String.raw`
let passed=0;
function test(name,run){run();passed++;console.log('PASS '+name);}
function ui(){const u=manager();u.A11yIsLive=method(tooltip,'A11yIsLive');return u;}
function button(p,name){const b=p.add(new MovieClip(name,'olympus.gui.buttons::Button'));b.focusable=true;b.enabled=true;return b;}
function stops(u,row){const a=[];u.A11yCollectFocusables(row,a,0);return a;}
function text(u,row){const a=[];u.A11yCollectText(row,a,0,false);return a.map(x=>x.slice(x.lastIndexOf('|')+1));}
for(const kind of ['widgets.Gameplay.Clubs.controls::ClubRulesCellView','widgets.shared.controls::RuleCellView','widgets.shared.controls::FoodCellView'])test(kind+' exposes visible Remove without activating',()=>{
 const u=ui(),r=new MovieClip('row',kind);r.focusable=true;r.btnDelete=button(r,'btnDelete');r.activate=r.btnDelete.activate=()=>{throw Error('Traversal must not activate');};
 assert.deepStrictEqual(stops(u,r),[r,r.btnDelete]);r.btnDelete.visible=false;assert.deepStrictEqual(stops(u,r),[r]);r.visible=false;assert.deepStrictEqual(stops(u,r),[]);
});
test('hover-owned Remove stays hidden until native hover shows it',()=>{
 const u=ui(),r=new MovieClip('row','widgets.Gameplay.Clubs.controls::ClubRulesCellView');r.focusable=true;r.btnDelete=button(r,'btnDelete');r.btnDelete.visible=false;
 assert.deepStrictEqual(stops(u,r),[r]);assert.equal(r.btnDelete.visible,false);r.btnDelete.visible=true;assert.deepStrictEqual(stops(u,r),[r,r.btnDelete]);
});
test('restaurant course exposes dishes and Add instead of inert heading',()=>{
 const u=ui(),r=new MovieClip('course','widgets.Restaurant.RestaurantMenu::CourseCellView');r.focusable=true;r.txtCourseLabel=r.add(new TextField('txtCourseLabel','Native course heading'));r.mcFoodGrid=r.add(new MovieClip('mcFoodGrid'));
 const add=button(r.mcFoodGrid,'add'),dish=button(r.mcFoodGrid,'dish');assert.deepStrictEqual(stops(u,r),[r.txtCourseLabel,add,dish]);assert.deepStrictEqual(text(u,r.txtCourseLabel),['Native course heading']);dish.visible=false;assert.deepStrictEqual(stops(u,r),[r.txtCourseLabel,add]);r.txtCourseLabel.visible=false;assert.deepStrictEqual(stops(u,r),[add]);
});
for(const kind of ['widgets.shared.controls::ButtonWarningContainer','widgets.Gameplay.RestaurantSettings::GenericTextButtonWarningContainer'])test(kind+' exposes actual inner buttons',()=>{
 const u=ui(),r=new MovieClip('wrapper',kind);r.focusable=true;r.btnButton=button(r,'btnButton');r.btnTextButton=button(r,'btnTextButton');r.btnButton.visible=false;
 assert.deepStrictEqual(stops(u,r),[r.btnTextButton]);r.btnTextButton.visible=false;r.btnButton.visible=true;assert.deepStrictEqual(stops(u,r),[r.btnButton]);
});
test('small-business protected actions accessible through public mcContent',()=>{
 const u=ui(),r=new MovieClip('employee','widgets.Gameplay.SmallBusinessEmployeeManagement.controls::SmallBusinessEmployeeCellView');r.focusable=true;r.enabled=false;r.mcContent=r.add(new MovieClip('mcContent'));
 r.mcContent.btnSalary=button(r.mcContent,'btnSalary');r.mcContent.btnFire=button(r.mcContent,'btnFire');assert(!('btnSalary' in r));assert(!('btnFire' in r));
 assert.deepStrictEqual(stops(u,r),[r,r.mcContent.btnSalary,r.mcContent.btnFire]);r.mcContent.btnSalary.visible=r.mcContent.btnFire.visible=false;assert.deepStrictEqual(stops(u,r),[r]);
});
test('unrelated cell retains original traversal',()=>{
 const u=ui(),r=new MovieClip('row','other::CourseCellView');r.focusable=true;r.btnDelete=button(r,'btnDelete');assert.deepStrictEqual(stops(u,r),[r]);assert.equal(u.A11yCompositeRow(r),false);
});
for(const [kind,prefix] of [['ManagementSettingsContainer','btnDropdown'],['EmployeeSettingsContainer','btnOutfit']])test(kind+' reads native sibling labels with existing values',()=>{
 const u=ui(),r=new MovieClip('settings','widgets.Gameplay.BusinessSettings::'+kind);
 for(let i=1;i<=3;i++){const b=button(r,prefix+i);r[prefix+i]=b;r['txtLabel'+i]=r.add(new TextField('txtLabel'+i,'Localized '+i));const lines=['0|0|Current value'];u.A11yOptionsRowLabel(b,lines);assert.deepStrictEqual(lines,['-999998|0|Localized '+i,'0|0|Current value']);}
});
test('business label requires exact control identity and live field',()=>{
 const u=ui(),r=new MovieClip('settings','widgets.Gameplay.BusinessSettings::ManagementSettingsContainer');r.txtLabel1=r.add(new TextField('txtLabel1','Markup'));r.btnDropdown1=button(r,'btnDropdown1');const fake=button(r,'btnDropdown1');
 let lines=[];u.A11yOptionsRowLabel(fake,lines);assert.deepStrictEqual(lines,[]);r.visible=false;lines=[];u.A11yOptionsRowLabel(r.btnDropdown1,lines);assert.deepStrictEqual(lines,[]);r.visible=true;r.txtLabel1.visible=false;lines=[];u.A11yOptionsRowLabel(r.btnDropdown1,lines);assert.deepStrictEqual(lines,[]);
});
test('salary/fire labels retain employee context from actual mcContent',()=>{
 const u=ui(),r=new MovieClip('employee','widgets.Gameplay.SmallBusinessEmployeeManagement.controls::SmallBusinessEmployeeCellView');r.mcContent=r.add(new MovieClip('mcContent'));r.mcContent.txtSimName=r.mcContent.add(new TextField('txtSimName','Employee Name'));
 for(const name of ['btnSalary','btnFire']){r.mcContent[name]=button(r.mcContent,name);const lines=['0|0|Native action'];u.A11yOptionsRowLabel(r.mcContent[name],lines);assert.deepStrictEqual(lines,['-999998|0|Employee Name','0|0|Native action']);}
});
test('unrelated settings do not gain guessed labels',()=>{
 const u=ui(),r=new MovieClip('settings','other::ManagementSettingsContainer');r.txtLabel1=r.add(new TextField('txtLabel1','Unexpected'));r.btnDropdown1=button(r,'btnDropdown1');const lines=[];u.A11yOptionsRowLabel(r.btnDropdown1,lines);assert.deepStrictEqual(lines,[]);
});
test('jewelry narration follows selected/empty/not-needed native branches',()=>{
 const u=ui(),r=new MovieClip('material','widgets.Gameplay.JewelryCrafting::JewelryMaterialCellView');r.mcContent=r.add(new MovieClip('mcContent'));r.mcContent.add(new TextField('txtName','Selected metal'));r.mcContent.add(new TextField('txtSecondary','Native price'));
 r.mcLabels=r.add(new MovieClip('mcLabels'));r.mcLabels.add(new TextField('txtClick','Choose a metal'));r.mcLabels.visible=false;r.txtNotNeededCrystal=r.add(new TextField('txtNotNeededCrystal','Crystal not needed'));r.txtNotNeededCrystal.visible=false;
 assert.deepStrictEqual(text(u,r),['Selected metal','Native price']);r.mcContent.visible=false;r.mcLabels.visible=true;assert.deepStrictEqual(text(u,r),['Choose a metal']);r.mcLabels.visible=false;r.txtNotNeededCrystal.visible=true;assert.deepStrictEqual(text(u,r),['Crystal not needed']);
});
test('unrelated transient hidden branches retain original row behavior',()=>{
 const u=ui(),r=new MovieClip('row','another::JewelryMaterialCellView'),branch=r.add(new MovieClip('mcLabels'));branch.visible=false;branch.add(new TextField('label','Transient text'));assert.deepStrictEqual(text(u,r),['Transient text']);
});
test('club reward keeps existing hidden-price handling and visible-price narration',()=>{
 const u=ui(),r=new MovieClip('reward','widgets.Gameplay.Clubs.ClubRewards.controls::RewardCellView'),c=r.add(new MovieClip('mcTextContainer')),cost=c.add(new TextField('txtAmount','500 club points'));
 cost.visible=false;assert.deepStrictEqual(text(u,r),[]);cost.visible=true;assert.deepStrictEqual(text(u,r),['500 club points']);r.kind='other::RewardCellView';cost.visible=false;assert.equal(u.A11yTextDecoration(cost),false);
});
test('exposed native actions preserve enabled/visibility checks',()=>{
 const u=ui(),r=new MovieClip('wrapper','widgets.shared.controls::ButtonWarningContainer'),b=button(r,'btnTextButton');u.A11yClickControl=method(tooltip,'A11yClickControl');const calls=[];u.A11ySafeDispatch=(target,event)=>calls.push([target,event]);runtime.MouseEvent={MOUSE_DOWN:'down',MOUSE_UP:'up',CLICK:'click'};
 b.enabled=false;assert.equal(u.A11yClickControl(b),false);assert.equal(calls.length,0);b.enabled=true;assert.equal(u.A11yClickControl(b),true);assert.deepStrictEqual(calls,[[b,'down'],[b,'up'],[b,'click']]);r.visible=false;calls.length=0;assert.equal(u.A11yClickControl(b),false);assert.equal(calls.length,0);
});
console.log(passed+' proactive native UI checks passed (not live-game verification).');
`;
vm.runInNewContext(head+checks,{require,console,__dirname},{filename:"proactive-native-fixtures"});
