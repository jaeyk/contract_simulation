import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {solve,defaults} from './dist/models.js';
const fixtures=JSON.parse(readFileSync(new URL('./fixtures.json',import.meta.url)));
test('Every browser outcome matches the Python reference scenarios',()=>{
  assert.ok(fixtures.length>=250);
  for(const fixture of fixtures){
    const result=solve(fixture.model,fixture.parameters);
    assert.deepEqual(Object.keys(result).sort(),Object.keys(fixture.expected).sort());
    for(const [key,value] of Object.entries(fixture.expected)){
      if(typeof value==='number')assert.ok(Math.abs(result[key]-value)<=1e-9*Math.max(1,Math.abs(value)),`Model ${fixture.model}: ${key} ${result[key]} vs ${value}`);
      else assert.equal(result[key],value,`Model ${fixture.model}: ${key}`);
    }
  }
});
test('Invalid probabilities, nonfinite values, unsupported domains and unknown parameters are rejected',()=>{
  for(const [id,p] of [['1',{m:2}],['1',{cI:100}],['2',{c:0}],['3',{a:NaN}],['4',{f:-1}],['5',{N:2.5}],['6',{f:100}],['7',{rho:2}],['5',{omega:2}],['8',{r:10}],['8',{w:1.5}],['9',{f:20}],['9',{h:0}],['1',{typo:1}]])assert.throws(()=>solve(id,p));
});
test('All nine default scenarios are finite',()=>{
  for(const id of Object.keys(defaults))for(const v of Object.values(solve(id)))if(typeof v==='number')assert.ok(Number.isFinite(v));
});
