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
    
def GetTr(data):
    tr=[]

    for i in range(1,28):
       itemP = data[i-1]
       itemN = data[i]
       maximum = max(abs(itemN['H'] - itemN['L']), abs(itemN['H'] - itemN['C']), abs(itemN['L'] - itemP['C']))
       tr.append(maximum)

    print(tr)
    return tr
    
def GetTrMax(tr):
    trMax=[]

    dis = 14
    sum = 0

    for i in range (0, dis):
        sum += tr[i]

    trMax.append(sum)

    for i in range(1,dis):
        trMax.append(trMax[i-1] - (trMax[i-1]/14) + tr[i+dis])

    print(len(trMax))
    return trMax
    
def GetdmPos(data):
    dmPos=[]

    for i in range(1,28):
        itemP = data[i-1]
        itemN = data[i]

    if (itemN['H'] - itemP['H']) > (itemP['L'] - itemN['L']):
        dmPos.append(0)
    else:
        dmPos.append(max((itemN['H'] - itemP['H']), 0))

    print(dmPos)
    return dmPos
    
def GetdmNeg(data):
    dmNeg=[]
    for i in range(1,28):
        itemP = data[i-1]
        itemN = data[i]

    if (itemP['L'] - itemN['L']) > (itemN['H'] - itemN['H']):
        dmNeg.append(0)
    else:
        dmNeg.append(max((itemP['L'] - itemN['L']), 0))

    print(dmNeg)
    return dmNeg
    
def GetdiPos(tr,dmPos,dmNeg):
    trMax = sum(tr)
    diPos = 100 * (dmPos/trMax)
    return diPos

#def GetdiNeg(data):
 #   return diNeg

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
    momentum = (current['C'] / previous['C'] - 1)
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









