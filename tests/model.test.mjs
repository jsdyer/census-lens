import test from 'node:test';
import assert from 'node:assert/strict';
import {match,difference} from '../web/model.mjs';
test('geography and type search',()=>assert.deepEqual(match([['1','Montréal, Ville QC'],['2','Marieville, Ville QC']],'montreal qc'),[['1','Montréal, Ville QC']]));
test('missing values and percentage points',()=>{assert.equal(difference(18.1,42.5),24.4);assert.equal(difference(null,0),null);});
