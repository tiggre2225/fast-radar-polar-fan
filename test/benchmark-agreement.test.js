import test from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { fanToGlobe, fanToMercator } from '../src/index.js';
import { loadKernels, makeInput, scriptSha256 } from '../test-helpers/benchmarkPage.js';

const m = 720, n = 1832;

test('script hash of benchmark.html matches benchmark/SHA256.txt and both logs', () => {
  const expected = readFileSync(new URL('../benchmark/SHA256.txt', import.meta.url), 'utf8').split(/\s+/)[0];
  assert.equal(scriptSha256(), expected);
  for (const f of ['desktop.txt', 'mobile.txt']) {
    const log = readFileSync(new URL(`../benchmark/results/${f}`, import.meta.url), 'utf8');
    assert.ok(log.includes(`Page script SHA-256: ${expected}`), `${f} records a different hash`);
  }
});

test('src/ reproduces the vector variant exactly, and Mercator matches the other two variants bit for bit', () => {
  const k = loadKernels();
  const input = makeInput(m, n);
  const az = Array.from(input.azimuths);
  const g = new Float32Array(3 * az.length * n), mm = new Float32Array(2 * az.length * n);
  fanToGlobe(35.333, -97.278, az, 2125, 250, n, g);
  fanToMercator(35.333, -97.278, az, 2125, 250, n, mm);
  const vec = k.kernel_Vector(input), opt = k.kernel_Optimized(input), leg = k.kernel_Legacy(input);
  const maxDiff = (a, b) => { let d = 0; for (let i = 0; i < a.length; i++) d = Math.max(d, Math.abs(a[i] - b[i])); return d; };
  assert.equal(maxDiff(g, vec.ecefXYZ), 0);
  assert.equal(maxDiff(mm, vec.mercXY), 0);
  assert.equal(maxDiff(mm, opt.mercXY), 0);
  assert.equal(maxDiff(mm, leg.mercXY), 0);
  assert.equal(maxDiff(leg.ecefXYZ, opt.ecefXYZ), 0);
  assert.ok(maxDiff(g, leg.ecefXYZ) < 2.5e-4);          // 1.22e-4 = one Float32 ulp at |value| in [1024, 2048)
});
