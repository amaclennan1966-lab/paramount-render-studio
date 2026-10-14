import {test}from 'node:test';import assert from 'node:assert/strict';import {detectFaces,contains}from '../geometry.js';
const rectangle=(x,y,w,h)=>{const p=[[x,y],[x+w,y],[x+w,y+h],[x,y+h],[x,y]];return p.slice(0,-1).map((a,i)=>[a,p[i+1]]);};
test('closed source wall with window hole stays separate',()=>{const faces=detectFaces([...rectangle(0,0,100,80),...rectangle(20,20,30,40)]);assert.equal(faces.length,2);assert.equal(faces[1].holes.length,1);assert.equal(faces[1].area,8000);});
test('open wall is not bridged',()=>{const lines=rectangle(0,0,100,80);lines[3]=[[0,80],[0,1]];assert.equal(detectFaces(lines).length,0);});
test('finite intersections create two source bounded areas',()=>{const faces=detectFaces([...rectangle(0,0,100,80),[[50,0],[50,80]]]);assert.equal(faces.length,2);assert.deepEqual(faces.map(f=>f.area),[4000,4000]);});
test('overlapping source edges do not duplicate fill regions',()=>{const lines=rectangle(0,0,100,80);const faces=detectFaces([...lines,[[0,0],[50,0]],[[50,0],[100,0]]]);assert.equal(faces.length,1);assert.equal(faces[0].area,8000);});
test('point inclusion finds the correct source region',()=>{assert(contains([20,20],rectangle(0,0,100,80).map(s=>s[0])));});
