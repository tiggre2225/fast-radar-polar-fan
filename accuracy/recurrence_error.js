const D2R = Math.PI / 180, R = 6371008.8;
const m = 720, n = 1832, dr = 250, r0 = 2125;
const sites = [[35.33, -97.28], [64.51, -165.30], [13.46, 144.81], [-12.0, 179.9], [47.0, 8.0]];

function dest(phi0, lam0, alpha, delta) {
  const sp = Math.sin(phi0), cp = Math.cos(phi0);
  const sphi2 = sp * Math.cos(delta) + cp * Math.sin(delta) * Math.cos(alpha);
  const phi2 = Math.asin(sphi2);
  const lam2 = lam0 + Math.atan2(Math.sin(alpha) * Math.sin(delta) * cp,
                                 Math.cos(delta) - sp * sphi2);
  return [Math.cos(phi2) * Math.cos(lam2), Math.cos(phi2) * Math.sin(lam2), sphi2];
}

for (const [lat, lng] of sites) {
  const phi0 = lat * D2R, lam0 = lng * D2R;
  const sp = Math.sin(phi0), cp = Math.cos(phi0), sl = Math.sin(lam0), cl = Math.cos(lam0);
  const p0 = [cp * cl, cp * sl, sp], nv = [-sp * cl, -sp * sl, cp], ev = [-sl, cl, 0];
  const cS = Math.cos(dr / R), sS = Math.sin(dr / R);
  let maxRecVsDirect = 0, maxVsStd = 0, maxNormDev = 0, maxAngle = 0;
  for (let j = 0; j < m; j++) {
    const a = (j * 0.5 + 0.25) * D2R, ca = Math.cos(a), sa = Math.sin(a);
    const d = [ca * nv[0] + sa * ev[0], ca * nv[1] + sa * ev[1], ca * nv[2] + sa * ev[2]];
    let c = Math.cos(r0 / R), s = Math.sin(r0 / R);
    for (let i = 0; i < n; i++) {
      const delta = (r0 + i * dr) / R;
      const cd = Math.cos(delta), sd = Math.sin(delta);
      // state error (angle-equivalent) and norm drift
      maxAngle = Math.max(maxAngle, Math.abs(c - cd), Math.abs(s - sd));
      maxNormDev = Math.max(maxNormDev, Math.abs(Math.hypot(c, s) - 1));
      const px = c * p0[0] + s * d[0], py = c * p0[1] + s * d[1], pz = c * p0[2] + s * d[2];
      const qx = cd * p0[0] + sd * d[0], qy = cd * p0[1] + sd * d[1], qz = cd * p0[2] + sd * d[2];
      maxRecVsDirect = Math.max(maxRecVsDirect, Math.hypot(px - qx, py - qy, pz - qz));
      const [ux, uy, uz] = dest(phi0, lam0, a, delta);
      maxVsStd = Math.max(maxVsStd, Math.hypot(px - ux, py - uy, pz - uz));
      const cn = c * cS - s * sS; s = s * cS + c * sS; c = cn;
    }
  }
  console.log(`site (${lat}, ${lng}): max|state err|=${maxAngle.toExponential(2)}  ` +
    `max norm dev=${maxNormDev.toExponential(2)}  ` +
    `rec-vs-direct=${maxRecVsDirect.toExponential(2)} rad (${(maxRecVsDirect * R * 1e6).toFixed(2)} um)  ` +
    `rec-vs-std=${maxVsStd.toExponential(2)} rad (${(maxVsStd * R * 1e6).toFixed(2)} um)`);
}
