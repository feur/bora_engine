from bittrex.bittrex import *
import argparse
import os
import time
import datetime
import MySQLdb
from settings import *



class Account(object): 
    
    def __init__(self, entry):
        
        self.pid = os.getpid()  ##Get process pid
        print("pid is: %d" % self.pid)
        
        if (entry.api != None and entry.secret != None):
            self.api = entry.api
            self.secret = entry.secret
        else:
            print("Please insert api & secret key")
            quit()
        
        self.account = Bittrex(self.api, self.secret, api_version=API_V2_0) ##now connect to bittrex with api and key

        self.conn = MySQLdb.connect(Fink_DB_HOST,Fink_DB_USER,Fink_DB_PW,Fink_DB_NAME)
        
        self.TotalBTC = 0
        self.BTC = 0
        self.BTCPrice = 0
        self.TotalUSD = 0
        
           ## Insert PID
        cursor = self.conn.cursor()
        query = "UPDATE Components SET PID = %d WHERE Unit='account'" % (self.pid) ##Null IchState, put in PID and entry pair

        try:
            cursor.execute(query)
            self.conn.commit()
            print("intialized")
    
        except MySQLdb.Error as error:
            print(error)
            self.conn.rollback()
            self.conn.close()
            
            
    def GetTotalBalance(self):
        
        
        while True:
            data = self.account.get_latest_candle("USDT-BTC", tick_interval=TICKINTERVAL_ONEMIN)
            
            if (data['success'] == True and data['result'] != None):
                result = data['result']
                self.BTCPrice = result[0]['C']
            break
    
        print(" ")
        print("BTC Price : %.9f") % self.BTCPrice
        print(" ")
        
        #First get BTC holdings
        while True:
            data = self.account.get_balances()
            
            if (data['success'] == True and data['result'] != None):
                result = data['result']
                
                #print(result)
                
                for i in result:
                
                    if (i['BitcoinMarket'] != None):    
                        currency = i['Currency']['Currency']
                        balance = float(i['Balance']['Balance']) + float(i['Balance']['Pending'])
                        price = i['BitcoinMarket']['Last']
                        balanceBTC = float(price * balance)
                        balanceUSDT = float(balanceBTC * self.BTCPrice)
                
                        if (balanceUSDT > 0):
                            print("Pair %s :         %.9f / %.9f BTC / $ %.9f USD") % (currency,balance,balanceBTC,balanceUSDT)
                            self.TotalBTC += balanceBTC
                            self.TotalUSD += balanceUSDT
                break
            
        ##Then get BTC 
        while True:
             data = self.account.get_balance('BTC')
             
             if (data['success'] == True and data['result'] != None):
                 result = data['result']
                 balanceBTC = result['Balance']
                 balanceUSDT = float(balanceBTC * self.BTCPrice)
                 
                 if (balanceUSDT > 0):
                     print(" ")
                     print("BTC Availbale:         %.9f BTC / $ %.9f USD") % (balanceBTC,balanceUSDT)
                     print(" ")
                     self.TotalBTC += balanceBTC
                     self.TotalUSD += balanceUSDT
             break
            
            
            
     
            
    def LogAccountBalance(self):
        
        print(" ")
        print("logging account now..")
        
        ts = time.time()
        timestamp = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')
        
        cursor = self.conn.cursor()
        query = "INSERT INTO `AccountBalance`(`PID`, `BTC`, `USD`, `DateTime`) VALUES (%d,%.9f,%.9f,'%s')" % (self.pid,self.TotalBTC,self.TotalUSD,timestamp)

        try:
            cursor.execute(query)
            self.conn.commit()
            
        except MySQLdb.Error as error:
            print(error)
            self.conn.rollback()
            self.conn.close()
            
        print("Done")
        
            

