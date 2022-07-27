import dbs  # dbs.current dbs.wind(dt, lon, lat)
from models.latin import ship_speed  # ship_speed(wind_speed, degrees)
import math
import pyproj
from datetime import datetime, timedelta

DT_STEP = timedelta(minutes = 60)  # timedelta(hours = 1)


def norm_long(l):
    return l - 180

def norm_latt(l):
    return l - 90

def is_land(m, x, y):
    return m.is_land(norm_long(x), norm_latt(y))


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

marked_days = set()
prev = (0,0)
def run_path(start_dt, ax, m, cur_dt, cur_lon, cur_lat, next_lon, next_lat, max_dt=None):
    global prev
    geodesic = pyproj.Geod(ellps='WGS84')
    while True:
        if cur_dt - start_dt > max_dt:
            return None
        #
        #day = (cur_dt - start_dt).days
        #if day % 7 == 0 and day not in marked_days:
        #    marked_days.add(day)
        #    ax.annotate(str(day), (cur_lon, cur_lat), xytext=(5, 5), textcoords='offset points')
        #
        fwd_azimuth, _, distance = geodesic.inv(cur_lon, cur_lat, next_lon, next_lat)
        current_u, current_v = dbs.current(cur_dt, cur_lon, cur_lat)
        if not current_u or not current_v:
            current_u, current_v = 0, 0
        wind_u, wind_v = dbs.wind(cur_dt, cur_lon, cur_lat)
        ####### #TODO
        if wind_u is None or wind_v is None:
            wind_u, wind_v = prev
            #print(f'empty wind {prev=}')
        else:
            prev =  wind_u, wind_v
        #######
        if is_land(m, cur_lon, cur_lat):
            print(f'Ran aground {cur_dt=} {cur_lon=} {cur_lat=} !!!')
            return None
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
        if drift_speed != 0:
            drift_distance = drift_speed * DT_STEP.seconds
            cur_lon, cur_lat, _ = geodesic.fwd(cur_lon, cur_lat, vector_degree(wind_u, wind_v), drift_distance)  # wind drift
        current_distance = vector_len(current_u, current_v) * DT_STEP.seconds
        cur_lon, cur_lat, _ = geodesic.fwd(cur_lon, cur_lat, vector_degree(current_u, current_v), current_distance)  # current
        cur_dt += DT_STEP