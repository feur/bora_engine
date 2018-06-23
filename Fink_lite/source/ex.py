from bittrex.bittrex import *
import argparse
import statistics 
import os
import MySQLdb
import time
import datetime
from settings import *
from ta import *



class MyPair(object):

    def __init__(self):
        
        self.pid = os.getpid()  ##Get process pid
        print("pid is: %d" % self.pid)

        self.TimeInterval = "FIVEMIN"
        
        self.conn = MySQLdb.connect(Fink_DB_HOST,Fink_DB_USER,Fink_DB_PW,Fink_DB_NAME) 
       
        self.BuyLimit = 0.012
        self.BuyBuffer = 0.95
        self.SellBufferH = 1.1
        self.SellBufferL = 1.03

             
            
    def GetData(self,pair,currency): 
        
        self.EMA = [0,0,0,0]  ##55,21,13,8
        self.pairName = pair
        self.currency = currency
        
        while True: 
            self.account = Bittrex("f5d8f6b8b21c44548d2799044d3105f0","b3845ea35176403bb530a31fd4481165", api_version=API_V2_0)
            data = self.account.get_candles(self.pairName, tick_interval=TICKINTERVAL_FIVEMIN)
        
            if (data['success'] == True and data['result']):
                self.data = data['result']
                self.current = self.data[-1]
                self.prev = self.data[-2]
            
            break
        
     
            
    def GetBalance(self): 
        
        data = self.account.get_balance(self.currency)
        
        if (data['success'] == True and data['result'] != None):
            result = data['result']           
            self.balance = result['Balance']
        else: 
           self.balance = 0
          
        self.balanceBTC = float(self.balance * self.current['C'])
    
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
                    
                print("There is an %s at %.9f with id: %s" % (order[0]['OrderType'],order[0]['Limit'],order[0]['OrderUuid']))
            else:
            	self.Order = 0
	else:
	    self.Order = 0
        
          
 
                             
 
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
        
        ###Get di+ & di- Trend
        
        self.diPos=[]
        self.diNeg=[]
        self.tr=[]
        self.trMax=[]
        self.dmPos=[]
        self.dmNeg=[]
        self.dmPosMax=[]
        self.dmNegMax=[]
     
        
        #calculate TR, dmPos, dmNeg
        tr=[]
        dmPos=[]
        dmNeg=[]
        
        for i in range(1,len(self.data)):
            itemP = self.data[i-1]
            itemN = self.data[i]
           
            maximum = max(itemN['H'] - itemN['L'], abs(itemN['H'] - itemP['C']), abs(itemN['L'] - itemP['C']))
            tr.append(maximum)
            
            if (itemN['H'] - itemP['H']) > (itemP['L'] - itemN['L']):
                dmPos.append(max((itemN['H'] - itemP['H']), 0))
            else:               
                dmPos.append(0)
                
            if (itemP['L'] - itemN['L']) > (itemN['H'] - itemP['H']):
                 dmNeg.append(max((itemP['L'] - itemN['L']), 0))               
            else:
                  dmNeg.append(0)
               
     
        self.tr = tr
        self.dmPos = dmPos
        self.dmNeg = dmNeg
    
        #calculate trMax,dmPosMax,dmNegMax
        
        SumTrMax = 0
        SumdmPosMax = 0
        SumdmNegMax = 0
        
        
        for i in range(13):
             SumTrMax += self.tr[i]
             SumdmPosMax += self.dmPos[i]
             SumdmNegMax += self.dmNeg[i]
             
        self.trMax.append(SumTrMax)
        self.dmPosMax.append(SumdmPosMax)
        self.dmNegMax.append(SumdmNegMax) 
        

        for i in range(1,len(self.tr) - 13):
            self.trMax.append(self.trMax[i-1] - (self.trMax[i-1]/14) + self.tr[i+13])
            self.dmPosMax.append(self.dmPosMax[i-1] - (self.dmPosMax[i-1]/14) + self.dmPos[i+13])
            self.dmNegMax.append(self.dmNegMax[i-1] - (self.dmNegMax[i-1]/14) + self.dmNeg[i+13])
            

        #calculate diPos & diNeg
        for i in range(0, len(self.trMax)):
            self.diPos.append((self.dmPosMax[i] / self.trMax[i]) * 100)
            self.diNeg.append((self.dmNegMax[i] / self.trMax[i]) * 100)
            
        print("DI- is: %.9f" % self.diNeg[-1])    
        print("DI+ is: %.9f" % self.diPos[-1])        
        
        if (self.diNeg[-1] > self.diPos[-1]): ##Downtrend
            self.Direction = 0 
        elif (self.diNeg[-1] == self.diPos[-1]): ##possible crossover
            self.Direction = 0
        else:
            self.Direction = 1 ##uptrend 
                
           
        print("Direction is: %d" % self.Direction)   
      
        

        
      

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
        
        period = 8
        
        for x in range (y/period):  
            
            for z in range(y - (x+1)*period, y-(period*x + 1)):
                highest.append(high[z])
                lowest.append(low[z])
                
            self.tenkanSen.append((max(highest) + min(lowest))/2) 
            highest *= 0
            lowest *= 0
                    
         
        period = 32
        
        for x in range (y/period):  
            
            for z in range(y - (x+1)*period, y-(period*x + 1)):
                highest.append(high[z])
                lowest.append(low[z])
                
            self.kijunSen.append((max(highest) + min(lowest))/2) 
            highest *= 0
            lowest *= 0
                    
     

        print("red at: %.9f" % self.tenkanSen[0])  
        print("blue at: %.9f" % self.kijunSen[0])  
            
        #find state of Tenkansen & Kijunsen as IchState
        if (self.tenkanSen[0] > self.kijunSen[0]): ##red on top of blue
            self.IchState = 1
        else:
            self.IchState = 0
            
        print("Ichstate: %d" % (self.IchState))    
       
    
        if (self.IchState == 1 and self.Direction == 1):
            self.active = 1
            print ("Pair is active")
        else:
            print ("Pair is not active")
            self.active = 0
            
        
                
      
    def UploadData(self):

        cursor = self.conn.cursor()
        query = "UPDATE `Pairs` SET `BuyState`=%d,`DistanceA`=%.9f,`DistanceB`=%.9f,`PID`=%d WHERE Pair ='%s'" % (self.buy,self.DistanceA,self.DistanceB,self.pid,self.pairName)

        try:
            cursor.execute(query)
            self.conn.commit()
        
        except MySQLdb.Error as error:
            print(error)
            self.conn.rollback()
            self.conn.close()
            
            
    def BuyPair(self):   

        
        print("buying pair")      
        
        ##Buy Price is at blue line
        self.OrderAmount = float(self.BuyLimit/ self.BuyPrice)
        
        print("buying %s at amount %.9f for price %.9f" % (self.pairName,self.OrderAmount,self.BuyPrice))
     
        data = self.account.trade_buy(self.pairName, ORDERTYPE_LIMIT,self.OrderAmount,self.BuyPrice, TIMEINEFFECT_GOOD_TIL_CANCELLED,CONDITIONTYPE_NONE, target=0.0) ##now placing buy order
            
        if (data['success'] == True):
            print("Buy Order in place")
        else:
            print(data)
               
            
            
    def SellPair(self):   
        
     
        ##get pair and amount to sell
        print("Creating Sell order")
        amount = float(self.balance * 0.999)
        print("selling %s of amount %.9f at %.9f" % (self.pairName, amount, self.SellPrice))
        
                
        while True: 
            
            data = self.account.trade_sell(self.pairName, ORDERTYPE_LIMIT, amount, self.SellPrice, TIMEINEFFECT_GOOD_TIL_CANCELLED,CONDITIONTYPE_NONE, target=0.0) ##now placing sell order
            
            if (data['success'] == True):
                print("Sell Order in place")
                break
            
    def CheckBuyPosition(self):
        
        '''
        Conditions that have to meet: 
        self.tenkanSen[0] > self.tenkanSenP (current > previous)
        self.tenkanSen[0] > float(self.kijunSen[0] * 1.0025)
        self.current['C'] < self.tenkanSen[0]  (if price is hovering above )
        '''
        
        self.BuyPrice = float(self.kijunSen[0] * self.BuyBuffer)
        
        if (self.active == 0 and self.current['L'] < self.BuyPrice): ##we're on the bottom of a downtrend 
            self.Buy = 1 
            print("We're in a position to buy")
        else:
            print("We're not in a position to buy")
            self.Buy = 0
        
        
               
    def CheckOrder(self):
        
        '''
        This function updates Orders if conditions do not meet, conditions are:
        
        Buy orders exist when we're in the buy zone (self.Buy == 0)
        Sell orders exist when we're in the active zone (self.active == 0) and we always readjust
        Sell orders to meet the update SellPrice (following tenkanSen * sellBuffer)
        
        ''' 
            
        ##different sell buffers for different active zones
        if (self.active == 0):
            self.SellPrice = float(self.kijunSen[0] * self.SellBufferH) 
        else:
            self.SellPrice = float(self.tenkanSen[0] * self.SellBufferL)
            
        
        SellPriceH = float(self.SellPrice * 1.001)
        SellPriceL = float(self.SellPrice * 0.994)       
        
        if (self.Order == 0):
            
            if (self.balanceBTC < 0.01 and self.Buy == 1): ##low balance and we're in Buy Zone
                self.BuyPair() 
            elif (self.balanceBTC > 0.01): ##only sell when tenkansen 
                if (self.active == 1):
                    print("in active selling zone")
                    self.SellPair() ##make a sell order
                else:
                    print("Not in selling zone")
                
        elif (self.Order == 1): ##sell order in place
            
            if (self.OrderPrice < SellPriceL or self.OrderPrice > SellPriceH):  ##make sure its in the Sell Order zone 
                data = self.account.cancel(self.OrderID)                        ##Cancel that Sell Order
                print("updating sell Order!")
                self.SellPair() ##readjust
            else:
                print("Sell Order is still okay!")
                
        elif (self.Order == 2): ##Buy order in place
        
            if (self.Buy == 0): ##we're in buy zone, check order
                data = self.account.cancel(self.OrderID)                        ##Cancel that Buy Order
                print("Cancelling Buy order, no longer in Buy Zone")
            else:
                print("Buy Order is still okay!")
                
                
            
        
    
