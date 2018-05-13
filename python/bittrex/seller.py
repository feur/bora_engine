from bittrex.bittrex import *
import argparse
from statistics import mean
import os
import time
import MySQLdb
import subprocess
from settings import *



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
    
 
 
 
"""
Simple Logic: 

1. Sort out the Pairs table by Signal
2. Filter out: 
 - If Pair has signal of 0, check Holding
     - If holding > 0.01 BTC set sell order 
         - Keep checking sell order until complete
    - else If holding < 0.01 BTC thenno sell order
 - If Pair has signal of > 0 then stop 
"""

 
class Account(object): 
    
    def __init__(self):
        
        self.account = Bittrex("f5d8f6b8b21c44548d2799044d3105f0", "b3845ea35176403bb530a31fd4481165", api_version=API_V2_0)
            
    def SellPair(self, pair, amount):   
        
        ##get pair and amount to sell
        ##check orderbook and complete sell order 
        
        print("selling %s at amount %.9f" % (pair, amount))
        
        while True:
            data = self.account.get_orderbook(pair, depth_type=BOTH_ORDERBOOK)
            
            if (data['success'] == True):
                result = data['result']['buy']
                SellPrice = float(result[1]['Rate'])
                print("selling %d at %.9f" % (amount, SellPrice))
                
                data = self.account.trade_sell(pair, ORDERTYPE_LIMIT, amount, SellPrice, TIMEINEFFECT_GOOD_TIL_CANCELLED,CONDITIONTYPE_NONE, target=0.0) ##now placing sell order
                if (data['success'] == True):
                    print("Sell Order in place")
                    break
                
        
            
    def GetBTCAvailable(self):
    
    #First get available BTC
        while True:
            data = self.account.get_balance('BTC')
            
            if (data['success'] == True):
                result = data['result']
                self.BTCAvailable = result['Balance']
                break
            
    def GetCurrencyBalance(self, currency, pair, conn):
        
        """
        {'success': True,
             'message': '',
             'result': {'Currency': '1ST',
                        'Balance': 10.0,
                        'Available': 10.0,
                        'Pending': 0.0,
                        'CryptoAddress': None}
            }     
            
        """
        ##Get Holdings
        while True:
            data = self.account.get_balance(currency)
            
            if (data['success'] == True):
                result = data['result']
                holding = result['Balance']
                break
            
        
        #convert the holdings into BTC
        while True:
            data = self.account.get_latest_candle(pair, tick_interval=TICKINTERVAL_ONEMIN)
            
            if (data['success'] == True and data['result']):
                result = data['result']
                holdingBTC = holding * result[0]['C']
                break

        
        print("balance for %s is: %.9f in btc %.9f" % (currency,holding,holdingBTC))
        
        
        #now insert the holdings into the database
        cursor = conn.cursor()
        query = "UPDATE Pairs SET Hold='%.9f', HoldBTC='%.9f' WHERE Pair = '%s'" % (holding,holdingBTC,pair)
    
        try:
            cursor.execute(query)
            conn.commit()
        
        except MySQLdb.Error as error:
            print(error)
            conn.rollback()
            
       
            
    def GetTotalBalance(self):
        
        #First get BTC holdings
        while True:
            data = self.account.get_balance('BTC')
            
            if (data['success'] == True):
                result = data['result']
                self.RemainingBTC = result['Balance']
                break
            
        #Get sum of BTCHolding column
        try:
            cursor.execute ("SELECT SUM(HoldBTC) from Pairs")
            Sum = cursor.fetchone()
            
        
        except MySQLdb.Error as error:
            print(error)
            conn.close()
    
        self.TotalBTCBalance = float(Sum[0]) + self.RemainingBTC
        print("Total BTC is: %.9f" % self.TotalBTCBalance)
        
        
    
    


##program start here

#entry = GetEntry() ##Get arguments to define Pair and Fib levels
pid = os.getpid()  ##Get process pid
ListofPairs = []   ##list of Pairs, e.g. BTC-ADA, ETH-ADA
ListofCurrencies= [] ##list of Currencies e.g. ADA, OMG

print("pid is: %d" % pid)

conn = MySQLdb.connect(DB_HOST,DB_USER,DB_PW,DB_NAME)

cursor = conn.cursor()

PersonalAccount = Account()



##insert PID into Database
query = "UPDATE `Components` SET `PID`=%d WHERE Unit='seller'" % (pid)

try:
    cursor.execute (query)
    conn.commit()
    
except MySQLdb.Error as error:
    print(error)
    conn.rollback()
    conn.close()
     
    
    
     
    


    
while True:
    
    try:
        cursor.execute ("SELECT Pair, TradeSignal, Hold, HoldBTC FROM `Pairs` ORDER BY TradeSignal ASC") ##getting a list of Pairs ordered by their signals to work out which one to sell 
        data = cursor.fetchall() 
    
        ##now filter out the list
        for i in range(len(data)):
            print("Pair %s has a signal of %d" % (str(data[i][0]), data[i][1]))
            if (data[i][1] <= 2 and data[i][1] != 0 and float(data[i][3]) > 0.01) : ##weakr or strong sell signal and has enough to sell 
                PersonalAccount.SellPair(str(data[i][0]), float(data[i][2])) 
               
        
        
    except MySQLdb.Error as error:
        print(error)
        conn.close()
    

    time.sleep(60)


