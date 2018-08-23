from bittrex.bittrex import *
import argparse
import MySQLdb
import traceback
import datetime
from settings import *
import numpy as np




def GetFib(current, a, b, c, d, e,f):
    
    ##find High first
    if current < a and current > c:
        high = a
    elif current < c and current > e: 
        high = c
    elif current < e: 
        high = e
    elif current > a:
        high = a
        
    if high == a:
        low = b
    elif high == c:
        low = d
    elif high == e:
        low = f
        
        
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
    
def GetEMA(data, n, prevEMA):
    
    x = 0
    K = 2 / (float(n) + 1)
    
    if (prevEMA == 0):
        for i in range (0,n-1):
            x += data[i]
        
        prev = float(x/n) ##prev is SMA of period n
    else:
        prev = prevEMA
            
    EMA = float(data[-1] * K + prev * (1-K))
    
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









