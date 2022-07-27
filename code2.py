from matplotlib.backend_bases import MouseButton
from mpl_toolkits.basemap import Basemap
import matplotlib.pyplot as plt
import numpy as np
import matplotlib.colors as mcolors
from collections import deque, defaultdict
from geopy.distance import geodesic
from heapq import heappush, heappop  # -30% compared to deque
import random

"""
half Antarctica problem  https://github.com/matplotlib/basemap/issues/522
import _geoslib

/Users/fullname/Downloads/_private/data_snippets/env/lib/python3.8/site-packages/basemap-1.2.2+dev-py3.8-macosx-10.14-x86_64.egg/mpl_toolkits/basemap/__init__.py

cd /usr/local/lib/python3.8/site-packages/basemap-1.2.2+dev-py3.8-macosx-10.14-x86_64.egg

py -m pip install geos=3.8.1=h4a8c4bd_0
wget http://download.osgeo.org/geos/geos-3.8.1.tar.bz2
bzip2 -d geos-3.8.1.tar.bz2 
tar xzf geos-3.8.1.tar
../configure
mkdir build && cd build && cmake -DCMAKE_BUILD_TYPE=Release ..
make
make install

/usr/local/lib/libgeos.3.8.1.dylib
-- Installing: /usr/local/lib/libgeos_c.1.13.3.dylib
-- Installing: /usr/local/lib/libgeos_c.1.dylib
"""

CELL_SCAN_RADIUS = 1
LATTITUDE_NORTH_BOUNDARY = 160
LATTITUDE_SOUTH_BOUNDARY = 20
TOO_BIG_DISTANCE = 1e6

plt.figure(figsize=(15, 10))#, dpi=80)
m = Basemap(projection='cyl', resolution='l')
m.bluemarble()

"""
m.drawcoastlines()
m.drawmapboundary(fill_color='aqua')
_ = m.fillcontinents(color='coral',lake_color='aqua')
m.drawcountries()
m.drawparallels(np.arange(-90.,120.,10.))
m.drawmeridians(np.arange(0.,420.,20.))
m.drawmapboundary(fill_color='aqua')

ax = plt.gca()
ax.set_ylim(-70, 75)
"""


def norm_long(l):
    return l - 180

def norm_latt(l):
    return l - 90

def flatten(xss):
    return [x for xs in xss for x in xs]

def neighbours(x, y, d):
    result = []
    for i in range(-d, d+1):
        for j in range(-d, d+1):
            if i == 0 and j == 0:
                continue
            x1 = (x + i) % 360
            y1 = (y + j)
            if y1 <= 0 or y1 >= 180:
                continue
            result.append((x1, y1))
    return result

def is_land(x, y):
    return m.is_land(norm_long(x), norm_latt(y))  #TODO it is slow - 0.3 msec per call even on low Basemap resolution

c = 0
#start_point = 3+180, 53+90  # in North sea
start_point = 2+180, 52+90 # near London
#start_point = -10+180, 38+90 # near Lisbon
#TODO slow - go till edge of land
distances = [[(-1 if y<LATTITUDE_SOUTH_BOUNDARY or y>LATTITUDE_NORTH_BOUNDARY or is_land(x, y) else TOO_BIG_DISTANCE) for y in range(180)] for x in range(360)]
distances[-83+180][10+90] = -1  # PANAMA 1degree closure (x==-83 and y==10) or  (x==-82 and y==9) or  (x==-81 and y==9)
distances[-82+180][9+90] = -1
distances[-81+180][9+90] = -1
#edge = deque([start_point])
edge = []
heappush(edge, (0, start_point))
distances[start_point[0]][start_point[1]] = 0
while edge:
    #x0, y0 = edge.popleft()
    d0, (x0, y0) = heappop(edge)
    #d0 = distances[x0][y0]
    for scan in range(1, CELL_SCAN_RADIUS+1):  # if there is land n cells nearby, stop scan
        near_land = any([distances[x][y] < 0 for x, y in neighbours(x0, y0, scan)])
        if not near_land and scan != CELL_SCAN_RADIUS:
            continue
        for x, y in neighbours(x0, y0, 1 if near_land else scan):
            c += 1
            if c % 10_000 == 0:
                print(c, len([i for i in flatten(distances) if 0 < i < TOO_BIG_DISTANCE]))  # 1411000 49031     cell1  370000 35814
            if distances[x][y] < 0:  # land
                continue
            d = geodesic((norm_latt(y0), norm_long(x0)), (norm_latt(y), norm_long(x))).km + d0
            if distances[x][y] > d:
                distances[x][y] = d
                #edge.append((x, y))
                heappush(edge, (d, (x, y)))
        break

# extract edges
eq_step = 1_000
eq_range = eq_step
eq_ranges = defaultdict(list)
processed = set()

edge = []
heappush(edge, (0, start_point))
while edge:
    #x0, y0 = edge.popleft()
    d0, (x0, y0) = heappop(edge)
    if d0 > eq_range:
        eq_range += eq_step
    for x, y in neighbours(x0, y0, 1):
        if (x, y) in processed:
            continue
        else:
            processed.add((x, y))
        d = distances[x][y]
        if d > d0:
            heappush(edge, (d, (x, y)))
        if d0<eq_range and d > eq_range:
            eq_ranges[eq_range].append((x, y))


l = flatten([eq_ranges[i] for i in eq_ranges])
list(sorted([i[0] for i in l]))
list(sorted([i[1] for i in l]))

