"""
add start date argument

coords in 0.5 degrees!

half of Antarctida
how to pass Gibraltar and Malacca?

you might also consider using cartopy instead of basemap. basemap has been more or less completely superseded by cartopy?

"""


from matplotlib.backend_bases import MouseButton
from mpl_toolkits.basemap import Basemap
import matplotlib.pyplot as plt
import numpy as np
import matplotlib.colors as mcolors
from datetime import datetime, timedelta
import pyproj
import math

# 'merc' - Mercator Very large distortion at high latitudes, cannot fully reach the polar regions.
# 'cyl' Equidistant just displays the world in latitude/longitude coordinates.
# 'mill' Miller  mercator projection that avoids the polar singularity
# projection='aeqd' Azimuthal  The shortest route from the center of the map to any other point is a straight line in the azimuthal equidistant projection.
# projection='moll' Mollweide  global, elliptical, equal-area projection.    also 'hammer'
# 'robin'  Robinson  once used by the National Geographic Society for world maps
# 'vandg' van der Grinten Projection - shows the world in a circle centered on the equator.
# 'sinu' length of each parallel is equal to the cosine of the latitude.



#fig, ax = plt.subplots()
"""
plt.figure(figsize=(15, 10))#, dpi=80)
m = Basemap(projection='cyl', resolution='l')
m.drawcoastlines()
#m.bluemarble()
ax = plt.gca()
ax.set_ylim(-70, 75)

path = []
prev = None
path_colors = list(mcolors.BASE_COLORS.values())
def on_click(event):
    global prev, path_indx, path_colors
    if event.button is MouseButton.LEFT:
        lat, lon = event.ydata, event.xdata
        x, y = m(lon, lat)
        print(x, y)
        path.append((x, y))
        if prev:
            print('plot')
            #m.plot([prev[0], x], [prev[1], y], 'o-', markersize=3, linewidth=1, color=path_colors[path_indx])
            m.drawgreatcircle(prev[0], prev[1], x, y, color='r')
        ax.annotate(str(len(path)), (x,y), xytext=(5, 5), textcoords='offset points')
        plt.draw()
        prev = x, y
    elif event.button is MouseButton.RIGHT:
        prev = None
        _ = path.pop()

plt.connect('button_press_event', on_click)

plt.show()
"""
#print(f'{path=}')
#TODO undo
path = [(-11.612903225806463, 48.14516129032256), (-30.80645161290323, 34.112903225806434), (-47.741935483870975, 34.758064516129025)]

import dbs  # dbs.current dbs.wind(dt, lon, lat)
from models.latin import ship_speed  # ship_speed(wind_speed, degrees)

DT_STEP = timedelta(minutes = 30)  # timedelta(hours = 1)

# wind - 95-97, 2000, 2004-5    current 96-05
cur_dt = datetime(year=1996, month=5, day=30, hour=12)
cur_lon, cur_lat = path[0]

def vector_len(x, y):
    return (x**2 + y**2) ** 0.5


def vector_degree(x, y):
    v_len = vector_len(x, y)
    if v_len < 1e-6:
        return 0
    cosd = y / v_len  # u = (0, 1/v_len)
    d = math.acos(cosd) / math.pi * 180
    return d if x > 0 else 360 - d


assert abs(vector_degree(1,1) - 45) < 1e-6
assert abs(vector_degree(0,1) - 360) < 1e-6
assert abs(vector_degree(1,0) - 90) < 1e-6
assert abs(vector_degree(0,-1) - 180) < 1e-6
assert abs(vector_degree(-1,0) - 270) < 1e-6


def run_path(cur_dt, cur_lon, cur_lat, next_lon, next_lat):
    geodesic = pyproj.Geod(ellps='WGS84')
    while True:
        fwd_azimuth, _, distance = geodesic.inv(cur_lon, cur_lat, next_lon, next_lat)
        current_u, current_v = dbs.current(cur_dt, cur_lon, cur_lat)
        if not current_u or not current_v:
            current_u, current_v = 0, 0
        wind_u, wind_v = dbs.wind(cur_dt, cur_lon, cur_lat)
        if not wind_u or not wind_v:
            print(f'Ran aground {cur_lon=} {cur_lat=} !!!')
            exit(1)
        wind_u -= current_u  # true wind
        wind_v -= current_v
        #
        wind_azimuth = vector_degree(wind_u, wind_v)
        ship_azimuth = fwd_azimuth - wind_azimuth + 180  #TODO test
        drift_speed, sail_speed = ship_speed(vector_len(wind_u, wind_v), ship_azimuth)  #TODO correct for current
        sail_distance = sail_speed * DT_STEP.seconds
        if sail_distance > distance:
            cur_dt += DT_STEP * (distance / sail_distance)
            return cur_dt
        cur_lon, cur_lat, _ = geodesic.fwd(cur_lon, cur_lat, fwd_azimuth, sail_distance)  # sail
        drift_distance = drift_speed * DT_STEP.seconds
        cur_lon, cur_lat, _ = geodesic.fwd(cur_lon, cur_lat, vector_degree(wind_u, wind_v), drift_distance)  # wind drift
        current_distance = vector_len(current_u, current_v) * DT_STEP.seconds
        cur_lon, cur_lat, _ = geodesic.fwd(cur_lon, cur_lat, vector_degree(current_u, current_v), current_distance)  # current
        cur_dt += DT_STEP



for next_lon, next_lat in path[1:]:
    print('step', cur_dt)
    cur_dt = run_path(cur_dt, cur_lon, cur_lat, next_lon, next_lat)


print('END', cur_dt)