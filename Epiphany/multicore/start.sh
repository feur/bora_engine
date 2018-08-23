#!/bin/bash

killall python

python init.py -k f5d8f6b8b21c44548d2799044d3105f0 -s b3845ea35176403bb530a31fd4481165 -l 0.035
python taskmanager.py &>/dev/null &


