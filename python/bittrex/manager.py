from bittrex.bittrex import *
import argparse
from statistics import mean
import os
import time
import MySQLdb
import subprocess
import psutil
from settings import *



class Account(object): 
    
    def __init__(self):
        
            self.account = Bittrex("f5d8f6b8b21c44548d2799044d3105f0", "b3845ea35176403bb530a31fd4481165", api_version=API_V2_0)
           
            
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
    
        print("watching Currency: %s for pair: %s " % (currency,pair))    
        
        while True:
            data = self.account.get_balance(currency)
            
            if (data['success'] == True and data['result'] != None):
                result = data['result']
                holding = result['Balance']
                break
            
        
        #convert the holdings into BTC
        while True:
            data = self.account.get_latest_candle(pair, tick_interval=TICKINTERVAL_ONEMIN)
            
            if (data['success'] == True and data['result'] != None):
                result = data['result']
                print(result)
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
            
            if (data['success'] == True and data['result'] != None):
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
        
        
    def CheckProcess(self,pair,conn):
        
        cursor = conn.cursor()
        query = "SELECT PID from Pairs WHERE Pair = '%s'" % (pair)
        
        try:
            
            cursor.execute (query)
            data = cursor.fetchone() #find PID for PAIR
            
            #check if pid is running
            if psutil.pid_exists(data[0]):
                print("process watching %s is still running with pid %d" % (pair, data[0]))
            else:
                print("re-running process for this signal %s" % (pair))
                process = subprocess.call("python ~/bora_local/python/bittrex/watch.py " + "-p " + pair + " > /dev/null 2>&1 & ",  shell=True)
         
            
        except MySQLdb.Error as error:
            print(error)
            conn.close()
            
       
                

    
##program start here

#entry = GetEntry() ##Get arguments to define Pair and Fib levels
pid = os.getpid()  ##Get process pid
ListofPairs = []   ##list of Pairs, e.g. BTC-ADA, ETH-ADA
ListofCurrencies= [] ##list of Currencies e.g. ADA, OMG

print("pid is: %d" % pid)

conn = MySQLdb.connect(DB_HOST,DB_USER,DB_PW,DB_NAME)

cursor = conn.cursor()

PersonalAccount = Account()


            
try:
    cursor.execute ("SELECT * from Config")
    data = cursor.fetchall()
    
    
    for i in range(len(data)):
        #print("watching %s " % str(data[i][0]))
        ListofPairs.append(str(data[i][0]))
        ListofCurrencies.append(str(data[i][7]))
       
    
    
except MySQLdb.Error as error:
    print(error)
    conn.close()
    

#while True: 
    #print("balance is: ")

while True:
    
    time.sleep(60)
    
    print("getting balances")
    
    for i in range(len(ListofPairs)):
        PersonalAccount.GetCurrencyBalance(ListofCurrencies[i], ListofPairs[i], conn)
        ##check for process if its still running 
        PersonalAccount.CheckProcess(ListofPairs[i],conn)
    
    PersonalAccount.GetTotalBalance();   

   

