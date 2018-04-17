from bittrex.bittrex import *
import argparse
from statistics import mean
import os
import MySQLdb
import traceback
import datetime
from settings import *
from ta import *



def GetEntry():
    parser = argparse.ArgumentParser(description='Process TA for pair')
    parser.add_argument('-p', '--pair',
                        action='store',  # tell to store a value
                        dest='pair',  # use `paor` to access value
                        help='The Pair to be watched')
    parser.add_argument('-a', '--high1',
                        type=float,
                        action='store',  # tell to store a value
                        dest='a',  # use `a` to access value
                        help='fib zone 1')
    parser.add_argument('-b', '--low1',
                        type=float,
                        action='store',  # tell to store a value
                        dest='b',  # use `d` to access value
                        help='fib zone 1')
    parser.add_argument('-c', '--high2',
                        type=float,
                        action='store',  # tell to store a value
                        dest='c',  # use `b` to access value
                        help='fib zone 2')
    parser.add_argument('-d', '--low2',
                        type=float,
                        action='store',  # tell to store a value
                        dest='d',  # use `c` to access value
                        help='fib zone 2')
    parser.add_argument('-e', '--high3',
                        type=float,
                        action='store',  # tell to store a value
                        dest='e',  # use `e` to access value
                        help='fib zone 3')
    parser.add_argument('-f', '--Low3',
                        type=float,
                        action='store',  # tell to store a value
                        dest='f',  # use `e` to access value
                        help='fib zone 3')
    pair = parser.parse_args()
    return pair


class MyPair(object):

    def __init__(self, entry):
        """
            {u'C': 3.079e-05, u'H': 3.079e-05, u'L': 3.079e-05, u'O': 3.079e-05, u'BV': 0.04902765, u'T': u'2018-04-13T07:10:00', u'V': 1592.32422805}
            """
        account = Bittrex("f5d8f6b8b21c44548d2799044d3105f0", "b3845ea35176403bb530a31fd4481165", api_version=API_V2_0)
        data = account.get_candles(entry.pair, tick_interval=TICKINTERVAL_FIVEMIN)
        if (data['success'] == True):
            self.data = data['result']
            self.current = self.data[-1]
            self.entry = entry

    def GetSignal(self):

        tenkanSen = GetIchimokuAverage(GetFramedData(self.data, 9))
        kijunSen = GetIchimokuAverage(GetFramedData(self.data, 26))
        senkouA = (tenkanSen + kijunSen) / 2
        senkouB = GetIchimokuAverage(GetFramedData(self.data, 52))

        print(tenkanSen)
        print(kijunSen)

        if tenkanSen == kijunSen:
            self.signal = 1
        else:
            self.signal = 0
        
    def GetRating(self):
        
        #print("Di+ is %.9f" % diPos)
        #print("Di- is %.9f" % diNeg)
        #print("DAX is %.9f" % dax)
        #print("Momentum is %.9f" % momentum)
        #print("Fib is %.9f" % fib)
        
        self.momentum = GetMomentum(self.data)        
        self.fib = GetFib(self.current['C'], entry.a, entry.b, entry.c, entry.d, entry.e, entry.f)
        self.rating = self.fib * self.momentum


entry = GetEntry()
pid = os.getpid() 

while True: 

    pair = MyPair(entry)


    print(pid)

    print("current price is: %.9f" % pair.current['C'])
    pair.GetSignal()
    pair.GetRating()

    print(pair.signal)
    print(pair.fib)
    print(pair.momentum)
    print(pair.rating)








