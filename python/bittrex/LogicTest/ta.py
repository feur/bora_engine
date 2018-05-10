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









