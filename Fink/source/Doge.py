from bittrex.bittrex import *
import argparse
import statistics 
import os
import MySQLdb
import time
import datetime
from settings import *
from ta import *



    

class MyAccount(object):

    def __init__(self):
        
        self.pid = os.getpid()  ##Get process pid
        print("pid is: %d" % self.pid)

        self.pairName = "BTC-DOGE"
        self.conn = MySQLdb.connect(Fink_DB_HOST,Fink_DB_USER,Fink_DB_PW,Fink_DB_NAME) 
        
        ##get BuyLimit, api key and secret
        cursor = self.conn.cursor()
        query = "SELECT * FROM `Settings` WHERE 1"
    
        try:
            cursor.execute(query)
            data = cursor.fetchone()
            self.api = data[0]
            self.secret = data[1]
            self.BuyLimit = float(data[2])
            self.uid = data[3]
        
        except MySQLdb.Error as error:
            print(error)
            self.conn.close()
            
        self.account = Bittrex(self.api, self.secret, api_version=API_V2_0) ##now connect to bittrex with api and key
        
        ## Initialize Pair Values
            
        cursor = self.conn.cursor()
        query = "UPDATE Pairs SET `IchState`= NULL, PID = %d WHERE Pair='BTC-DOGE'" % (self.pid) ##Null IchState, put in PID and entry pair

        try:
            cursor.execute(query)
            self.conn.commit()
            print("intialized")
    
        except MySQLdb.Error as error:
            print(error)
            self.conn.rollback()
            self.conn.close()
        
        self.DogeOrder = 0
        
            
            
    def GetActivationStatus(self):
        
        ##Check that Activated = 1 on that UID
        
        cursor = self.edel.cursor()
        query = "SELECT Active from `User_List` WHERE UID='%s' " % (self.uid)
        
        try:
            cursor.execute(query)
            data = cursor.fetchone()
            self.activation = data[0]
        
        except MySQLdb.Error as error:
            print(error)
            self.edel.close()
        
       
            
    def GetDogePrice(self): 
        
        while True:
            data = self.account.get_latest_candle(self.pairName, tick_interval=TICKINTERVAL_ONEMIN)
            
            if (data['success'] == True and data['result']):
                result = data['result']
                self.DogePrice = float(result[0]['C'])
                break
            
    def GetDoge(self): 
        
        while True: 
            data = self.account.get_balance("DOGE")
        
            if (data['success'] == True and data['result'] != None):
                result = data['result']
                self.Doge = result['Balance']
                self.DogeBTC = float(self.Doge * self.DogePrice)
                break
            
            
    def GetDogeOrders(self):
        
        data = self.account.get_open_orders("BTC-DOGE")  
        
        if (data['success'] == True):
            order = data['result']
            if (order != []):
                self.OrderID = order[0]['OrderUuid']
                self.OrderPrice = order[0]['Limit']
                
                if (order[0]['OrderType'] == 'LIMIT_BUY'):
                    self.DogeOrder = 2
                elif (order[0]['OrderType'] == 'LIMIT_SELL'):
                    self.DogeOrder = 1
            else:
                self.DogeOrder = 0
                    
                
    
               
                     
    def SellDoge(self):   
        
        amount = float(self.Doge * 0.99)
        
        ##get Price we need to Buy at through the Orderbook
        while True: 
            data = self.account.get_orderbook(self.pairName, depth_type=BOTH_ORDERBOOK)
        
            if (data['success'] == True):
                result = data['result']['sell'] ##buy orders
                if (result[0]['Rate'] >= self.DogePrice):
                    self.SellPrice = result[0]['Rate']
                    break   
        print("selling %s of amount %.9f at %.9f" % ("BTC-DOGE", amount,self.SellPrice))
                
        while True: 
            
            data = self.account.trade_sell("BTC-DOGE", ORDERTYPE_LIMIT, amount, self.SellPrice, TIMEINEFFECT_GOOD_TIL_CANCELLED,CONDITIONTYPE_NONE, target=0.0) ##now placing sell order
                    
            if (data['success'] == True):
                print("Sell Order in place")
                        
            ## logging action
            ts = time.time()
            timestamp = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')
            cursor = self.conn.cursor()
            query = "INSERT INTO `AccountHistory`(`PID`, `Pair`, `Amount`, `Price`, `Action`, `ActionTime`) VALUES (%d,'%s',%d,%.9f,'Sell','%s')" % (self.pid,"BTC-DOGE",amount,self.SellPrice,timestamp)
                        
            try:
                cursor.execute(query)
                self.conn.commit()
        
            except MySQLdb.Error as error:
                print(error)
                self.conn.rollback()
                self.conn.close()
                        
            break
            
       
       
      
    def BuyDoge(self):   
        
        print("buying pair")
        
        ##get BTC Balance

        while True:
            data = self.account.get_balance('BTC')
            
            if (data['success'] == True and data['result'] != None):
                result = data['result']
                self.RemainingBTC = result['Balance']
                break        
        
        ##get Price we need to Buy at through the Orderbook
        while True: 
            data = self.account.get_orderbook(self.pairName, depth_type=BOTH_ORDERBOOK)
        
            if (data['success'] == True):
                result = data['result']['buy'] ##buy orders
                if (result[0]['Rate'] <= self.DogePrice):
                    self.BuyPrice = result[0]['Rate']
                    break              
                    
        ##Amount = BTC Balance * Price
        self.OrderAmount = float(self.RemainingBTC / self.BuyPrice)
        
        print("buying DOGE at amount %.9f for price %.9f" % (self.OrderAmount, self.BuyPrice))
    
       
        while True: 
            
            data = self.account.trade_buy("BTC-DOGE", ORDERTYPE_LIMIT,self.OrderAmount,self.BuyPrice, TIMEINEFFECT_GOOD_TIL_CANCELLED,CONDITIONTYPE_NONE, target=0.0) ##now placing buy order
            
            if (data['success'] == True):
                print("Buy Order in place")
                ## logging action
                ts = time.time()
                timestamp = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')
                cursor = self.conn.cursor()
                query = "INSERT INTO `AccountHistory`(`PID`, `Pair`, `Amount`, `Price`, `Action`, `ActionTime`) VALUES (%d,'%s',%d,%.9f,'Buy','%s')" % (self.pid,"BTC-DOGE",self.OrderAmount,self.BuyPrice,timestamp)

        
                try:
                    cursor.execute(query)
                    self.conn.commit()
                    break
        
                except MySQLdb.Error as error:
                    print(error)
                    self.conn.rollback()
                    self.conn.close()
          
          
    def CheckOrder(self):  
        
        ##IF it is a sell order
        if (self.DogeOrder == 1 and self.OrderPrice > float(1.02 * self.DogePrice)): ##Doge Price has gone down by 4% 
            print("Sell Order needs to be readjusted")
            data = self.account.cancel(self.OrderID) ##Cancel that Sell Price
            self.SellDoge()  ##this will readjust price order
            print("re-adjusted Sell Order")
            
        ##IF it is a buy order
        elif (self.DogeOrder == 2 and ((self.OrderPrice < float(0.98 * self.DogePrice)): ##Doge Price has gone down by 4% 
            print("Buy Order needs to be readjusted")
            data = self.account.cancel(self.OrderID) ##Cancel that Sell Price
            self.BuyDoge()  ##this will readjust price order
            print("re-adjusted Buy Order")
        else:
            print("All orders check out okay")
    
                
        
##program start here

account = MyAccount()


while True:  

    account.GetDogePrice();  ##get Current Price
    account.GetDoge();       ##get DOGE amount
    account.GetDogeOrders(); ##discover if there is any orders for DOGE
    
    print ("DOGE is now at: %.9f") % (account.DogePrice)    
    print ("Amount of Doge Held: %.9f or %.9f") % (account.Doge,account.DogeBTC)

    if (account.DogeOrder == 0):       ##No Orders detected
        
        print ("No order will be placed, putting order in now")

        if (account.DogeBTC < 0.01):   ##No DOGE
          account.BuyDoge()            ##buy Doge
        elif (account.DogeBTC > 0.01): ##There's DOGE 
          account.SellDoge()           ##sell Doge
          
    elif (account.DogeOrder == 1):
        print ("A sell order has been placed with UUid: %s at price: %.9f") % (account.OrderID, account.OrderPrice)
        print ("checking on that sell order")  
        account.CheckOrder()
    elif (account.DogeOrder == 2):
        print ("A buy order has been placed with UUid: %s at price: %.9f") % (account.OrderID, account.OrderPrice)
        print ("checking on that buy order")  
        account.CheckOrder()
  

    ##pair.GetActivationStatus() 
    ##if (pair.activation == 0):
    ##    print("sorry you're agent system is not activated, please activate it !")
    ##    break
    
    
    time.sleep(10) ## enoguh delay for an order to be complete







