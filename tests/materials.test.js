import {test}from 'node:test';import assert from 'node:assert/strict';import fs from 'node:fs';import crypto from 'node:crypto';import {FINISHES}from '../renderer.js';
test('all library photographs match provenance and every finish resolves',()=>{
 assert.equal(Object.keys(FINISHES).length,40);const manifest=JSON.parse(fs.readFileSync('public/assets/library/manifest.json'));assert.equal(manifest.materials.length,10);
 for(const material of manifest.materials)for(const map of Object.values(material.maps)){const bytes=fs.readFileSync('public/assets/library/'+map.file);assert.equal(crypto.createHash('sha256').update(bytes).digest('hex'),map.sha256);assert.match(map.source_url,/^https:\/\/dl\.polyhaven\.org\//);}
 for(const finish of Object.values(FINISHES)){assert(finish.category);if(finish.file)assert(fs.existsSync('public/assets/'+finish.file));if(finish.normal)assert(fs.existsSync('public/assets/'+finish.normal));}
});

test("material controls have unique HTML identifiers",()=>{const html=fs.readFileSync("index.html","utf8"),ids=[...html.matchAll(/id="([^"]+)"/g)].map(m=>m[1]);assert.equal(ids.length,new Set(ids).size);});
