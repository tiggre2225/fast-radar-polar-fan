import { D2R } from './constants.js';

export function frame(latDeg, lngDeg) {
  const phi = latDeg * D2R, lam = lngDeg * D2R;
  const sp = Math.sin(phi), cp = Math.cos(phi), sl = Math.sin(lam), cl = Math.cos(lam);
  return { p0: [cp*cl, cp*sl, sp], nv: [-sp*cl, -sp*sl, cp], ev: [-sl, cl, 0] };
}