##program start here

pair = MyPair()
ListofPairs = []     ##list of Pairs, e.g. BTC-ADA, ETH-ADA
ListofCurrencies= [] ##list of Currencies e.g. ADA, OMG

 ##Get list of pairs
print("getting pairs")
print(".............................................")

cursor = pair.conn.cursor()
query = "SELECT * FROM Pairs"

try:
    cursor.execute(query)
    data = cursor.fetchall()   
    for i in range(len(data)):
        ListofPairs.append(str(data[i][0]))
        ListofCurrencies.append(str(data[i][1]))
       
        
except MySQLdb.Error as error:
    print(error)
    pair.conn.close()    



while True:  ##Forever loop 


    ## for every pair
    for i in range(len(ListofPairs)):
        
        pair.GetData(ListofPairs[i],ListofCurrencies[i]) ##get data for Pair
        pair.GetBalance()
        print("Pair %s" % (pair.pairName))
        print("Balance: %.9f" % (pair.balance))
        print("**************************************")
        print(" ")
        print("current is: %.9f" % pair.current['C'])   
        print("Open is: %.9f" % pair.current['C']) 
        print("Low is: %.9f" % pair.current['C']) 
        print("High is: %.9f" % pair.current['C']) 
        print("____________________________________")
        print(" ")
        
        
        
        
        pair.GetTrend()              ##get EMA Trend and Direction
        pair.GetActive()             ##get Active Zone 
        pair.CheckBuyPosition()        ##get Buy Zone
        
        
        print("____________________________________")
        print(" ")
        
        print("checking order")
        pair.GetOrder()
        pair.CheckOrder()
        print("________________DONE________________")
       
       ## pair.UploadData()            ##upload data
        
        
        
    time.sleep(60) ## delay to not stuff up api calls







