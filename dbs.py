import os
import netCDF4
from collections import defaultdict, OrderedDict
import numpy as np

WIND_PATH = 'www.ncei.noaa.gov/data/blended-global-sea-surface-wind-products/access/winds/6-hourly/'
CURRENT_PATH = 'oscar/'

CACHE_SIZES = {WIND_PATH: 2*7*4+1, CURRENT_PATH: 2}


# cached data
file_paths = defaultdict(dict)
cache = defaultdict(OrderedDict)


def get_cached_file(path, fname):
    if fname not in cache[path]:
        if len(cache) > CACHE_SIZES[path]:
            k, _ = cache.popitem()  # pop last
            print(f'evicted "{k}" from cache {path=}')
        cache[path][fname] = netCDF4.Dataset(file_paths[path][fname])
    cache[path].move_to_end(fname, last=False)
    return cache[path][fname]


def fill_files(path):
    for root, subdirs, files in os.walk(path):
        for file in files:
            if file.endswith('.nc'):
                file_paths[path][file] = root + os.sep + file


def wind_fname(dt):  # uv19960413.nc
    fname = f'uv{dt.year}{dt.month:02}{dt.day:02}.nc'
    t = dt.hour // 6
    return t, fname


def wind(dt, lon, lat):
    t, fname = wind_fname(dt)
    file_wind = get_cached_file(WIND_PATH, fname)
    lon += 360
    lon %=360
    lat += 90
    lon= int(lon * 4)
    lat = int(lat * 4)
    u, v = file_wind.variables['u'][t][0][lat][lon], file_wind.variables['v'][t][0][lat][lon]
    return (u, v) if isinstance(u, np.float32) and isinstance(v, np.float32) else (None, None)


def current_fname(dt):  # world_oscar_vel_5d1996.nc
    fname = f'world_oscar_vel_5d{dt.year}.nc'
    day = dt.timetuple().tm_yday
    day %= 5  # units: day since 1992-10-05 00:00:00
    if day >= 72:
        day = 72 - 1
    return day, fname


def current(dt, lon, lat):
    day, fname = current_fname(dt)
    file_current = get_cached_file(CURRENT_PATH, fname)
    lon, lat = round(lon), round(lat)
    lat = -lat
    lon += -20  # wtf fix
    lon %=360
    lat += 70
    if lat >= 140:
        return None, None
    depth = 0
    u, v = file_current.variables['u'][day,depth,lat,lon], file_current.variables['v'][day,depth,lat,lon]
    return (u, v) if isinstance(u, np.float32) and isinstance(v, np.float32) else (None, None)


fill_files(WIND_PATH)
fill_files(CURRENT_PATH)