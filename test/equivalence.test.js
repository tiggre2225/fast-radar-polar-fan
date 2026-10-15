import test from 'node:test';
import assert from 'node:assert/strict';
import { D2R, R, RG, fanToGlobe, fanToMercator, rangeTable, rangeTableDirect } from '../src/index.js';

const SITES = [[35.33, -97.28], [64.51, -165.30], [13.46, 144.81], [-12.0, 179.9], [47.0, 8.0]];
const m = 720, n = 1832, r0 = 2125, dr = 250;
const az = Float64Array.from({ length: m }, (_, j) => j * 0.5 + 0.25);

function destination(latDeg, lngDeg, azDeg, distM) {          // standard formula, double precision
  const phi0 = latDeg * D2R, lam0 = lngDeg * D2R, a = azDeg * D2R, d = distM / R;
  const sp = Math.sin(phi0), cp = Math.cos(phi0);
  const sphi2 = sp * Math.cos(d) + cp * Math.sin(d) * Math.cos(a);
  const phi2 = Math.asin(sphi2);
  const lam2 = lam0 + Math.atan2(Math.sin(a) * Math.sin(d) * cp, Math.cos(d) - sp * sphi2);
  return [phi2, lam2];
}

for (const [lat, lng] of SITES) {
  test(`globe and Mercator agree with the destination formula at (${lat}, ${lng})`, () => {
    const g = new Float32Array(3 * m * n), mm = new Float32Array(2 * m * n);
    fanToGlobe(lat, lng, az, r0, dr, n, g);
    fanToMercator(lat, lng, az, r0, dr, n, mm);
    let maxGlobe = 0, maxX = 0, maxY = 0;
    for (let j = 0; j < m; j++) for (let i = 0; i < n; i++) {
      const [phi, lam] = destination(lat, lng, az[j], r0 + i * dr);
      const k = j * n + i;
      const ref = [RG * Math.cos(phi) * Math.sin(lam), -RG * Math.sin(phi), RG * Math.cos(phi) * Math.cos(lam)];
      for (let c = 0; c < 3; c++) maxGlobe = Math.max(maxGlobe, Math.abs(g[3 * k + c] - ref[c]));
      let x = ((lam + Math.PI) % (2 * Math.PI) + 2 * Math.PI) % (2 * Math.PI) / (2 * Math.PI);   // wrap into [0, 1)
      const dx = Math.abs(mm[2 * k] - x);
      maxX = Math.max(maxX, Math.min(dx, 1 - dx));                                               // across the antimeridian
      const y = (Math.PI - Math.log(Math.tan(Math.PI / 4 + phi / 2))) / (2 * Math.PI);
      maxY = Math.max(maxY, Math.abs(mm[2 * k + 1] - y));
    }
    assert.ok(maxGlobe < 2.5e-4, `globe max |diff| ${maxGlobe}`);   // one Float32 ulp at |value| in [1024, 2048) is 1.22e-4
    assert.ok(maxX < 5e-7, `Mercator x max |diff| ${maxX}`);
    assert.ok(maxY < 5e-7, `Mercator y max |diff| ${maxY}`);
  });
}

test('the rotation-recurrence table matches direct evaluation to 1e-13 (Euclidean)', () => {
  const a = rangeTable(r0, dr, n);
  const b = rangeTableDirect(Array.from({ length: n }, (_, i) => r0 + i * dr));
  let worst = 0;
  for (let i = 0; i < n; i++) worst = Math.max(worst, Math.hypot(a.ct[i] - b.ct[i], a.st[i] - b.st[i]));
  assert.ok(worst < 1e-13, `max deviation ${worst}`);
});
