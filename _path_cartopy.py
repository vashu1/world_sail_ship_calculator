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
            plt.plot([0,0], [5,45],#[prev[0], prev[1]], [-0.4, -0.4],
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

"""

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