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
import dbs  # dbs.current dbs.wind(dt, lon, lat)
from models.latin import ship_speed  # ship_speed(wind_speed, degrees)
import navigation

# 'merc' - Mercator Very large distortion at high latitudes, cannot fully reach the polar regions.
# 'cyl' Equidistant just displays the world in latitude/longitude coordinates.
# 'mill' Miller  mercator projection that avoids the polar singularity
# projection='aeqd' Azimuthal  The shortest route from the center of the map to any other point is a straight line in the azimuthal equidistant projection.
# projection='moll' Mollweide  global, elliptical, equal-area projection.    also 'hammer'
# 'robin'  Robinson  once used by the National Geographic Society for world maps
# 'vandg' van der Grinten Projection - shows the world in a circle centered on the equator.
# 'sinu' length of each parallel is equal to the cosine of the latitude.



#fig, ax = plt.subplots()


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

#print(f'{path=}')
#TODO undo
#path = [(-13.612903225806463, 48.14516129032256), (-30.80645161290323, 34.112903225806434), (-47.741935483870975, 34.758064516129025)]

plt.figure(figsize=(15, 10))#, dpi=80)
m = Basemap(projection='cyl', resolution='l')
m.drawcoastlines()
#m.bluemarble()
ax = plt.gca()
ax.set_ylim(-70, 75)

for (x1,y1), (x2, y2) in zip(path, path[1:]):
    m.drawgreatcircle(x1, y1, x2, y2, color='r')



# wind - 95-97, 2000, 2004-5    current 96-05   waves 2003-

start_dt = cur_dt = datetime(year=1997, month=5, day=30, hour=12)
cur_lon, cur_lat = path[0]




for next_lon, next_lat in path[1:]:
    print('step', cur_dt)
    cur_dt = navigation.run_path(start_dt, ax, m, cur_dt, cur_lon, cur_lat, next_lon, next_lat)


print('END', cur_dt)


plt.show()