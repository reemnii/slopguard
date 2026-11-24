export const samples = {
  Python: `import os\nimport requests\nimport requets\nimport numpy\nimport pandass\nfrom bs4 import BeautifulSoup\n\n# Review AI-suggested dependencies before installing\n# Try an unknown package to see an unverified finding\n`,
  JavaScript: `import React from 'react';\nimport axios from 'axios';\nimport express from 'expresss';\nimport 'example-new';\nimport { readFile } from 'node:fs/promises';\n`,
  TypeScript: `import type { ReactNode } from 'react';\nimport axios from 'axios';\nimport 'example-new';\nimport { inspect } from 'lodashh';\n`,
};
const fixtures = {
  requests: {}, numpy: {}, pandas: {}, beautifulsoup4: {}, Pillow: {}, flask: {}, react: {}, axios: {}, express: {}, lodash: {}, next: {}, typescript: {},
  requets: { missing: true, similar: 'requests' }, requestss: { missing: true, similar: 'requests' },
  pandass: { missing: true, similar: 'pandas' }, numpyy: { missing: true, similar: 'numpy' },
  expresss: { missing: true, similar: 'express' }, reactt: { missing: true, similar: 'react' }, lodashh: { missing: true, similar: 'lodash' },
  'example-new': { young: true }, 'ai-helper-kit': { missing: true }, 'quick-ai-utils': { young: true, noRepo: true },
};
const builtins = new Set(['os', 'sys', 'json', 're', 'ast', 'math', 'time', 'datetime', 'pathlib', 'typing', 'collections', 'unittest', 'subprocess', 'asyncio', 'fs', 'path', 'http', 'https', 'crypto', 'util', 'stream', 'events', 'buffer', 'url', 'process']);
const aliases = { bs4: 'beautifulsoup4', PIL: 'Pillow', sklearn: 'scikit-learn', cv2: 'opencv-python', yaml: 'PyYAML' };
export function extractPackages(code, language) {
  const packages = new Set();
  if (language === 'Python') {
    const clean = code.replace(/#[^\n]*/g, '');
    for (const m of clean.matchAll(/^\s*(?:from\s+([\w.]+)\s+import|import\s+([^\n;]+))/gm)) {
      if (m[1] && !m[1].startsWith('.')) packages.add(m[1].split('.')[0]);
      if (m[2]) for (const p of m[2].split(',')) packages.add(p.trim().split(/[.\s]/)[0]);
    }
    for (const m of clean.matchAll(/\bpip3?\s+install\s+([^\n]+)/g)) {
      let skip = false;
      for (const raw of m[1].split(/\s+/)) {
        if (skip) { skip = false; continue; }
        if (['-r','--requirement','-i','--index-url','--extra-index-url','-c','--constraint'].includes(raw)) {skip = true; continue;}
        const name = raw.replace(/^["']|["']$/g, '').split(/[\[=<>!~]/)[0];
        if (/^[a-zA-Z0-9][\w.-]*$/.test(name)) packages.add(name);
      }
    }
  } else {
    const clean = code.replace(/\/\*[\s\S]*?\*\//g, '').replace(/^\s*\/\/.*$/gm, '');
    for (const m of clean.matchAll(/\b(?:from\s*|import\s*\(?\s*|require\s*\(\s*)['"]([^'"]+)['"]/g)) {
      const p = m[1];
      if (p.startsWith('.') || p.startsWith('/') || p.startsWith('#') || (p.includes(':') && !p.startsWith('node:'))) continue;
      packages.add(p.startsWith('@') ? p.split('/').slice(0, 2).join('/') : p.split('/')[0]);
    }
    for (const m of clean.matchAll(/\bnpm\s+(?:install|i)\s+([^\n]+)/g)) {
      let skip = false;
      for (let p of m[1].split(/\s+/)) {
        if (skip) {skip = false; continue;}
        if (['--registry','--prefix','-w','--workspace'].includes(p)) {skip = true; continue;}
        if (['&&',';','|'].includes(p)) break;
        p = p.replace(/^['"]|['"]$/g, '').replace(/(?!^)@[^/]*$/, '');
        if (/^(?:@[\w.-]+\/)?[\w-]+$/.test(p)) packages.add(p);
      }
    }
  }
  return [...packages].filter(p => p && !builtins.has(p.replace('node:', ''))).sort();
}
export function scanDemo(inputs) {
  const found = new Map();
  for (const {code, language} of inputs) for (const name of extractPackages(code, language)) {
    const registry = language === 'Python' ? 'PyPI' : 'npm';
    const key = registry + ':' + name;
    const fixture = fixtures[aliases[name] || name];
    const reasons = [];
    if (!fixture) {
      found.set(key, { name, registry, score: null, level: 'Unverified', reasons: [{ text: 'No demonstration fixture for this package', points: null }], simulated: true });
      continue;
    }
    if (fixture.missing) reasons.push({ text: 'Missing from registry in the demo fixture', points: 60 });
    if (fixture.similar) reasons.push({ text: `Name resembles ${fixture.similar}`, points: 30 });
    if (fixture.young) reasons.push({ text: 'Published less than 30 days ago in the demo fixture', points: 20 });
    if (fixture.noRepo) reasons.push({ text: 'Missing repository metadata in the demo fixture', points: 10 });
    const score = Math.min(100, reasons.reduce((sum, r) => sum + r.points, 0));
    const level = score >= 70 ? 'High' : score >= 40 ? 'Medium' : score >= 20 ? 'Low' : 'Minimal';
    found.set(key, { name, registry, score, level, reasons, similar: fixture.similar, simulated: true });
  }
  return [...found.values()];
}
export const demoReport = scanDemo([{ code: samples.Python + '\npip install ai-helper-kit', language: 'Python' }, {code: samples.JavaScript, language: 'JavaScript'}]);
export const initialHistory = [
  { id: 'SG-1042', name: 'ai-assistant / dependencies', date: '2026-11-24T09:42:00+02:00', results: demoReport, sample: true },
  { id: 'SG-1041', name: 'storefront / api-client.ts', date: '2026-11-23T16:18:00+02:00', results: scanDemo([{code: samples.TypeScript, language: 'TypeScript'}]), sample: true },
  { id: 'SG-1040', name: 'data-pipeline / analytics.py', date: '2026-11-22T11:05:00+02:00', results: scanDemo([{code: 'import requests\nimport numpy\nimport pandas', language: 'Python'}]), sample: true },
];
