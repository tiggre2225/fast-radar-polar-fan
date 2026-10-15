import { D2R, INV_2PI } from './constants.js';
import { frame } from './frame.js';
import { rangeTable } from './rangeTable.js';

export function fanToMercator(latDeg, lngDeg, azDeg, r0, dr, n, out) {
  const { p0, nv, ev } = frame(latDeg, lngDeg);
  const { ct, st } = rangeTable(r0, dr, n);
  let k = 0;
  for (let j = 0; j < azDeg.length; j++) {
    const a = azDeg[j] * D2R, ca = Math.cos(a), sa = Math.sin(a);
    const dx = ca*nv[0] + sa*ev[0], dy = ca*nv[1] + sa*ev[1], dz = ca*nv[2] + sa*ev[2];
    for (let i = 0; i < n; i++) {
      const c = ct[i], s = st[i];
      const px = c*p0[0] + s*dx, py = c*p0[1] + s*dy, pz = c*p0[2] + s*dz;
      out[k++] = (Math.atan2(py, px) + Math.PI) * INV_2PI;
      out[k++] = (Math.PI - 0.5*Math.log((1 + pz) / (1 - pz))) * INV_2PI;
    }
  }
}
