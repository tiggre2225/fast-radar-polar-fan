"""Summary statistics for the two benchmark logs (note, Section 6 and Appendix C).

Usage: python benchmark/analysis/analyze.py [RESULTS_DIR]     (default: benchmark/results)
Each log must contain the JSON line of raw samples that the page prints at the end.
"""
import json, random, statistics as st, sys
from pathlib import Path

random.seed(1)
KEYS = ['Legacy', 'Optimized', 'Vector']


def load(path):
    line = [l for l in Path(path).read_text(encoding='utf-8').splitlines() if l.startswith('{"label"')][0]
    return json.loads(line)


def boot_ratio(base, x, B=4000):
    n = len(base); out = []
    for _ in range(B):
        idx = [random.randrange(n) for _ in range(n)]
        out.append(st.median([base[i] for i in idx]) / st.median([x[i] for i in idx]))
    out.sort()
    return out[int(.025 * B)], out[int(.975 * B)]


def main(results):
    for name in ('desktop', 'mobile'):
        d = load(Path(results) / f'{name}.txt'); r = d['raw']; n = d['meas']
        print('=====', name, d['label'], 'n =', n, d['scriptSha256'][:12])
        for k in KEYS:
            for ph in ('e2e', 'kernel'):
                x = r[k][ph]; assert len(x) == n
                print(f'{k:10s}{ph:7s} median {st.median(x):8.2f} mean {st.mean(x):8.2f} sd {st.stdev(x):6.2f} '
                      f'min {min(x):8.2f} max {max(x):8.2f}')
        a = r['assembly']
        print('assembly   median', round(st.median(a), 2), 'mean', round(st.mean(a), 2), 'sd', round(st.stdev(a), 2))
        for ph in ('e2e', 'kernel'):
            for base, x in (('Legacy', 'Optimized'), ('Legacy', 'Vector'), ('Optimized', 'Vector')):
                b, y = r[base][ph], r[x][ph]
                lo, hi = boot_ratio(b, y)
                print(f'  {ph:6s} {x:9s} vs {base:9s}: ratio of medians {st.median(b) / st.median(y):.2f} [{lo:.2f}, {hi:.2f}]'
                      f'   ratio of means {st.mean(b) / st.mean(y):.2f}')
        for k in KEYS:
            e, kk, aa = st.median(r[k]['e2e']), st.median(r[k]['kernel']), st.median(a)
            print(f'  {k}: e2e {e:.1f}  kernel+assembly {kk + aa:.1f}  excess {e - kk - aa:+.1f} ms  assembly share of e2e {100 * aa / e:.0f}%')
        w = d['warm']
        print('  median by position within the round (first, second, third):')
        for ph in ('e2e', 'kernel'):
            for ki, k in enumerate(KEYS):
                by = {0: [], 1: [], 2: []}
                for m_, v in enumerate(r[k][ph]):
                    by[(ki - (w + m_)) % 3].append(v)
                print(f'    {ph:6s} {k:9s}', '  '.join(f'{st.median(by[p]):7.1f}' for p in range(3)))


if __name__ == '__main__':
    here = Path(__file__).resolve().parent
    main(sys.argv[1] if len(sys.argv) > 1 else here.parent / 'results')
