from bittrex.bittrex import *
import argparse
from statistics import mean
import MySQLdb
import traceback
import datetime
from settings import *



def GetFib(current, a, b, c, d, e,f):

    if current < e:
        high = e
        low = f
    elif current > e and current < c:
        high = c
        low = d
    elif current > c and current < a:
        high = a
        low = b
    else:
        return  1
        
        
    print("Fib is between %0.9f and %0.9f" % (high,low))
    
    fib = (current - low) / (high - low)
    return fib
    


def GetDX(diPos, diNeg):
    diDiff = abs(diPos - diNeg)
    diSum  = diPos + diNeg
    dx = 100 * (diDiff / diSum)
    return dx
    
def GetADX(dx):
    adx = mean(dx)
    return adx
    
def GetEMA(data, period, prevEMA):
    
    Multiplier = 2 / (float(period) + 1)
    
    
    ##now get average by periods 
    Sum = 0 
    
    if (prevEMA == 0):   
        
        for i in range (0,period-1):
            Sum += data[i]['C']
       
        prev = Sum / period ##get the first SMA of the series
        
        for i in range (period,len(data) - 1):
            EMA = data[i]['C'] * Multiplier + prev * (1 - Multiplier)
            prev = EMA
        
    else:
        prev = prevEMA
        EMA = data[-1]['C'] * Multiplier + prev * (1 - Multiplier)

    return EMA    
    

    
def GetMomentum(data):
    current = data[-1]
    previous = data[-11]
    momentum = (current['C'] / previous['C'] * 100)
    return momentum
    
def GetIchimokuAverage(data):
    #get list of high & low#
    high=[]
    low=[]
    for item in data:
        high.append(item['H'])
        low.append(item['L'])

    result = (mean(high) + mean(low)) / 2
    return result

def GetFramedData(data,window):
        data_window=[]

        for i in range (len(data)-window,len(data)):
            data_window.append(data[i])

        return data_window









