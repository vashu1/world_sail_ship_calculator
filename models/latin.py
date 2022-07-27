import numpy as np
import math
from functools import lru_cache
import scipy.optimize

# ? https://github.com/hrosailing/hrosailing  import hrosailing.polardiagram as pol

# http://davidburchnavigation.blogspot.com/2022/02/VMC.html  The programs Expedition, LuckGrib, qtVlm, and others each have an extensive set of polars included.
KNOTS_TO_MS = 1852 / 3600

# https://jieter.github.io/orc-data/site/#USA/USA13751
data = """twa/tws;6;8;10;12;14;16;20
0;0;0;0;0;0;0;0
52;7.08;8.44;9.33;9.72;9.93;10.06;10.19
60;7.52;8.93;9.7;10.04;10.23;10.34;10.47
75;7.88;9.3;9.96;10.32;10.57;10.72;10.9
90;7.84;9.27;10;10.4;10.71;10.98;11.38
110;7.09;8.62;9.79;10.29;10.55;10.79;11.32
120;6.84;8.46;9.72;10.35;10.76;11.04;11.56
135;6.21;7.76;9.12;10;10.53;10.98;11.99
150;5.22;6.62;7.85;9;9.85;10.39;11.29
180;4.52;5.73;6.8;7.79;8.53;9.0;9.78"""  # a=[5.22,6.62,7.85,9,9.85,10.39,11.29] ; [round(i*0.866,2) for i in a]  # math.cos(30*3.14/180) = 0.866158094405463
data = data.split('\n')[1:]
data = [list(map(float, line.split(';')[1:])) for line in data]


def __ship_speed(wind_index, degrees):
    degrees_lst = [0, 52, 60, 75, 90, 110, 120, 135, 150, 180]
    for i, d in enumerate(degrees_lst):
        if degrees < degrees_lst[i+1]:
            d1, d2 = d, degrees_lst[i+1]
            return KNOTS_TO_MS * np.interp(degrees, [d1, d2], [data[i][wind_index], data[i+1][wind_index]])

#@lru_cache(maxsize=1_000)
def _ship_speed(wind_speed, degrees):  #TODO waves    180 degrees = wind from behind, 0 - against wind
    degrees = abs(degrees)
    degrees = degrees % 360
    if degrees >= 180:
        degrees = 360 - degrees
    if wind_speed >= 20:
        wind_speed = 10  # lower sails!
    speeds = [0, 6, 8, 10, 12, 14, 16, 20]
    for i, s in enumerate(speeds):
        if wind_speed < speeds[i+1]:
            wind_index = i-1
            wind_speed1, wind_speed2 = s, speeds[i+1]
            break
    ship_speed1 = __ship_speed(wind_index, degrees) if wind_speed1 else 0
    ship_speed2 = __ship_speed(wind_index+1, degrees)
    drift = 0
    return drift, np.interp(wind_speed, [wind_speed1, wind_speed2], [ship_speed1, ship_speed2])

def tack_speed(wind_speed, az, az1, az2):
    dr1, sp1 = _ship_speed(wind_speed, az1)
    dr2, sp2 = _ship_speed(wind_speed, az2)
    if sp1 == 0 or sp2 == 0:
        return 0, 0
    c1 = math.cos(math.pi / 180 * (az - az1))
    s1 = math.sin(math.pi / 180 * (az - az1))
    c2 = math.cos(math.pi / 180 * (az - az2))
    s2 = math.sin(math.pi / 180 * (az - az2))
    if s1 * s2 >= 0:
        return 0, 0
    coeff = - sp1 * s1 / (sp2 * s2)
    drift = (dr1 + coeff * dr2) / (1 + coeff)
    tack_speed = (sp1 * c1 + sp2 * c2 * coeff) / (1 + coeff)
    return drift, tack_speed


def ship_speed(wind_speed, degrees, d=80):
    dr0, sp0 = _ship_speed(wind_speed, degrees)
    res = scipy.optimize.minimize(lambda azs: - tack_speed(wind_speed, degrees, azs[0], azs[1])[1],
                                  x0=(degrees - d, degrees + d), method='Nelder-Mead')  #, tol=1e-4
    #print(res)
    #assert res.success
    az1, az2 = res.x
    dr, sp = tack_speed(wind_speed, degrees, az1, az2)
    return (dr0, sp0) if sp0 > sp else (dr, sp)



assert __ship_speed(1, 90) == 9.27 * KNOTS_TO_MS
assert __ship_speed(1, 100) == (9.27+8.62)/2 * KNOTS_TO_MS
assert _ship_speed(8, 90) == (0, 9.27 * KNOTS_TO_MS)

"""
import time
theta = np.arange(0, 2*np.pi, 0.1)
wind_speed = 10
t = time.time()
vals1 = [ship_speed(wind_speed, d/np.pi*180) for d in theta]
print(time.time() - t)
#exit(0)
"""
"""
import numpy as np
import matplotlib.pyplot as plt



wind_speed = 10
theta = np.arange(0, 2*np.pi, 0.1)
vals1 = [0.9*_ship_speed(wind_speed, d/np.pi*180)[1] for d in theta]
fig, ax = plt.subplots(subplot_kw={'projection': 'polar'})
ax.plot(theta, vals1, color='r')
vals2 = [ ship_speed(wind_speed, d/np.pi*180, 20)[1] for d in theta]
ax.plot(theta, vals2, color='b')
vals3 = [ 1.1*ship_speed(wind_speed, d/np.pi*180, 80)[1] for d in theta]
ax.plot(theta, vals3, color='g')
vals4 = [ 1.2*ship_speed(wind_speed, d/np.pi*180, 50)[1] for d in theta]
ax.plot(theta, vals4, color='b')
ax.grid(True)

plt.show()
"""

"""
import numpy as np
import matplotlib.pyplot as plt

wind_speed = 10
theta = np.arange(0, np.pi, 0.01)
vals1 = [_ship_speed(wind_speed, d) for d in theta]
vals2 = [ ship_speed(wind_speed, d) for d in theta]
fig, ax = plt.subplots(subplot_kw={'projection': 'polar'})
ax.plot(theta, vals1, color='r')
ax.plot(theta, vals2, color='b')
ax.grid(True)

plt.show()
"""