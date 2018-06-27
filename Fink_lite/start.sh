#!/bin/bash

killall python

python source/fink.py -k f5d8f6b8b21c44548d2799044d3105f0 -s b3845ea35176403bb530a31fd4481165 -t 5 -m 0.95 -n 1.03  &>/dev/null &

python manager.py -k f5d8f6b8b21c44548d2799044d3105f0 -s b3845ea35176403bb530a31fd4481165 -t 5 -m 0.95 -n 1.03 -ex 1 -r 1
python fink.py -p BTC-FTC -k f5d8f6b8b21c44548d2799044d3105f0 -s b3845ea35176403bb530a31fd4481165 -t 5 -m 0.95 -n 1.03 -ex 1
python account.py -k f5d8f6b8b21c44548d2799044d3105f0 -s b3845ea35176403bb530a31fd4481165 


python manager.py -k f5d8f6b8b21c44548d2799044d3105f0 -s b3845ea35176403bb530a31fd4481165 -t 60 -m 0.95 -n 1.03 -ex 1 -r 1 -st 2
python fink.py -p BTC-XLM -k f5d8f6b8b21c44548d2799044d3105f0 -s b3845ea35176403bb530a31fd4481165 -t 5 -m 0.95 -n 1.03 -ex 1 -st 2

______


-st 1: 

Buy when: 
self.active == 0 and self.current['L'] < self.BuyPrice
self.BuyPrice = float(self.kijunSen[0] * self.BuyBuffer)

Sell when: 
self.active == 1 

-st 2 when at 1 hour: 

Buy when: 

self.active == 1
self.BuyPrice = float(self.tenkansen[0] * self.BuyBuffer)


sell when: 
self.SellPrice = float(self.tenkansen[0] * self.SellBuffer)



