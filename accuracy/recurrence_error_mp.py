import math, mpmath as mp
mp.mp.dps = 60
R = mp.mpf('6371008.8'); n = 1832; dr = mp.mpf(250); r0 = mp.mpf(2125)
cS = math.cos(250/6371008.8); sS = math.sin(250/6371008.8)
c = math.cos(2125/6371008.8); s = math.sin(2125/6371008.8)
rec = comp = direct = 0
for i in range(n):
    ce, se = mp.cos((r0 + i*dr)/R), mp.sin((r0 + i*dr)/R)
    rec = max(rec, mp.sqrt((c-ce)**2 + (s-se)**2)); comp = max(comp, abs(c-ce), abs(s-se))
    d = (2125 + i*250)/6371008.8
    direct = max(direct, mp.sqrt((math.cos(d)-ce)**2 + (math.sin(d)-se)**2))
    c, s = c*cS - s*sS, s*cS + c*sS
print('recurrence vs 60-digit reference, Euclidean:', mp.nstr(rec, 4), ' componentwise:', mp.nstr(comp, 4))
print('direct double evaluation vs reference, Euclidean:', mp.nstr(direct, 4))
