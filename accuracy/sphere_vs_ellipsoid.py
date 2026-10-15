"""Position difference between the spherical destination formula (R = 6371008.8 m) and WGS84 geodesics.

Reproduces the figures in the note's Limitations section at 460 km range:
  about 1.2 km at 35.333 N, about 1.3 km at 45 N, and 2.6 km (0.56 % of range) for a north-south ray at the equator.

Usage:  pip install -r requirements.txt   (GeographicLib)
        python accuracy/sphere_vs_ellipsoid.py
"""
import math

from geographiclib.geodesic import Geodesic

R = 6371008.8


def sphere_destination(lat, lon, az, dist):
    p, l, a, d = math.radians(lat), math.radians(lon), math.radians(az), dist / R
    sp = math.sin(p) * math.cos(d) + math.cos(p) * math.sin(d) * math.cos(a)
    p2 = math.asin(sp)
    l2 = l + math.atan2(math.sin(a) * math.sin(d) * math.cos(p), math.cos(d) - math.sin(p) * sp)
    return math.degrees(p2), math.degrees(l2)


def worst_difference(lat, dist, azimuths):
    worst, at = 0.0, None
    for az in azimuths:
        e = Geodesic.WGS84.Direct(lat, 0.0, az, dist)
        s = sphere_destination(lat, 0.0, az, dist)
        err = Geodesic.WGS84.Inverse(s[0], s[1], e['lat2'], e['lon2'])['s12']
        if err > worst:
            worst, at = err, az
    return worst, at


if __name__ == '__main__':
    dist = 460e3
    azimuths = [0.5 * j for j in range(720)]
    for lat in (0.0, 35.333, 45.0):
        w, az = worst_difference(lat, dist, azimuths)
        print(f"lat {lat:6.3f}: max position difference at 460 km = {w:6.0f} m ({100 * w / dist:.2f} % of range), at azimuth {az} deg")