for y in range(15, 5, -1):
    print('')
    for x in range(-85, -75):
        if (x==-83 and y==10) or  (x==-82 and y==9) or  (x==-81 and y==9):
            print('ADD' + '\t', end='')
        else:
            print(str(m.is_land(x, y)) + '\t',end='')

for y in range(15, 5, -1):
    print('')
    for x in range(-85, -75):
        print(str(distances[x+180][y+90] < 0) + '\t', end='')

# draw edges

###  ###  ###  ###  ###  ###  ###  ###  ###  ###  ###

fig, ax = plt.subplots()
m = Basemap(projection='cyl', resolution='l')
m.drawcoastlines()

import random
for x in range(360):
    for y in range(LATTITUDE_SOUTH_BOUNDARY, LATTITUDE_NORTH_BOUNDARY):
        if random.random() < 0.001:
            s = str(int(distances[x][y]))
            #s = f'{x}, {y}'
            #s = str(m.is_land(x-180, norm_latt(y)))
            _ = ax.annotate(s, (norm_long(x), norm_latt(y)), xytext=(5, 5), textcoords='offset points')

for i in eq_ranges:
    for x, y in eq_ranges[i]:
        xx = norm_long(x)
        yy = norm_latt(y)
        _ = m.drawgreatcircle(xx, yy, xx + 1, yy + 1, color='r' if (i/eq_step)%2 == 0 else 'g')

plt.show()

###  ###  ###

for x in range(360):
    for y in range(180):
        if 15000 < distances[x][y] < 16000:
            if random.random() < 0.02:
                xx = norm_long(x)
                yy = norm_latt(y)
                _ = m.drawgreatcircle(xx, yy, xx+1, yy+1, color='r')

###  ###  ###  ###  ###  ###  ###  ###  ###  ###  ###

boundaries = [[0]*180 for x in range(360)]
for eq_range in eq_ranges:
    for x, y in eq_ranges[eq_range]:
        boundaries[x][y] = eq_range

plt.figure(figsize=(15, 10))#, dpi=80)
fig, ax = plt.subplots()
m = Basemap(projection='cyl', resolution='l')
m.drawcoastlines()
#m.bluemarble()
ax = plt.gca()
ax.set_ylim(-70, 75)


for x1 in range(360):
    for y1 in range(180):
        range_distance = boundaries[x1][y1]
        if range_distance:
            for x2, y2 in neighbours(x1, y1, 1):
                if boundaries[x2][y2] and (y2 > y1 or (y2 == y1 and x2 > x1)):
                    if abs(x1-x2) > 10 or (x1 == 0 and x2 == 0) or (x1 == 359 and x2 == 359): # will go cross map
                        continue
                    if y1 == y2 and ((y2-1 >= 0 and boundaries[x2][y2-1]) or (y2+1 < 180 and boundaries[x2][y2+1])):
                        continue
                    if x1 == x2 and ((x2-1 >= 0 and boundaries[x2-1][y2]) or (x2+1 < 360 and boundaries[x2+1][y2])):
                        continue
                    color = 'r' if (range_distance/eq_step)%2 == 0 else 'g'
                    _ = m.drawgreatcircle(norm_long(x1), norm_latt(y1), norm_long(x2), norm_latt(y2), color=color)
                    #print(x1, x2, y1, y2)

random.seed(1)
annotations = set()
while annotations != set(eq_ranges.keys()):
    for x1 in range(360):
        for y1 in range(180):
            range_distance = boundaries[x1][y1]
            if not range_distance:
                continue
            if random.random() < 0.001 and range_distance not in annotations:
                annotations.add(range_distance)
                #color = 'r' if (range_distance / eq_step) % 2 == 0 else 'g'
                _ = ax.annotate(f'{range_distance:,}', (norm_long(x1), norm_latt(y1)), xytext=(1, 1), textcoords='offset points', fontsize=7, weight='bold')

plt.show()


###  ###  ###


"""

for eq_range in eq_ranges:
    #eq_range = 10_000
    dots = eq_ranges[eq_range]
    while dots:
        print('dots', len(dots))
        dots.sort(key=lambda a: a[1]*360 + a[0])
        leftover_dots = []
        boundary = deque([dots[0]])
        for x, y in dots[1:]:
            x0, y0 = boundary[-1]
            d = geodesic((norm_latt(y0), x0), (norm_latt(y), x)).km
            if d < 3 * 111: #TODO 2?
                boundary.append((x, y))
            else:
                leftover_dots.append((x, y))
            x0, y0 = boundary[0] #TODO drop
            d = geodesic((norm_latt(y0), x0), (norm_latt(y), x)).km
            if d < 2 * 111:
                boundary.appendleft((x, y))
            else:
                leftover_dots.append((x, y)) #TODO merge lines?
        boundary = list(boundary)
        for a, b in zip(boundary[:-1], boundary[1:]):
            x1, y1 = a
            x2, y2 = b
            if abs(norm_long(x1) - norm_long(x2)) > 100:
                continue
            if random.random() < 0.5:
                _ = m.drawgreatcircle(norm_long(x1), norm_latt(y1), norm_long(x2), norm_latt(y2), color='r')
            _ = 1 == 1
        print('boundary', len(boundary))
        dots = leftover_dots
    break

        boundary = list(boundary)
        for a, b in zip(boundary[:-1], boundary[1:]):
            x1, y1 = a
            x2, y2 = b
            if abs(norm_long(x1) - norm_long(x2)) > 100:
                continue
            if random.random() < 0.5:
                _ = m.drawgreatcircle(norm_long(x1), norm_latt(y1), norm_long(x2), norm_latt(y2), color='r')
            _ = 1 == 1
        print('boundary', len(boundary))
        dots = leftover_dots
    break
"""

