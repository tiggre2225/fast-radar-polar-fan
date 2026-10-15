"""Write the LaTeX table rows used in the note (Table 2, Table 3 of Appendix C, and the position table).

Usage: python benchmark/analysis/make_tables.py [RESULTS_DIR] [OUT_DIR]
       defaults: benchmark/results and the current directory.  Output: main_rows.tex, app_rows.tex, pos_rows.tex
"""
import json, random, statistics as st, sys
from pathlib import Path

random.seed(7)
DEVICES = {'Desktop': 'desktop.txt', 'Mobile': 'mobile.txt'}
LONG = {'Legacy': 'Legacy per-vertex', 'Optimized': 'Optimized destination formula', 'Vector': 'This method'}
SHORT = {'Legacy': 'Legacy', 'Optimized': 'Optimized', 'Vector': 'This method'}
KEYS = ['Legacy', 'Optimized', 'Vector']
med = st.median


def load(path):
    line = [l for l in Path(path).read_text(encoding='utf-8').splitlines() if l.startswith('{"label"')][0]
    return json.loads(line)


def q(x, p):
    s = sorted(x); n = len(s); t = (n - 1) * p; lo = int(t // 1); hi = min(lo + 1, n - 1)
    return s[lo] + (s[hi] - s[lo]) * (t - lo)


def boot(b, x, B=4000):
    n = len(b); out = []
    for _ in range(B):
        i = [random.randrange(n) for _ in range(n)]
        out.append(med([b[k] for k in i]) / med([x[k] for k in i]))
    out.sort()
    return out[int(.025 * B)], out[int(.975 * B)]


def main(results, outdir):
    D = {dev: load(Path(results) / f) for dev, f in DEVICES.items()}
    outdir = Path(outdir)

    def cell(d, k, ph):
        r = d['raw']; m = med(r[k][ph]); s = med(r['Legacy'][ph]) / m
        return f'{m:.1f}' + ('' if k == 'Legacy' else f' ({s:.2f}$\\times$)')

    main_rows = []
    for k in KEYS:
        row = [LONG[k]]
        for dev in D:
            row += [cell(D[dev], k, 'e2e'), cell(D[dev], k, 'kernel')]
        main_rows.append(' & '.join(row) + r' \\')
    asm = ['Quad assembly only'] + ['\\multicolumn{2}{c}{%.1f}' % med(D[dev]['raw']['assembly']) for dev in D]
    main_rows += [r'\midrule', ' & '.join(asm) + r' \\']
    (outdir / 'main_rows.tex').write_text('\n'.join(main_rows))

    rows = []
    for dev, d in D.items():
        r = d['raw']
        rows.append(r'\midrule' if rows else '')
        rows.append(r'\multicolumn{8}{l}{\emph{%s}} \\' % dev)
        for ph, lab in (('e2e', 'End-to-end'), ('kernel', 'Kernel only')):
            for k in KEYS:
                x = r[k][ph]
                if k == 'Legacy':
                    sp, so = '1', '---'
                else:
                    lo, hi = boot(r['Legacy'][ph], x)
                    sp = f"{med(r['Legacy'][ph]) / med(x):.2f} [{lo:.2f}, {hi:.2f}]"
                    if k == 'Optimized':
                        so = '1'
                    else:
                        lo, hi = boot(r['Optimized'][ph], x)
                        so = f"{med(r['Optimized'][ph]) / med(x):.2f} [{lo:.2f}, {hi:.2f}]"
                rows.append(f"{lab} & {SHORT[k]} & {med(x):.1f} & ${st.mean(x):.1f}\\pm{st.stdev(x):.1f}$ & "
                            f"{q(x, .25):.1f}--{q(x, .75):.1f} & {min(x):.1f}--{max(x):.1f} & {sp} & {so} \\\\")
        a = r['assembly']
        rows.append(f"Assembly only & --- & {med(a):.1f} & ${st.mean(a):.1f}\\pm{st.stdev(a):.1f}$ & "
                    f"{q(a, .25):.1f}--{q(a, .75):.1f} & {min(a):.1f}--{max(a):.1f} & --- & --- \\\\")
    (outdir / 'app_rows.tex').write_text('\n'.join(x for x in rows if x))

    pos = []
    for dev, d in D.items():
        r = d['raw']; w = d['warm']
        for ph, lab in (('e2e', 'End-to-end'), ('kernel', 'Kernel')):
            for ki, k in enumerate(KEYS):
                by = {0: [], 1: [], 2: []}
                for m_, v in enumerate(r[k][ph]):
                    by[(ki - (w + m_)) % 3].append(v)
                pos.append(f'{dev} & {lab} & {SHORT[k]} & ' + ' & '.join(f'{med(by[p]):.1f}' for p in range(3)) + r' \\')
    (outdir / 'pos_rows.tex').write_text('\n'.join(pos))
    print('wrote main_rows.tex, app_rows.tex, pos_rows.tex to', outdir)


if __name__ == '__main__':
    here = Path(__file__).resolve().parent
    main(sys.argv[1] if len(sys.argv) > 1 else here.parent / 'results', sys.argv[2] if len(sys.argv) > 2 else '.')
