import { R } from './constants.js';

export function rangeTable(r0, dr, n) {
  const cStep = Math.cos(dr / R), sStep = Math.sin(dr / R);
  const ct = new Float64Array(n), st = new Float64Array(n);
  ct[0] = Math.cos(r0 / R); st[0] = Math.sin(r0 / R);
  for (let i = 1; i < n; i++) {          // rotation by one gate spacing
    ct[i] = ct[i-1]*cStep - st[i-1]*sStep;
    st[i] = st[i-1]*cStep + ct[i-1]*sStep;
  }
  return { ct, st };
}

export function rangeTableDirect(rangesM) {
  const n = rangesM.length;
  const ct = new Float64Array(n), st = new Float64Array(n);
  for (let i = 0; i < n; i++) { ct[i] = Math.cos(rangesM[i] / R); st[i] = Math.sin(rangesM[i] / R); }
  return { ct, st };
}
