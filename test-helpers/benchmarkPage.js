import { readFileSync } from 'node:fs';
import { createHash } from 'node:crypto';
import { fileURLToPath } from 'node:url';
import { dirname, join } from 'node:path';

const here = dirname(fileURLToPath(import.meta.url));
export const PAGE = join(here, '..', 'benchmark', 'benchmark.html');

export function scriptText() {
  const html = readFileSync(PAGE, 'utf8');
  return html.split('<script id="bench-script">')[1].split('</script>')[0];
}

export function scriptSha256() {
  return createHash('sha256').update(scriptText(), 'utf8').digest('hex');
}

export function loadKernels() {
  const text = scriptText();
  const cut = text.slice(0, text.indexOf('function stats'));
  return new Function('performance', cut + 'return {kernel_Legacy, kernel_Optimized, kernel_Vector};')(performance);
}

export function makeInput(m, n, latDeg = 35.333, lngDeg = -97.278, firstKm = 2.125, stepKm = 0.25) {
  const azimuths = Float64Array.from({ length: m + 1 }, (_, j) => j * 360 / m);   // m+1 radials, closing the fan
  const data = []; for (let j = 0; j < m; j++) data.push(new Array(n).fill(1));
  return { azimuths, ranges: { numRanges: n, step: stepKm, firstRange: firstKm }, data, radarLat: latDeg, radarLng: lngDeg };
}

const NAMES = ['sin', 'cos', 'tan', 'asin', 'acos', 'atan', 'atan2', 'log', 'sqrt', 'atanh'];
export function countCalls(fn) {
  const orig = {}, counts = {};
  for (const f of NAMES) { orig[f] = Math[f]; counts[f] = 0; Math[f] = (...a) => { counts[f]++; return orig[f](...a); }; }
  try { fn(); } finally { for (const f of NAMES) Math[f] = orig[f]; }
  return Object.fromEntries(Object.entries(counts).filter(([, v]) => v));
}
