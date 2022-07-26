#!/usr/bin/env bash

# TODO
# winds NOAA
# currents OSCAR

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