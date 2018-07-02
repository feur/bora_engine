import argparse
from pair import *
import time



def GetEntry():
    
    parser = argparse.ArgumentParser(description='Process TA for pair')
    parser.add_argument('-p', '--pair',
                        action='store',  # tell to store a value
                        dest='pair',  # use `pair` to access value
                        help='The Pair to be watched')
    parser.add_argument('-k', '--key',
                        action='store',  # tell to store a value
                        dest='api',  # use `paor` to access value
                        help='Your API Key')
    parser.add_argument('-s', '--secret',
                        action='store',  # tell to store a value
                        dest='secret',  # use `paor` to access value
                        help='Your API Secret')
    parser.add_argument('-l', '--limit',
                        action='store',  # tell to store a value
                        dest='limit',  # use `paor` to access value
                        help='Your Buy Limit')
    parser.add_argument('-m', '--buybuffer',
                        action='store',  # tell to store a value
                        dest='buyBuffer',  # use `paor` to access value
                        help='your buy buffer')
    parser.add_argument('-n', '--sellbuffer',
                        action='store',  # tell to store a value
                        dest='sellBuffer',  # use `paor` to access value
                        help='your sell buffer')
    parser.add_argument('-ex', '--simulate',
                        action='store',  # tell to store a value
                        dest='ex',  # use `paor` to access value
                        help='Simulation on or off')
    parser.add_argument('-t', '--time',
                        action='store',  # tell to store a value
                        dest='time',  # use `paor` to access value
                        help='Time Interval')
    parser.add_argument('-st', '--strat',
                        action='store',  # tell to store a value
                        dest='st',  # use `paor` to access value
                        help='Strategy')
    parser.add_argument('-f', '--fib',
                        action='store',  # tell to store a value
                        dest='FibZone',  # use `FibZone` to access value
                        help='Fib buy zone')
    parser.add_argument('-d', '--distance',
                        action='store',  # tell to store a value
                        dest='distance',  # use `FibZone` to access value
                        help='Distance between Tenkansen & Kijunsen')
    
    
   
    action = parser.parse_args()
    return action
    
    
    



entry = GetEntry() 
pair = MyPair(entry)
pair.SetParams(entry)


while True:  
    pair.Trade()
    time.sleep(10) ## should be enough delay to 






