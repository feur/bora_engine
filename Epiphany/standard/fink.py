import argparse
from pair import *
import time
import os
import subprocess
import psutil



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
    
    
    



entry = GetEntry() 
pair = MyPair(entry)
pair.SetParams(entry)

if (pair.ex == 1):
    pair.Trade()
else:

    while(True):
        pair.Trade()
        time.sleep(50) ## should be enough delay to not throttle the api






