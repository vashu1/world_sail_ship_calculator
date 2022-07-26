from matplotlib.backend_bases import MouseButton
from mpl_toolkits.basemap import Basemap
import matplotlib.pyplot as plt
import numpy as np
import matplotlib.colors as mcolors
import random
from matplotlib.patches import Arrow
from collections import Counter, defaultdict

fig, ax = plt.subplots()
# 'merc' - Mercator Very large distortion at high latitudes, cannot fully reach the polar regions.
# 'cyl' Equidistant just displays the world in latitude/longitude coordinates.
# 'mill' Miller  mercator projection that avoids the polar singularity
# projection='aeqd' Azimuthal  The shortest route from the center of the map to any other point is a straight line in the azimuthal equidistant projection.
# projection='moll' Mollweide  global, elliptical, equal-area projection.    also 'hammer'
# 'robin'  Robinson  once used by the National Geographic Society for world maps
# 'vandg' van der Grinten Projection - shows the world in a circle centered on the equator.
# 'sinu' length of each parallel is equal to the cosine of the latitude.
m = Basemap(projection='cyl', resolution='l')
m.drawcoastlines()
m.drawmapboundary(fill_color='aqua')
_ = m.fillcontinents(color='coral',lake_color='aqua')
m.drawcountries()
m.drawparallels(np.arange(-90.,120.,10.))
m.drawmeridians(np.arange(0.,420.,20.))
m.drawmapboundary(fill_color='aqua')

# =====

import os
import netCDF4

def read_netcdf(filename):
    file = netCDF4.Dataset(filename)
    data = file.variables[:]   # ['data'][:]  # keys ['time', 'zlev', 'lat', 'lon', 'u', 'v']
    file.close()

folder = 'www.ncei.noaa.gov/data/blended-global-sea-surface-wind-products/access/winds/6-hourly/'
file = netCDF4.Dataset(folder + '1995/uv19950115.nc')

wind_files = {}
for root, subdirs, files in os.walk('www.ncei.noaa.gov'):  #'./Blended_Sea_Winds_dataset_6hourly'):
    for file in files:
        if file.endswith('.nc'):
            #print(root, subdirs, file)
            wind_files[file] = root + '/' + file

fn = wind_files['uv20051227.nc']
file = netCDF4.Dataset(fn)

"""
file.dimensions
    zlev1 10.
    time4 [245328 245334 245340 245346]
    lat719  -89.75  89.75
    lon1440 0 359.75

print(file.variables['v'])   current shape = (4, 1, 719, 1440)
"""
fn_wind = None
file_wind = None
def wind(fn, lon, lat, t = 0):
    #print(lon, lat)
    if fn != fn_wind:
        file_wind = netCDF4.Dataset(wind_files[fn])
    lon += 360
    lon %=360
    lat += 90
    lon= int(lon * 4)
    lat = int(lat * 4)
    if not file_wind.variables['u'][t][0][lat][lon] or not file_wind.variables['v'][t][0][lat][lon]:
        return None, None
    return file_wind.variables['u'][t][0][lat][lon], file_wind.variables['v'][t][0][lat][lon]


# =====


STEP = 10
winds_u = defaultdict(Counter)
winds_v = defaultdict(Counter)
#for t in range(4):

c = 0
for fn in list(wind_files.keys())[5::100]:
    print(c)
    c += 1
    t = int(random.random()*4)
    for lat in range(-90 + STEP, 90, STEP):
        for lon in range(-180+STEP, 180, STEP):
            x, y = m(lon, lat)
            dx, dy = wind(fn, lon, lat, t)
            if not dx or not dy:
                continue
            winds_u[lon][lat] += dx
            winds_v[lon][lat] += dy

plt.figure(figsize=(15, 10))#, dpi=80)
fig, ax = plt.subplots()
m = Basemap(projection='cyl', resolution='l')
m.drawcoastlines()
#m.bluemarble()
ax = plt.gca()
ax.set_ylim(-70, 75)

# normalise
mx1 = max([max([abs(winds_u[lon][lat]) for lat in winds_u[lon]]) for lon in winds_u])
mx2 = max([max([abs(winds_u[lon][lat]) for lat in winds_u[lon]]) for lon in winds_u])
mx = max(mx1, mx2)
MAX_VECTOR = 30

for lat in range(-90 + STEP, 90, STEP):
    for lon in range(-180 + STEP, 180, STEP):
        x, y = m(lon, lat)
        dx = winds_u[lon][lat] * MAX_VECTOR / mx
        dy = winds_v[lon][lat] * MAX_VECTOR / mx
        if not dx or not dy:
            continue
        arrow = Arrow(x, y, dx, dy, width=5.0, color="red")  # https://matplotlib.org/stable/api/_as_gen/matplotlib.patches.Arrow.html
        ax.add_patch(arrow)

plt.show()

####  CURRENTs

folder = 'oscar/'
current_files = {}
for root, subdirs, files in os.walk(folder):  #'./Blended_Sea_Winds_dataset_6hourly'):
    for file in files:
        if file.endswith('.nc'):
            current_files[file] = root + '/' + file

fn_current = None
file_current = None
def current(fn, lon, lat, day = 0):
    if fn != fn_current:
        file_current = netCDF4.Dataset(current_files[fn])
    lat = -lat
    lon += -20  # wtf fix
    lon %=360
    lat += 70
    if lat >= 140:
        return None, None
    day %= 5  # units: day since 1992-10-05 00:00:00
    depth = 0
    if not file_current.variables['u'][day,depth,lat,lon] or not file_current.variables['v'][day,depth,lat,lon]:
        return None, None
    return file_current.variables['u'][day,depth,lat,lon], file_current.variables['v'][day,depth,lat,lon]

#print(file_current.variables['v'])

STEP = 10
currents_u = defaultdict(Counter)
currents_v = defaultdict(Counter)
#for t in range(4):

c = 0
for fn in list(current_files.keys()):
    for day in range(0, 72, 10):
        print(c)
        c += 1
        for lat in range(-90 + STEP, 90, STEP):
            for lon in range(-180+STEP, 180, STEP):
                x, y = m(lon, lat)
                dx, dy = current(fn, lon, lat, day)
                if not dx or not dy:
                    continue
                currents_u[lon][lat] += dx
                currents_v[lon][lat] += dy

plt.figure(figsize=(15, 10))#, dpi=80)
fig, ax = plt.subplots()
m = Basemap(projection='cyl', resolution='l')
m.drawcoastlines()
#m.bluemarble()
ax = plt.gca()
ax.set_ylim(-70, 75)

# normalise
mx1 = max([max([abs(currents_u[lon][lat]) for lat in currents_u[lon]]+[0]) for lon in currents_u])
mx2 = max([max([abs(currents_v[lon][lat]) for lat in currents_v[lon]]+[0]) for lon in currents_v])
mx = max(mx1, mx2)
mx = float(mx.data)
MAX_VECTOR = 20

for lat in range(-90 + STEP, 90, STEP):
    for lon in range(-180 + STEP, 180, STEP):
        x, y = m(lon, lat)
        dx = currents_u[lon][lat] * MAX_VECTOR / mx
        dy = currents_v[lon][lat] * MAX_VECTOR / mx
        if not dx or not dy:
            continue
        arrow = Arrow(x, y, dx, dy, width=5.0, color="red")  # https://matplotlib.org/stable/api/_as_gen/matplotlib.patches.Arrow.html
        ax.add_patch(arrow)

plt.show()

