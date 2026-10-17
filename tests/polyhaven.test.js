import test from 'node:test';
import assert from 'node:assert/strict';
import {catalogFromAPI,resolvePolyHavenMaterial,validateLibraryFinishes} from '../polyhaven.js';
const url=(suffix='diff')=>'https://dl.polyhaven.org/file/ph-assets/Textures/jpg/1k/brick_wall_005/brick_wall_005_'+suffix+'_1k.jpg';
const entry={id:'brick_wall_005',name:'Brick wall',category:'Brick',dimensions:[1440,2400]};
const fetcher=async()=>({ok:true,json:async()=>({Diffuse:{'1k':{jpg:{url:url()}}},nor_gl:{'1k':{jpg:{url:url('nor_gl')}}}})});
test('catalogue tolerates malformed metadata and never treats unknown provider units as measured mm',()=>{
 const result=catalogFromAPI({brick_wall_005:{name:'Brick wall',categories:4,tags:null,dimensions:[1.4,2.4]},'../bad':{name:'bad'},blank:{name:' '}});
 assert.equal(result.length,1);assert.equal(result[0].category,'Brick');assert.deepEqual(result[0].dimensions,[2000,2000]);
 assert.throws(()=>catalogFromAPI([]));
});
test('resolution and project roundtrip retain independent physical repeats and allowlisted URLs',async()=>{
 const f=await resolvePolyHavenMaterial(entry,fetcher);
 assert.equal(f.tile,1440);assert.equal(f.tileHeight,2400);
 assert.deepEqual(validateLibraryFinishes({ph_brick_wall_005:f}),{ph_brick_wall_005:f});
 for(const change of [{url:'https://evil.example/a.jpg'},{normalUrl:url()+'?redirect=bad'},{tile:0},{tileHeight:Infinity},{category:'invalid'}])
  assert.throws(()=>validateLibraryFinishes({ph_brick_wall_005:{...f,...change}}));
 assert.throws(()=>validateLibraryFinishes(Object.fromEntries(Array.from({length:61},(_,i)=>['ph_'+i,f]))),/maximum 60/);
});
test('provider failures and unsupported maps fail without accepting arbitrary URLs',async()=>{
 await assert.rejects(resolvePolyHavenMaterial({...entry,id:'../bad'},fetcher));
 await assert.rejects(resolvePolyHavenMaterial(entry,async()=>({ok:false})),/unavailable/);
 await assert.rejects(resolvePolyHavenMaterial(entry,async()=>({ok:true,json:async()=>({})})),/supported/);
});
