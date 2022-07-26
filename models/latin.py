import numpy as np

# ? https://github.com/hrosailing/hrosailing  import hrosailing.polardiagram as pol

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


def _ship_speed(wind_index, degrees):
    degrees_lst = [0, 52, 60, 75, 90, 110, 120, 135, 150, 180]
    for i, d in enumerate(degrees_lst):
        if degrees < degrees_lst[i+1]:
            d1, d2 = d, degrees_lst[i+1]
            return np.interp(degrees, [d1, d2], [data[i][wind_index], data[i+1][wind_index]])


def ship_speed(wind_speed, degrees):  #TODO waves    180 degrees = wind from behind, 0 - against wind
    degrees = abs(degrees)
    degrees = degrees % 360
    if degrees >= 180:
        degrees = 180 - degrees
    if wind_speed >= 20:
        wind_speed = 10  # lower sails!
    speeds = [0, 6, 8, 10, 12, 14, 16, 20]
    for i, s in enumerate(speeds):
        if wind_speed < speeds[i+1]:
            wind_index = i-1
            wind_speed1, wind_speed2 = s, speeds[i+1]
            break
    ship_speed1 = _ship_speed(wind_index, degrees) if wind_speed1 else 0
    ship_speed2 = _ship_speed(wind_index+1, degrees)
    drift = 0
    return drift, np.interp(wind_speed, [wind_speed1, wind_speed2], [ship_speed1, ship_speed2])


assert _ship_speed(1, 90) == 9.27
assert _ship_speed(1, 100) == (9.27+8.62)/2
assert ship_speed(8, 90) == 9.27