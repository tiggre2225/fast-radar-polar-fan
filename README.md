# fast-radar-polar-fan

> **A Note on Fast Georeferencing of Polar Radar Fans with Shared Range Weights**  
> Hoang Bach Nguyen — arXiv:[TODO] — 10.5281/zenodo.23399006

## Quick start

Requires Node.js 18 or newer for the code and tests, and Python 3.9 or newer for the analysis and accuracy scripts.

```sh
npm test                               # 11 tests, a few seconds
pip install -r requirements.txt        # only for the Python scripts
```

```js
import { fanToGlobe, fanToMercator } from './src/index.js';

const m = 720, n = 1832;
const az = Float64Array.from({ length: m }, (_, j) => 0.5 * j);
const globe = new Float32Array(3 * m * n);
fanToGlobe(35.333, -97.278, az, 2125, 250, n, globe);
const merc = new Float32Array(2 * m * n);
fanToMercator(35.333, -97.278, az, 2125, 250, n, merc);
```

For non-uniform gate spacing use `rangeTableDirect` in `src/rangeTable.js`.

## Benchmark

`benchmark/benchmark.html` is a standalone page; open it in a browser (a local file is fine, no server needed).

Keep in mind that in the note, the benchmark is ran on a machine on AC power with no other heavy load.

Do not edit `benchmark.html`. The log records the SHA-256 of the page's script element, and any
change, even a tiny comment, will change the hash. Absolute times depend on the browser, the machine and its
state.

The logs in `benchmark/results/` come from a Dell Precision 7540 (Intel Core i9-9880H, Brave 1.97.56 / Chromium
155.0.8059.40) and a Samsung Galaxy A26 5G (Chrome 154.0.8037.126), both on AC power.

## Data

No radar data are redistributed. The gate geometry in the note comes from the Level II (Archive II) volume
`KTLX20261001_040223_V06` (KTLX, Oklahoma City, volume start 2026-10-01 04:02:23.9 UTC), which is available from the
public NEXRAD Level II archive. The benchmark itself uses synthetic values.

## License

MIT, see `LICENSE`. If you use this work, please cite the note (and the archived release of this repository); see
`CITATION.cff`.
