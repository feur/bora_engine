from bittrex.bittrex import *
import argparse
from statistics import mean
import os
import time
import MySQLdb
import subprocess
from settings import *


    
 
 
 
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
        
        self.account = Bittrex("f5d8f6b8b21c44548d2799044d3105f0", "b3845ea35176403bb530a31fd4481165", api_version=API_V2_0) ##connect to bittrex account
            
    def BuyPair(self, pair):   
        
        ##get pair and amount to sell
        ##check orderbook and complete sell order 
        
        while True:
            data = self.account.get_latest_candle(pair, tick_interval=TICKINTERVAL_ONEMIN)
            
            if (data['success'] == True and data['result']):
                result = data['result']
                amount = result[0]['C']
                break
        
        print("selling %s at amount %.9f" % (pair, amount))
        
        while True:
            data = self.account.get_orderbook(pair, depth_type=BOTH_ORDERBOOK)
            
            if (data['success'] == True):
                result = data['result']['buy']
                BuyPrice = float(result[1]['Rate'])
                print("buying %d at %.9f" % (amount, Buy))
                
                data = self.account.buy_limit(pair, amount, BuyPrice) ##now placing sell order
                if (data['success'] == True):
                    print("Buy Order in place")
                    break
            
            
            
    def GetBTCAvailable(self):
    
    #First get available BTC
        while True:
            data = self.account.get_balance('BTC')
            
            if (data['success'] == True):
                result = data['result']
                self.BTCAvailable = float(result['Balance'])
                break
        
        print("BTC balance: %.9f" % self.BTCAvailable)
            
 
    
        
        
    
"""
1. If BTC Balance >= 0.05 BTC
2. Sort out Pairs ordered by Rating 
3. If Pairs - HoldBTC < 0.01 then 
    - Buy order for 0.05 BTC 
    - Otherwise go to the next BTC 
"""


##program start here

pid = os.getpid()  ##Get process pid
ListofPairs = []   ##list of Pairs, e.g. BTC-ADA, ETH-ADA
ListofCurrencies= [] ##list of Currencies e.g. ADA, OMG

print("pid is: %d" % pid)

conn = MySQLdb.connect(DB_HOST,DB_USER,DB_PW,DB_NAME)

cursor = conn.cursor()

PersonalAccount = Account()


##insert PID into Database
query = "UPDATE `Components` SET `PID`=%d WHERE Unit='buyer'" % (pid)

try:
    cursor.execute (query)
    conn.commit()
    
except MySQLdb.Error as error:
    print(error)
    conn.rollback()
    conn.close()
     
    
    
    


while True:
    
    ## Check BTC Balance 
    PersonalAccount.GetBTCAvailable()
    if (PersonalAccount.BTCAvailable >= 0.25):
        
        try:
            cursor.execute ("SELECT Pair, TradeSignal, Hold, HoldBTC FROM `Pairs` ORDER BY Rating DESC") ##getting a list of Pairs ordered by their rating and signal to work out which one to buy 
            data = cursor.fetchall() 
    
            ##now filter out the list
            for i in range(len(data)):
                print("Pair %s has a signal of %d" % (str(data[i][0]), data[i][1]))
                if data[i][1] == 4  and float(data[i][3]) < 0.01 and PersonalAccount.BTCAvailable >= 0.25 : ##buy signal and nothing has been bought in yet and theres enough balance still
                    PersonalAccount.BuyPair(str(data[i][0]))  #buy pair
                    PersonalAccount.BTCAvailable = PersonalAccount.BTCAvailable - 0.25
                else:
                    print("Nothing to buy")
        
        except MySQLdb.Error as error:
            print(error)
            conn.close()
    else:
        print ("not enough balance")
    

    time.sleep(60)


