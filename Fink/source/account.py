from bittrex.bittrex import *
import argparse
from statistics import mean
import os
import time
import datetime
import MySQLdb
import subprocess
import psutil
from settings import *



class Account(object): 
    
    def __init__(self):
    ###Get API and secret first 
        self.conn = MySQLdb.connect(Fink_DB_HOST,Fink_DB_USER,Fink_DB_PW,Fink_DB_NAME)
        cursor = self.conn.cursor() 
        
        try:
            cursor.execute ("SELECT `API_Key`,`API_Secret` FROM `Settings` WHERE 1 ")
            data = cursor.fetchone()
            self.api = data[0]
            self.key = data[1]
            
        except MySQLdb.Error as error:
           print(error)
           self.conn.close()
        
        
        self.account = Bittrex(self.api, self.key, api_version=API_V2_0) ##now connect to bittrex with api and key
            

    def GetCurrencyBalance(self, currency, pair):
        
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
    
        data = self.account.get_balance(currency)
        
        if (data['success'] == True and data['result'] != None):
            result = data['result']
            holding = result['Balance']
            
            #convert the holdings into BTC
            while True:
                data = self.account.get_latest_candle(pair, tick_interval=TICKINTERVAL_ONEMIN)
                if (data['success'] == True):
                    result = data['result']
                    if (result[0]['C'] != None):
                        holdingBTC = holding * result[0]['C']
                        break
        else:
            holding = 0
            holdingBTC = 0

        
        print("balance for %s is: %.9f in btc %.9f" % (currency,holding,holdingBTC))
        
        
        #now insert the holdings into the database
        cursor = self.conn.cursor()
        query = "UPDATE Pairs SET Hold='%.9f', HoldBTC='%.9f' WHERE Pair = '%s'" % (holding,holdingBTC,pair)
    
        try:
            cursor.execute(query)
            self.conn.commit()
        
        except MySQLdb.Error as error:
            print(error)
            self.conn.rollback()
            
       
            
    def GetTotalBalance(self):
        
        #First get BTC holdings
        while True:
            data = self.account.get_balance('BTC')
            
            if (data['success'] == True and data['result'] != None):
                result = data['result']
                self.RemainingBTC = result['Balance']
                break
            
        #Get sum of BTCHolding column
            
        cursor = self.conn.cursor() 
        
        try:
            cursor.execute ("SELECT SUM(HoldBTC) from Pairs")
            Sum = cursor.fetchone()
            
        
        except MySQLdb.Error as error:
            print(error)
            self.conn.close()
    
        self.TotalBTCBalance = float(Sum[0]) + self.RemainingBTC
        print("Total BTC is: %.9f" % self.TotalBTCBalance)
        
            
    def LogAccountBalance(self,pid):
        
        print("logging account now..")
        
        ##get Balance in USD
        while True:
            data = self.account.get_latest_candle("USDT-BTC", tick_interval=TICKINTERVAL_ONEMIN)
            
            if (data['success'] == True and data['result'] != None):
                result = data['result']
                self.TotalUSDBalance = self.TotalBTCBalance * result[0]['C']
            break
        
        
        ts = time.time()
        timestamp = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')
        
        cursor = self.conn.cursor()
        query = "INSERT INTO `AccountBalance`(`PID`, `BTC`, `USD`, `DateTime`) VALUES (%d,%.9f,%.9f,'%s')" % (pid,self.TotalBTCBalance,self.TotalUSDBalance,timestamp)

        try:
            cursor.execute(query)
            self.conn.commit()
            
        except MySQLdb.Error as error:
            print(error)
            self.conn.rollback()
            self.conn.close()
     
   

                
##program start here

#entry = GetEntry() ##Get arguments to define Pair and Fib levels
pid = os.getpid()  ##Get process pid
ListofPairs = []   ##list of Pairs, e.g. BTC-ADA, ETH-ADA
ListofCurrencies= [] ##list of Currencies e.g. ADA, OMG

print("pid is: %d" % pid)


PersonalAccount = Account()


##insert PID into Database
cursor = PersonalAccount.conn.cursor()
query = "UPDATE `Components` SET `PID`=%d WHERE Unit='manager'" % (pid)

try:
    cursor.execute (query)
    PersonalAccount.conn.commit()
    
except MySQLdb.Error as error:
    print(error)
    PersonalAccount.conn.rollback()
    PersonalAccount.conn.close()
     

##get a list of all Pairs in database    

try:
    cursor.execute ("SELECT `Pair`, `Currency` FROM `Pairs` WHERE 1")
    data = cursor.fetchall()
    
    
    for i in range(len(data)):
        ListofPairs.append(str(data[i][0]))
        ListofCurrencies.append(str(data[i][1]))
          
except MySQLdb.Error as error:
    print(error)
    PersonalAccount.conn.close()
    

#while True: 
    #print("balance is: ")

while True:
     
    print("getting balances")

    for i in range(len(ListofPairs)):
        PersonalAccount.GetCurrencyBalance(ListofCurrencies[i], ListofPairs[i])
    
    PersonalAccount.GetTotalBalance()
    PersonalAccount.LogAccountBalance(pid)
    
    time.sleep(60)

  
