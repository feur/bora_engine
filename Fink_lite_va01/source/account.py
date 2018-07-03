from bittrex.bittrex import *
import argparse
import os
import time
import datetime
import MySQLdb
from settings import *


def GetEntry():
    parser = argparse.ArgumentParser(description='Get Account info')
    parser.add_argument('-k', '--key',
                        action='store',  # tell to store a value
                        dest='api',  # use `paor` to access value
                        help='Your API Key')
    parser.add_argument('-s', '--secret',
                        action='store',  # tell to store a value
                        dest='secret',  # use `paor` to access value
                        help='Your API Secret')
    
    action = parser.parse_args()
    return action


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

        
        self.TotalBTC = 0
        self.BTC = 0
        self.BTCPrice = 0
        self.TotalUSD = 0
            
            
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
            
            
            
     
        
            
            

##program start here
                

entry = GetEntry() ##Get params
PersonalAccount = Account(entry)


while True:
    
    print("*******************************************************************")
    print("getting balances")
    print("___________________________________________________________________")
    PersonalAccount.GetTotalBalance()
    print(" ")
    print("Total Account: %.9f BTC / $ %.9f USD") % (PersonalAccount.TotalBTC, PersonalAccount.TotalUSD)
    print("___________________________________________________________________")
    
    
    PersonalAccount.TotalBTC = 0
    PersonalAccount.TotalUSD = 0

    
    time.sleep(60)
