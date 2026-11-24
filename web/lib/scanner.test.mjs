import test from 'node:test';
import assert from 'node:assert/strict';
import {extractPackages, scanDemo} from './scanner.mjs';
test('filters local imports and builtins', () => assert.deepEqual(extractPackages('import "./file"; import "node:fs/promises"; import "react";', 'JavaScript'), ['react']));
test('handles Python aliases and multiple imports', () => assert.deepEqual(extractPackages('import os, requests\nfrom .local import x\nfrom bs4 import BeautifulSoup', 'Python'), ['bs4', 'requests']));
test('unknown names remain unverified', () => { const r = scanDemo([{code:'import no_fixture_package', language:'Python'}])[0]; assert.equal(r.score, null); assert.equal(r.level, 'Unverified'); });
test('typos receive explainable score', () => {const r = scanDemo([{code:'import requets', language:'Python'}])[0]; assert.equal(r.score, 90); assert.equal(r.level, 'High'); assert.equal(r.reasons.reduce((n,r)=>n+r.points,0),90);});
test('deduplicates within ecosystem', () => assert.equal(scanDemo([{code:'import requests',language:'Python'},{code:'import requests',language:'Python'}]).length,1));
test('npm scoped versions and options', () => assert.deepEqual(extractPackages('npm i --registry https://example.org @scope/pkg@2 react@19', 'JavaScript'), ['@scope/pkg','react']));
