from bittrex.bittrex import *
import argparse
import statistics 
import os
import MySQLdb
import time
import datetime
from settings import *
from ta import *



def GetEntry():
    parser = argparse.ArgumentParser(description='Process TA for pair')
    parser.add_argument('-p', '--pair',
                        action='store',  # tell to store a value
                        dest='pair',  # use `paor` to access value
                        help='The Pair to be watched')
   
    pair = parser.parse_args()
    return pair
    
    
    

class MyPair(object):

    def __init__(self,entry):
        
        self.pid = os.getpid()  ##Get process pid
        print("pid is: %d" % self.pid)

        self.TimeInterval = "FIVEMIN"
        self.pairName = entry.pair
        self.conn = MySQLdb.connect(Fink_DB_HOST,Fink_DB_USER,Fink_DB_PW,Fink_DB_NAME) 
        self.edel = MySQLdb.connect(Edel_DB_HOST,Edel_DB_USER,Edel_DB_PW,Edel_DB_NAME) ##connect to edel DB
        
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
        
        ## Initialize Pair Values
            
        cursor = self.conn.cursor()
        query = "UPDATE Pairs SET `IchState`= NULL, PID = %d WHERE Pair='%s'" % (self.pid,entry.pair) ##Null IchState, put in PID and entry pair

        try:
            cursor.execute(query)
            self.conn.commit()
            print("intialized")
    
        except MySQLdb.Error as error:
            print(error)
            self.conn.rollback()
            self.conn.close()
            
        
    def GetWatchSignal(self):
        
        cursor = self.edel.cursor()
        query = "SELECT Watch, Currency from `Pair_List` WHERE Pair='%s' " % (self.pairName)
        
        try:
            cursor.execute(query)
            data = cursor.fetchone()
            self.currency = data[1]
            self.watch = data[0]
        
        except MySQLdb.Error as error:
            print(error)
            self.edel.close()
            
            
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
        
       
            
    def GetData(self): 
        
        self.EMA = [0,0,0,0]  ##55,21,13,8
        
        while True: 
            self.account = Bittrex(self.api,self.secret, api_version=API_V2_0)
            data = self.account.get_candles(self.pairName, tick_interval=TICKINTERVAL_FIVEMIN)
        
            if (data['success'] == True and data['result']):
                self.data = data['result']
                self.current = self.data[-1]
                self.entry = entry
                break
            
            
    def GetBalance(self): 
        
        while True: 
            data = self.account.get_balance(self.currency)
        
            if (data['success'] == True and data['result'] != None):
                result = data['result']
                self.balance = result['Balance']
                self.balanceBTC = float(self.balance * self.current)
                print("Balance is: %.9f or %.9f BTC") % (self.balance, self.balanceBTC)
                break
        
          
          
    def GetOrder(self):
        
        data = self.account.get_open_orders(self.pairName)  
        
        if (data['success'] == True):
            order = data['result']
            if (order != []):
                self.OrderID = order[0]['OrderUuid']
                self.OrderPrice = order[0]['Limit']
                
                if (order[0]['OrderType'] == 'LIMIT_BUY'):
                    self.Order = 2
                elif (order[0]['OrderType'] == 'LIMIT_SELL'):
                    self.Order = 1
            else:
                self.Order = 0

            
            
    def UpdateOrder(self):
        
        '''
        if order is sell: 
            - Sell must be tenkanSen
            - Buy must be  kijunSen
        '''        
        if (self.Order == 2 and self.OrderPrice < float(self.kijunSen[0] * 0.992)):
            data = self.account.cancel(self.OrderID) ##Cancel that Buy Price
            print("updating buy Order!")
            self.BuyPair()
        elif (self.Order == 1 and self.OrderPrice < float(self.tenkanSen[0] * 0.992)):
            data = self.account.cancel(self.OrderID) ##Cancel that Sell Price
            print("updating sell Order!")
            self.SellPair()
        else:
            print("All Orders are okay!")
                    
 
    def GetTrend(self):
        
        
        ###Get EMA Trend first
        
        self.EMA[0] = GetEMA(self.data, 55, self.EMA[0])  ##Get EMA55
        self.EMA[1] = GetEMA(self.data, 21, self.EMA[1])  ##Get EMA21
        self.EMA[2] = GetEMA(self.data, 13, self.EMA[2]) ##Get EMA13
        self.EMA[3] = GetEMA(self.data, 8, self.EMA[3]) ##Get EMA8
        
        print("EMA55 is (%.9f) EMA21 is (%.9f) EMA13 is (%.9f) EMA8 (%.9f)" % (self.EMA[0], self.EMA[1], self.EMA[2], self.EMA[3]))        
        
        if (self.EMA[0] == max(self.EMA)):  ##work out if EMA55 is on top 
            self.EMATrend = 0
        else:
            self.EMATrend = 1 
            
        print("EMA Trend is: %d" % self.EMATrend)
        

        
      

    def GetActive(self):
        
        '''
        Get Ichimoku elements:
        - Tenkansen
        - Kijusen
        - Cloud 
        - Lagging
        
        A signal is when there is a Ichimoku Crossover  
        The type of signal (buy or sell) is determined by:
        - The order of the Tenkansen or Kijusen 
        - The order of the EMAs (55 dominant or not)
        
        When a signal is detected and defined, a buy or sell order is actioned

        '''
        
        high=[]
        low=[]
        highest=[]
        lowest=[]
        
        self.tenkanSen = []
        self.kijunSen = []
        self.senkouB = []
        self.senkouA = []
        
        for item in self.data:
            high.append(item['H'])
            low.append(item['L'])
            
     
        y = len(self.data)
        
        period = 2
        
        for x in range (y/period):  
            
            for z in range(y - (x+1)*period, y-(period*x + 1)):
                highest.append(high[z])
                lowest.append(low[z])
                
            self.tenkanSen.append((max(highest) + min(lowest))/2) 
            highest *= 0
            lowest *= 0
                    
         
        period = 8
        
        for x in range (y/period):  
            
            for z in range(y - (x+1)*period, y-(period*x + 1)):
                highest.append(high[z])
                lowest.append(low[z])
                
            self.kijunSen.append((max(highest) + min(lowest))/2) 
            highest *= 0
            lowest *= 0
                    
       
        period = 16
        
        for x in range (y/period):  
            
            for z in range(y - (x+1)*period, y-(period*x + 1)):
                highest.append(high[z])
                lowest.append(low[z])
                
            self.senkouB.append((max(highest) + min(lowest))/2) 
            highest *= 0
            lowest *= 0
            
            
        period = 8
        
        for x in range(period-1):
            self.senkouA.append((self.tenkanSen[x] + self.kijunSen[x])/ 2)
            
            
        print("red at: %.9f" % self.tenkanSen[0])  
        print("blue at: %.9f" % self.kijunSen[0])  
            
        #find state of Tenkansen & Kijunsen as IchState
        if (self.tenkanSen[0] > self.kijunSen[0]): ##red on top of blue
            self.IchState = 1
        else:
            self.IchState = 0
    
        if (self.IchState == 1 and self.EMATrend == 1):
            self.active = 1
            print ("Pair is active")
        else:
            print ("Pair is not active")
            self.active = 0
        
                
      
    def UploadData(self):

        cursor = self.conn.cursor()
        query = "UPDATE Pairs SET TradeSignal = %d, PID = %d WHERE Pair = '%s'" % (self.active,self.pid,self.pairName)

        try:
            cursor.execute(query)
            self.conn.commit()
        
        except MySQLdb.Error as error:
            print(error)
            self.conn.rollback()
            self.conn.close()
            
            
    
    
    def BuyPair(self):   
        
        '''
        When a buy signal is identified, a buy order is to be made
        The price of which to be sold is determined by the tenkanSen line (no need to go via order book)  
        This reduces the risk of buy at a too high price to avoid lossess when selling 
        '''    
        
        print("buying pair")
        
    
        ##Buy Price is at blue line
        self.OrderAmount = float(self.BuyLimit/ self.kijunSen[0])
        
        print("buying %s at amount %.9f for price %.9f" % (self.pairName,self.OrderAmount, self.kijunSen[0]))
    
       
        while True: 
            
            data = self.account.trade_buy(self.pairName, ORDERTYPE_LIMIT,self.OrderAmount,self.kijunSen[0], TIMEINEFFECT_GOOD_TIL_CANCELLED,CONDITIONTYPE_NONE, target=0.0) ##now placing buy order
            
            if (data['success'] == True):
                print("Buy Order in place")
                ## logging action
                ts = time.time()
                timestamp = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')
                cursor = self.conn.cursor()
                query = "INSERT INTO `AccountHistory`(`PID`, `Pair`, `Amount`, `Price`, `Action`, `ActionTime`) VALUES (%d,'%s',%d,%.9f,'Buy','%s')" % (self.pid,self.pairName,self.OrderAmount,self.kijunSen[0],timestamp)

        
                try:
                    cursor.execute(query)
                    self.conn.commit()
                    break
        
                except MySQLdb.Error as error:
                    print(error)
                    self.conn.rollback()
                    self.conn.close()
        
        
                        
                    
    def SellPair(self):   
        
        '''
        When a SELL signal is identified, a sell order is to be made
        The price of which to be sold is determined by the kijunSen line (no need to go via order book)  
        This reduces the risk of selling at a lower price then originally bought even on a downtrend 
        '''        
        ##get pair and amount to sell
        
        amount = float(self.balance * 0.995)
        print("selling %s of amount %.9f at %.9f" % (self.pairName, amount, self.tenkanSen[0]))
                
        while True: 
            
            data = self.account.trade_sell(self.pairName, ORDERTYPE_LIMIT, amount, self.tenkanSen[0], TIMEINEFFECT_GOOD_TIL_CANCELLED,CONDITIONTYPE_NONE, target=0.0) ##now placing sell order
                    
            if (data['success'] == True):
                print("Sell Order in place")
                        
            ## logging action
            ts = time.time()
            timestamp = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')
            cursor = self.conn.cursor()
            query = "INSERT INTO `AccountHistory`(`PID`, `Pair`, `Amount`, `Price`, `Action`, `ActionTime`) VALUES (%d,'%s',%d,%.9f,'Sell','%s')" % (self.pid,self.pairName,amount,self.tenkanSen[0],timestamp)
                        
            try:
                cursor.execute(query)
                self.conn.commit()
        
            except MySQLdb.Error as error:
                print(error)
                self.conn.rollback()
                self.conn.close()
                        
            break
            
        
         
    def GetBuyPosition(self):
        
        ## determine whether it should be bought despite the signal
        ## Check if theres enough balance in the first place
        ## Go through all the pairs ordered by rating
        ## 1. is it of the highest rating? if so yes its in a buy position
        ## 2. Is the Pair with the highest rating allready holding something? Yes go to the next one and ask the same question
        ## 2.a. If no then not in a buying position
        ## 3. Are we now on the same rating? Okay we're in buy position 
        
      
        ## Check BTC Balance 
        while True:
            data = self.account.get_balance('BTC')
            
            if (data['success'] == True):
                result = data['result']
                self.BTCBalance = float(result['Balance'])
                break
            
        ##check total BTC in order 
        TotalBTCInOrder = 0    
        
        
        ##get a list of pairs (because we can't for some fucking reason just get open orders for everything)
        
        ListofPairs = []   ##list of Pairs, e.g. BTC-ADA, ETH-ADA
        ListofCurrencies= [] ##list of Currencies e.g. ADA, OMG
        
        cursor = self.conn.cursor()
        
        try:
            cursor.execute ("SELECT `Pair`, `Currency` FROM `Pairs` WHERE 1")
            data = cursor.fetchall()
            
            for i in range(len(data)):
                ListofPairs.append(str(data[i][0]))
                ListofCurrencies.append(str(data[i][1]))
                
        except MySQLdb.Error as error:
            print(error)
            self.conn.close()
        
        for i in range(len(ListofPairs)):    
            while True:    
                data = self.account.get_open_orders(ListofPairs[i])  
                print(data)
                if (data['success'] == True):
                    print("getting order books")
                    self.OrderBook = data['result']
                    for i in range(len(self.OrderBook)):
                 
                        if (self.OrderBook[i]['OrderType'] == 'LIMIT_BUY'):  ##only count unfinished buy orders
                            TotalBTCInOrder += float(float(self.OrderBook[i]['Quantity']) * float(float(self.OrderBook[i]['Limit'])))
                            print("Total BTC in order is: %.9f" % TotalBTCInOrder)
                    
                        if (self.OrderBook[i]['OrderType'] == 'LIMIT_SELL'):  ##coin is allready on sell but unfinished
                            self.BTCBalance = 0
                        
                    break
                    

        self.BTCAvailable = self.BTCBalance - TotalBTCInOrder #this is to prevent multiple orders made on several coin that exceed actual balance
             
        print("BTC balance: %.9f" % self.BTCAvailable)
        
        if (self.BTCAvailable >= self.BuyLimit):
            self.BuyPosition = 1
        else:
            self.BuyPosition = 0
        
   
    
            
                
                      
                
    
##program start here

entry = GetEntry() ##Get arguments to define Pair and Fib levels
pair = MyPair(entry)


while True:  ##Forever loop 

    ##get Data

    pair.GetWatchSignal()

    if (pair.watch):
        print("this pair needs to be watched")
    
    pair.GetData()
    print("current price is: %.9f" % pair.current['C'])    
    
    
    pair.GetActivationStatus()   
    if (pair.activation == 0):
        print("sorry your agent system is not activated, please activate it !")
        break
    
    
    pair.GetTrend()
    pair.GetActive()
    
    pair.GetBalance() 
    pair.GetOrder()
    
    if (pair.Order > 0):
        pair.UpdateOrder()
    else:
        if (pair.active == 1 and pair.Balance < 0.01 and pair.watch == 1): ##No balance 
            pair.BuyPair() ##put in a buy order
        elif (pair.Balance > 0.01): ##there is balance
            pair.SellPair() ##put in sell orders
    
            
    pair.UploadData()  
    time.sleep(10) ## enoguh delay for an order to be complete







