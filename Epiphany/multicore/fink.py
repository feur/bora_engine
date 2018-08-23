from bittrex.bittrex import *
import argparse
import time
import os
import subprocess
import psutil
import MySQLdb
import time
import datetime
import numpy as np
from pair import *
from settings import *
from ta import *



def GetEntry():
    
    parser = argparse.ArgumentParser(description='Agent trading for pair')
    
    parser.add_argument('-k', '--key',
                        action='store',  # tell to store a value
                        dest='api',  # use `paor` to access value
                        help='Your API Key')
    parser.add_argument('-s', '--secret',
                        action='store',  # tell to store a value
                        dest='secret',  # use `paor` to access value
                        help='Your API Secret')
    parser.add_argument('-u', '--uid',
                        action='store',  # tell to store a value
                        dest='uid',  # use `paor` to access value
                        help='Your FINK UID')
    
    parser.add_argument('-p', '--pair',
                        action='store',  # tell to store a value
                        dest='pair',  # use `pair` to access value
                        help='The Pair to be watched')
    parser.add_argument('-c', '--currency',
                        action='store',  # tell to store a value
                        dest='currency',  # use `pair` to access value
                        help='The currency for the pair')
    
    parser.add_argument('-l', '--limit',
                        action='store',  # tell to store a value
                        dest='limit',  # use `paor` to access value
                        help='Your Buy Limit')
    parser.add_argument('-t', '--time',
                        action='store',  # tell to store a value
                        dest='time',  # use `paor` to access value
                        help='Time Interval')
    parser.add_argument('-a', '--aggression',
                        action='store', # tell to store a value
                        dest='agLvl',  # use `paor` to access value
                        help='your level of aggression ')
    parser.add_argument('-lp', '--lookback',
                        action='store', # tell to store a value
                        dest='lp',  # use `paor` to access value
                        help='lookback period ')
    parser.add_argument('-sl', '--stoploss',
                        action='store', # tell to store a value
                        dest='sl',  # use `paor` to access value
                        help='your stoplosss')
    
    parser.add_argument('-st', '--standalone',
                        action='store',  # tell to store a value
                        dest='st',  # use `pair` to access value
                        help='If you want to work without a database')
    parser.add_argument('-ex', '--experiment',
                        action='store',  # tell to store a value
                        dest='ex',  # use `pair` to access value
                        help='Experimentation no trading')
    
    parser.add_argument('-ip', '--masterip',
                        action='store',  # tell to store a value
                        dest='ip',  # use `pair` to access value
                        help='IP address of master')
    
    
   
    action = parser.parse_args()
    return action
    
    
@offload
def BackTest(close, low, high, CRMI, Floor, rl, IchtPeriod, lp, sl):
    
    result = [0,0,0,0] #Profit, Wins, Lossess
    
    state = 0
    order = 0
    hold = 0
    initial = 0
    bought = 0
    loss = 0
    wins = 0
    profit = 0
    
    fee = 0.0055 ##0.55% fee 
    
    
    for i in range (len(close)-1-lp,len(close)-2):
        
        if (CRMI[i] <= Floor):
            state = 1
        else: 
            state = 0
            order = 0
                            
        if (hold == 0 and state == 1 and (order == 0 or order == 1)):
            buyPrice = close[i]
            bought += 1   
            order = 1
                        
                            
        elif (hold == 1 and (order == 0 or order == 2)):
            absolutemin = float(initial * (1+fee))      ##absolute minimum is to cover the fee
            minimum = float(close[i] * (rl + fee))    ##minium is just slighlty above the fee
            maximum = float(initial * rl)          ## maximum return limit

            position = float((close[i]) / initial)
                        
            if (position < 1 and minimum > absolutemin):
                sellPrice = minimum
            elif (position >= 1): ##current closing price at initial or above
                sellPrice = maximum
            elif position <= sl: ##stop loss
                sellPrice = close[i] 
            else:
                sellPrice = absolutemin
                
            order = 2
                                         
         
        if order == 1 and buyPrice >= low[i+1]: ## to make sure order is completed 
            buy = buyPrice
            hold = 1    
            order = 0
            initial = buy ##initial position
                    
                        
        if order == 2 and sellPrice <= high[i+1]:
            sell = sellPrice
            hold = 0 
            order = 0
            r = float(float(float(sell)/float(buy) - 1.005)*100)
                        
            if (r < 0):
                loss += 1
            elif (r > 0):
                wins += 1
                            
            profit = float(profit)+float(r)
                        
                            
                            
    if (hold == 1): ##take care of unifnihsed business
        sell = close[i]                           
                                    
        r = float(float(float(sell)/float(buy) - 1.005)*100)
        
        if (r < 0):
            loss += 1
        elif (r > 0):
            wins += 1
                            
        profit = float(profit)+float(r)
        
    result[0] = profit
    result[1] = wins
    result[2] = loss   
    result[3] = Floor
    return result 
    



entry = GetEntry() 
pair = MyPair(entry)
pair.SetParams(entry)

if (pair.ex == 1):
    pair.Trade()
else:

    while(True):
        pair.Trade()
        time.sleep(50) ## should be enough delay to not throttle the api






