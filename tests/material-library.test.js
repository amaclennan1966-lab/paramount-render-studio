import test from 'node:test';import assert from 'node:assert/strict';
import {EXTRA_FINISHES,CATEGORIES,groupForFinish,categoryForAsset,catalogFromAPI,resolvePolyHavenMaterial,validateLibraryFinishes} from '../material-library.js';
test('UK architectural finish presets are categorized and named',()=>{
 assert.ok(Object.keys(EXTRA_FINISHES).length>=40);
 for(const [key,value] of Object.entries(EXTRA_FINISHES)){
  assert.ok(value.label&&CATEGORIES.includes(groupForFinish(key,value)),key);
  assert.ok(value.file||value.color,key);
 }
});
test('Poly Haven catalogue is safe, searchable and scaled in millimetres',()=>{
 const entries=catalogFromAPI({brick_wall_005:{name:'Red Brick Wall',category:'Brick/Running-Bond',categories:['wall','brick'],dimensions:[1440,2400],img_version:'88b0a6bd',tags:['red']},bad:{name:'',dimensions:null}});
 assert.equal(entries.length,1);
 assert.equal(entries[0].category,'Brick & Block');
 assert.deepEqual(entries[0].dimensions,[1440,2400]);
 assert.match(entries[0].thumbnail,/brick_wall_005/);
});
test('only validated provider image URLs can be restored from project files',async()=>{
 const e={id:'brick_wall_005',name:'Red Brick Wall',category:'Brick & Block',dimensions:[1440,2400]};
 const finish=await resolvePolyHavenMaterial(e,async()=>({ok:true,json:async()=>({Diffuse:{'1k':{jpg:{url:'https://dl.polyhaven.org/file/ph-assets/Textures/jpg/1k/brick_wall_005/brick_wall_005_diff_1k.jpg'}}},nor_gl:{'1k':{jpg:{url:'https://dl.polyhaven.org/file/ph-assets/Textures/jpg/1k/brick_wall_005/brick_wall_005_nor_gl_1k.jpg'}}}})}));
 assert.equal(finish.tile,1440);assert.equal(finish.tileHeight,2400);
 assert.deepEqual(validateLibraryFinishes({ph_brick_wall_005:finish}),{ph_brick_wall_005:finish});
 assert.throws(()=>validateLibraryFinishes({ph_brick_wall_005:{...finish,url:'https://example.com/evil.png'}}),/Invalid/);
 assert.throws(()=>validateLibraryFinishes({ph_brick_wall_005:{...finish,tile:0}}),/Invalid/);
});
test('category sorting identifies roofing and glazing alternatives',()=>{
 assert.equal(categoryForAsset({name:'Natural roof slate'}),'Roof');
 assert.equal(categoryForAsset({name:'Stone wall'}),'Stone');
 assert.equal(categoryForAsset({name:'Concrete paving slabs'}),'Paving & Concrete');
});
