import test from 'node:test';
import assert from 'node:assert/strict';
import { fanToGlobe, fanToMercator } from '../src/index.js';
import { loadKernels, makeInput, countCalls } from '../test-helpers/benchmarkPage.js';

const m = 25, n = 40, az = Float64Array.from({ length: m }, (_, j) => j * 14.4);

test('globe space: 8 + 2m sin/cos calls in total and nothing per point', () => {
  const c = countCalls(() => fanToGlobe(35.333, -97.278, az, 2125, 250, n, new Float32Array(3 * m * n)));
  assert.deepEqual(c, { sin: 4 + m, cos: 4 + m });
  assert.equal(c.sin + c.cos, 8 + 2 * m);
});

test('Web Mercator adds one atan2 and one log per point (2mn)', () => {
  const c = countCalls(() => fanToMercator(35.333, -97.278, az, 2125, 250, n, new Float32Array(2 * m * n)));
  assert.deepEqual(c, { sin: 4 + m, cos: 4 + m, atan2: m * n, log: m * n });
});

test('benchmark page: legacy 15, optimized 4, vector 2 calls per point (both outputs)', () => {
  const k = loadKernels();
  const mm = 10, nn = 20, pts = (mm + 1) * nn;           // the page's grids have m + 1 radials
  const input = makeInput(mm, nn);
  const legacy = countCalls(() => k.kernel_Legacy(input));
  assert.deepEqual(legacy, { sin: 6 * pts, cos: 5 * pts, tan: pts, asin: pts, atan2: pts, log: pts });
  assert.equal(Object.values(legacy).reduce((a, b) => a + b, 0), 15 * pts);
  const opt = countCalls(() => k.kernel_Optimized(input));
  // per point: atan2, log, sin and cos of the new longitude; plus sin/cos once for the radar latitude,
  // once per radial and once per gate (sqrt is not counted)
  assert.deepEqual(opt, { sin: pts + 1 + (mm + 1) + nn, cos: pts + 1 + (mm + 1) + nn, atan2: pts, log: pts, sqrt: pts });
  const vec = countCalls(() => k.kernel_Vector(input));
  assert.deepEqual(vec, { sin: 4 + (mm + 1), cos: 4 + (mm + 1), atan2: pts, log: pts });   // 8 + 2(m+1) sin/cos, 2 per point
});
