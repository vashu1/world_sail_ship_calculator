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

prev = None
path_indx = 0
path_colors = list(mcolors.BASE_COLORS.values())
def on_click(event):
    global prev, path_indx, path_colors
    if event.button is MouseButton.LEFT:
        lat, lon = event.ydata, event.xdata
        x, y = m(lon, lat)
        print(x, y)
        if prev:
            print('plot')
            #m.plot([prev[0], x], [prev[1], y], 'o-', markersize=3, linewidth=1, color=path_colors[path_indx])
            m.drawgreatcircle(prev[0], prev[1], x, y, color='r')
            ax.annotate(str(path_indx), (x,y), xytext=(5, 5), textcoords='offset points')
            plt.draw()
        prev = x, y
    elif event.button is MouseButton.RIGHT:
        prev = None
        path_indx = (path_indx + 1) % len(path_colors)

plt.connect('button_press_event', on_click)

plt.show()
"""

# pip3 install Cartopy
import cartopy.crs as ccrs
import matplotlib.pyplot as plt

from matplotlib.backend_bases import MouseButton
import matplotlib.colors as mcolors




ax = plt.axes(projection=ccrs.PlateCarree())
ax.coastlines() # projections https://scitools.org.uk/cartopy/docs/v0.15/crs/projections.html#cartopy-projections

proj = ccrs.TransverseMercator()
proj_cart = ccrs.PlateCarree()

prev = None
path_indx = 0
path_colors = list(mcolors.BASE_COLORS.values())
def on_click(event):
    global prev, path_indx, path_colors
    if event.button is MouseButton.LEFT:
        x, y = event.ydata, event.xdata
        rel = ax.transData.inverted().transform((x, y))
        lon, lat = proj_cart.transform_point(*rel, src_crs=proj)
        print('rel lon/lat x/y', rel, lon, lat, x, y)
        if prev:
            plt.plot([prev[0], prev[1]], [x, y],
                     color='blue', linewidth=2, marker='o',
                     transform = proj_cart,
                     #transform=ccrs.PlateCarree(),
                     )
            #ax.annotate(str(path_indx), (lon, lat), xytext=(5, 5), transform=proj_cart, textcoords='offset points')
            plt.draw()
        prev = x, y
    elif event.button is MouseButton.RIGHT:
        prev = None
        path_indx = (path_indx + 1) % len(path_colors)

plt.connect('button_press_event', on_click)
plt.show()




# (0.3, 0.4) rel
# (157, 234) point
# -75, 43  NY lon lat

import cartopy.crs as ccrs
import matplotlib.pyplot as plt
proj = ccrs.TransverseMercator()
proj_cart = ccrs.PlateCarree()

f, ax = plt.subplots(subplot_kw=dict(projection=proj))
ax.coastlines()

# define point
rel = (0.6, 0.6)
point = ax.transAxes.transform(rel)  # array([377.6 , 274.56])
rel = ax.transData.inverted().transform(point)  # array([0.6, 0.6])

p_a_cart = proj_cart.transform_point(*rel, src_crs=proj_cart)
proj_cart.transform_point(*rel, src_crs=proj)
proj.transform_point(*rel, src_crs=proj_cart)
"""