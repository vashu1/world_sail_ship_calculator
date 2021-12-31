# find ship polars
# use coordinates present in both datasets
# scan +-2 cells - 25 grid

"""
ICE https://www.saf21.eu/2017/04/29/plotting-seas-with-python-and-ices-shape-file/

ocean waves dataset


"""
import numpy as np
import heapq
import datetime
from collections import OrderedDict

import netCDF4
from timeit import Timer
import os, sys

"""TODO
polar

draw equidistant


utility for path file
path -> speed per day
"""

START_POINT = (51.5, 1.25)  # y x   lat lon   near London
assert(all(map(lambda x: x % 0.25 == 0, START_POINT)))  # to quarter degree
START_TIME = '2000-06-01 12:00'  # "yyyy-mm-dd H:M"
START_TIME = datetime.datetime.strptime(START_TIME, '%Y-%m-%d %H:%M')

SCAN_NEIGHBOURS_DISTANCE = 2  # +/- 2 cells

# state
arrival_time_state = np.empty((180*4,360*4))  # in seconds from START_TIME
arrival_from_state = np.empty((180*4,360*4,2))  # y x
arrival_time_state.fill(np.Inf)
arrival_from_state.fill(np.Inf)

# polar data
# modern yacht https://hsto.org/webt/o0/dr/h3/o0drh3kgbbnxm0_2srzeagmxgj8.png  http://ukryachting.net/education/aerodinamika/mal_13_2.gif
polar = [0] * 360  # 0 is against wind
if all(map(lambda x: x==0, polar[180:])):  # only 0-179 half is filled, mirror it
    for i in range(1, 180):
        polar[360 - i] = polar[i]

def speed(angle_degrees, wind):
    return 1

# interpolate
# enrich with tacking speeds

def point_to_indexes(point):
        y, x = point
        return int(y/0.25), int(x/0.25)


def process_step(start_time, start, end):
    start, end = point_to_indexes(start), point_to_indexes(end)
    if arrival_time_state[start] > arrival_time_state[end]:
        return
    # calculate travel


def process_point(start_time, start):
    y, x = start
    for i in range(-SCAN_NEIGHBOURS_DISTANCE, +SCAN_NEIGHBOURS_DISTANCE):
        for j in range(-SCAN_NEIGHBOURS_DISTANCE, +SCAN_NEIGHBOURS_DISTANCE):
            if i == 0 and j ==0:
                continue
                yy = y + i * 0.25
                xx = x + j * 0.25
                process_step(start_time, start, (yy, xx))

start = point_to_indexes(START_POINT)
arrival_time_state[start] = 0
travel_front = []
# heapq.heappush(travel_front, (time, cell))
# heapq.heappop(travel_front)

process_point(start_time, start)
while travel_front:
    cell = heapq.heappop(travel_front)
    process_point(start_time, cell)



def read_netcdf(filename):
    file = netCDF4.Dataset(filename)
    data = file.variables[:]   # ['data'][:]  # keys ['time', 'zlev', 'lat', 'lon', 'u', 'v']
    file.close()

# Blended_Sea_Winds_dataset_6hourly/www.ncei.noaa.gov/data/blended-global-sea-surface-wind-products/access/winds/6-hourly
# 1995/uv19950115.nc


file = netCDF4.Dataset('1995/uv19950115.nc')

wind_files = {}
for root, subdirs, files in os.walk('www.ncei.noaa.gov'):  #'./Blended_Sea_Winds_dataset_6hourly'):
    for file in files:
        if file.endswith('.nc'):
            print(root, subdirs, file)
            wind_files[file] = root + '/' + file

wind_root_path = 'www.ncei.noaa.gov/data/blended-global-sea-surface-wind-products/access/winds/6-hourly'
cache_size = 10
cache = OrderedDict()
def get_file(travel_time):
    dt = START_TIME + datetime.timedelta(seconds=travel_time)
    filename = f'uv{dt.year}{dt.month:02}{dt.day:02}.nc'
    if filename in cache:
        f = cache[filename]
    else:
        if len(cache) > cache_size:
            k, _ = cache.popitem()  # pop last
            print(f'evicted "{k}" from cache')
        f = netCDF4.Dataset(f'{wind_root_path}/{dt.year}/{filename}')
        cache[filename] = f
    return f


import datetime

datetime.datetime.strptime(date_time_str, '%Y-%m-%d %H:%M:%S.%f')