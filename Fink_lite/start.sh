#!/bin/bash

killall python

python source/fink.py -k f5d8f6b8b21c44548d2799044d3105f0 -s b3845ea35176403bb530a31fd4481165 -t 5 -m 0.95 -n 1.03  &>/dev/null &

python manager.py -k f5d8f6b8b21c44548d2799044d3105f0 -s b3845ea35176403bb530a31fd4481165 -t 5 -m 0.95 -n 1.03 -ex 1 -r 1
python fink.py -p BTC-FTC -k f5d8f6b8b21c44548d2799044d3105f0 -s b3845ea35176403bb530a31fd4481165 -t 5 -m 0.95 -n 1.03 -ex 1
python account.py -k f5d8f6b8b21c44548d2799044d3105f0 -s b3845ea35176403bb530a31fd4481165 


python manager.py -k f5d8f6b8b21c44548d2799044d3105f0 -s b3845ea35176403bb530a31fd4481165 -t 60 -m 0.95 -n 1.03 -ex 1 -r 1 -st 2


python fink.py -k f5d8f6b8b21c44548d2799044d3105f0 -s b3845ea35176403bb530a31fd4481165 -t 5 -m 0.95 -n 1.03 -l 0.012 -f 0.236


//For fink lite
python fink.py -p BTC-XLM -k f5d8f6b8b21c44548d2799044d3105f0 -s b3845ea35176403bb530a31fd4481165 -t 5 -m 0.95 -n 1.03 -ex 1 -st 1 -l 0.012 

