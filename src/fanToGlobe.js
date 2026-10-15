import { D2R, RG } from './constants.js';
import { frame } from './frame.js';
import { rangeTable } from './rangeTable.js';

export function fanToGlobe(latDeg, lngDeg, azDeg, r0, dr, n, out) {
  const { p0, nv, ev } = frame(latDeg, lngDeg);
  const g = v => [RG*v[1], -RG*v[2], RG*v[0]];
  const P = g(p0), N = g(nv), E = g(ev);
  const { ct, st } = rangeTable(r0, dr, n);
  let k = 0;
  for (let j = 0; j < azDeg.length; j++) {
    const a = azDeg[j] * D2R, ca = Math.cos(a), sa = Math.sin(a);
    const dx = ca*N[0] + sa*E[0], dy = ca*N[1] + sa*E[1], dz = ca*N[2] + sa*E[2];
    for (let i = 0; i < n; i++) {
      out[k++] = ct[i]*P[0] + st[i]*dx;
      out[k++] = ct[i]*P[1] + st[i]*dy;
      out[k++] = ct[i]*P[2] + st[i]*dz;
    }
  }
}
