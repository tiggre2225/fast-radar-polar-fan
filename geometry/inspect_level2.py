#!/usr/bin/env python3
"""Print the NEXRAD Level II (Archive II, message type 31) header fields that the note's geometry relies on.

Usage:
    pip install arm_pyart          # brings numpy etc.
    python inspect_level2.py KTLX20261001_040223_V06      # a downloaded Archive II file (.gz/.bz2 ok)
    python inspect_level2.py FILE --json out.json           # also save the numbers

What it reports, per sweep (elevation cut) and per moment (REF, VEL, SW, ZDR, PHI, RHO, CFP):
  * ngates, first_gate, gate_spacing exactly as stored (ICD 2620002 Table XVII-B), and whether they are
    identical in every radial of the sweep;
  * the far edge of the last gate, assuming first_gate is the CENTRE of gate 0 (the ICD wording);
  * the azimuth_resolution code of each radial (ICD 2620002 Table XVII-A, byte 20: 1 = 0.5 deg, 2 = 1.0 deg),
    and the ACTUAL spacing derived from the per-radial azimuth angles (min / median / max, count of outliers).

Units: Py-ART returns first_gate and gate_spacing as stored in the message. In Archive II they are metres,
so for super-resolution reflectivity we expect first_gate = 2125, gate_spacing = 250, ngates = 1832.
This script prints what is actually in your file; it does not assume those values.
"""
import argparse
import json
import sys

import numpy as np

MOMENTS = ("REF", "VEL", "SW", "ZDR", "PHI", "RHO", "CFP")


def _wrap_diff(az):
    """Differences between consecutive azimuths (deg), wrapped to (-180, 180]."""
    d = np.diff(np.asarray(az, dtype=float))
    return (d + 180.0) % 360.0 - 180.0


def summarize_sweep(nex, scan):
    idx = nex.scan_msgs[scan]
    recs = [nex.radial_records[i] for i in idx]
    first_hdr = recs[0]["msg_header"]
    out = {
        "sweep": int(scan),
        "elevation_number": int(first_hdr.get("elevation_number", -1)),
        "elevation_angle_mean": float(np.mean([r["msg_header"]["elevation_angle"] for r in recs])),
        "n_radials": len(recs),
        "moments": {},
    }

    az = np.array([r["msg_header"]["azimuth_angle"] for r in recs], dtype=float)
    codes = sorted({int(r["msg_header"].get("azimuth_resolution", -1)) for r in recs})
    d = _wrap_diff(az)
    if d.size:
        med = float(np.median(d))
        out["azimuth"] = {
            "azimuth_resolution_codes_seen": codes,  # 1 = 0.5 deg, 2 = 1.0 deg (commanded value)
            "actual_spacing_min": float(d.min()),
            "actual_spacing_median": med,
            "actual_spacing_max": float(d.max()),
            "radials_with_spacing_off_median_by_more_than_0.1deg": int(np.sum(np.abs(d - med) > 0.1)),
            "first_azimuths": [round(float(x), 3) for x in az[:6]],
        }
    
    for m in MOMENTS:
        have = [r[m] for r in recs if m in r]
        if not have:
            continue
        geoms = {(int(b["ngates"]), int(b["first_gate"]), int(b["gate_spacing"])) for b in have}
        ng, fg, gs = sorted(geoms)[0]
        out["moments"][m] = {
            "radials_with_moment": len(have),
            "distinct_geometries(ngates,first_gate,gate_spacing)": sorted(geoms),
            "ngates": ng,
            "first_gate_stored": fg,
            "gate_spacing_stored": gs,
            # if first_gate is the centre of gate 0 and units are metres:
            "far_edge_of_last_gate_km": (fg - gs / 2.0 + ng * gs) / 1000.0,
            "far_edge_of_last_gate_nmi": (fg - gs / 2.0 + ng * gs) / 1852.0,
            "centre_of_last_gate_km": (fg + (ng - 1) * gs) / 1000.0,
        }
    return out


def summarize(nex):
    info = {}
    vh = getattr(nex, "volume_header", None)
    if vh:
        info["volume_header"] = {k: (v.decode("ascii", "replace") if isinstance(v, bytes) else v)
                                 for k, v in vh.items()}
    info["n_sweeps"] = int(nex.nscans)
    info["sweeps"] = [summarize_sweep(nex, s) for s in range(nex.nscans)]
    return info


def print_report(info):
    print("=" * 78)
    print("Volume header:", info.get("volume_header"))
    print("Sweeps:", info["n_sweeps"])
    for sw in info["sweeps"]:
        print("-" * 78)
        print(f"Sweep {sw['sweep']}  elevation #{sw['elevation_number']}  "
              f"mean elevation {sw['elevation_angle_mean']:.2f} deg  radials {sw['n_radials']}")
        a = sw.get("azimuth")
        if a:
            print(f"  azimuth_resolution codes seen: {a['azimuth_resolution_codes_seen']} "
                  f"(1 = 0.5 deg, 2 = 1.0 deg; commanded value)")
            print(f"  actual spacing deg: min {a['actual_spacing_min']:.3f}  median {a['actual_spacing_median']:.3f}  "
                  f"max {a['actual_spacing_max']:.3f}  outliers(>0.1 deg off median): "
                  f"{a['radials_with_spacing_off_median_by_more_than_0.1deg']}")
        for m, g in sw["moments"].items():
            uniform = len(g["distinct_geometries(ngates,first_gate,gate_spacing)"]) == 1
            print(f"  {m:3s} ngates={g['ngates']:5d} first_gate={g['first_gate_stored']:6d} "
                  f"gate_spacing={g['gate_spacing_stored']:5d}  same in all radials: {uniform}  "
                  f"far edge {g['far_edge_of_last_gate_km']:.3f} km = {g['far_edge_of_last_gate_nmi']:.2f} nmi")
    print("=" * 78)
    print("Super-resolution reflectivity shows ngates=1832, first_gate=2125, gate_spacing=250 and azimuth codes [1].")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("file")
    ap.add_argument("--json", help="also write the numbers to this file")
    args = ap.parse_args()
    try:
        from pyart.io.nexrad_level2 import NEXRADLevel2File
    except ImportError:
        sys.exit("Py-ART is not installed: pip install arm_pyart")
    nex = NEXRADLevel2File(args.file)
    try:
        if not nex.radial_records or "msg_header" not in nex.radial_records[0]:
            sys.exit("No message-31 radial records found (legacy message type 1 file?).")
        info = summarize(nex)
    finally:
        nex.close()
    print_report(info)
    if args.json:
        with open(args.json, "w") as f:
            json.dump(info, f, indent=1, default=lambda o: o.item() if hasattr(o, "item") else str(o))


if __name__ == "__main__":
    main()
