#!/usr/bin/env bash

# TODO
# winds NOAA
wget -c -N --accept-regex='.*1997.*' -r https://www.ncei.noaa.gov/data/blended-global-sea-surface-wind-products/access/winds/6-hourly/1997/

# currents OSCAR
wget -c -N --accept-regex='.*world_oscar_vel.*' -r https://podaac-opendap.jpl.nasa.gov/opendap/allData/oscar/L4/oscar_1_deg/contents.html

mkdir seanoe
cd seanoe

# 2003-2011
#wget https://www.seanoe.org/data/00601/71337/data/73474.tar.gz
wget https://www.seanoe.org/data/00601/71337/data/73475.tar.gz
wget https://www.seanoe.org/data/00601/71337/data/73476.tar.gz
wget https://www.seanoe.org/data/00601/71337/data/73477.tar.gz
wget https://www.seanoe.org/data/00601/71337/data/73478.tar.gz
wget https://www.seanoe.org/data/00601/71337/data/73479.tar.gz
wget https://www.seanoe.org/data/00601/71337/data/73480.tar.gz
wget https://www.seanoe.org/data/00601/71337/data/73481.tar.gz
wget https://www.seanoe.org/data/00601/71337/data/73482.tar.gz

tar -xzvf *.gz
cd ..