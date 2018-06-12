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
        self.SellBuffer = 1.005
        self.BuyBuffer = 0.995
        self.tenkanSenP = 0 
        self.cycle = 0
        
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
            self.IchStatePrev = 0
        
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
            data = self.account.get_candles(self.pairName, tick_interval=TICKINTERVAL_HOUR)
        
            if (data['success'] == True and data['result']):
                self.data = data['result']
                self.current = self.data[-1]
                self.entry = entry
                break
            
    def GetBalance(self): 
        
        data = self.account.get_balance(self.currency)
        
        if (data['success'] == True and data['result'] != None):
            result = data['result']           
            self.balance = result['Balance']
        else: 
           self.balance = 0
          
        self.balanceBTC = float(self.balance * self.current['C'])
        print("Balance is: %.9f or %.9f BTC") % (self.balance, self.balanceBTC)
        
          
          
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
            self.IchState = 2
        else:
            self.IchState = 1
            
        print("Ichstate: %d, previous: %d" % (self.IchState, self.IchStatePrev))    
       
    
        if (self.IchState > self.IchStatePrev and self.Direction == 1 and self.IchStatePrev > 0):
            self.active = 1
            print ("Pair is active")
        else:
            print ("Pair is not active")
            self.active = 0
            
        self.IchStatePrev = self.IchState ##store ichstate to previous
        
                
      
    def UploadData(self):

        cursor = self.conn.cursor()
        query = "UPDATE Pairs SET TradeSignal = %d, HoldBTC=%.9f, PID = %d WHERE Pair = '%s'" % (self.active,self.balanceBTC, self.pid,self.pairName)

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
        price = float(self.kijunSen[0] * self.BuyBuffer)
        self.OrderAmount = float(self.BuyLimit/ price)
        
        print("buying %s at amount %.9f for price %.9f" % (self.pairName,self.OrderAmount,price))
    
       
        while True: 
            
            data = self.account.trade_buy(self.pairName, ORDERTYPE_LIMIT,self.OrderAmount,price, TIMEINEFFECT_GOOD_TIL_CANCELLED,CONDITIONTYPE_NONE, target=0.0) ##now placing buy order
            
            if (data['success'] == True):
                print("Buy Order in place")
                ## logging action
                ts = time.time()
                timestamp = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')
                cursor = self.conn.cursor()
                query = "INSERT INTO `AccountHistory`(`PID`, `Pair`, `Amount`, `Price`, `Action`, `ActionTime`) VALUES (%d,'%s',%d,%.9f,'Buy','%s')" % (self.pid,self.pairName,self.OrderAmount,price,timestamp)

        
                try:
                    cursor.execute(query)
                    self.conn.commit()
                    break
        
                except MySQLdb.Error as error:
                    print(error)
                    self.conn.rollback()
                    self.conn.close()
	    else:
		break
        
        
                        
                    
    def SellPair(self):   
        
        '''
        When a SELL signal is identified, a sell order is to be made
        The price of which to be sold is determined by the kijunSen line (no need to go via order book)  
        This reduces the risk of selling at a lower price then originally bought even on a downtrend 
        '''        
        ##get pair and amount to sell
        print("Creating Sell order")
        amount = float(self.balance * 0.999)
        price = float(self.SellBuffer * self.tenkanSen[0])
        print("selling %s of amount %.9f at %.9f" % (self.pairName, amount, price))
        
        self.cycle = 0 ##reset cycle
                
        while True: 
            
            data = self.account.trade_sell(self.pairName, ORDERTYPE_LIMIT, amount, price, TIMEINEFFECT_GOOD_TIL_CANCELLED,CONDITIONTYPE_NONE, target=0.0) ##now placing sell order
            
            if (data['success'] == True):
                print("Sell Order in place")
                
                ## logging action\
                ts = time.time()
            	timestamp = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')
            	cursor = self.conn.cursor()
            	query = "INSERT INTO `AccountHistory`(`PID`, `Pair`, `Amount`, `Price`, `Action`, `ActionTime`) VALUES (%d,'%s',%d,%.9f,'Sell','%s')" % (self.pid,self.pairName,amount,price,timestamp) 
             
                try:
                    cursor.execute(query)
                    self.conn.commit()
                    break
        
                except MySQLdb.Error as error:
                    print(error)
                    self.conn.rollback()
                    self.conn.close()
            else:
                print(data)
                break
            
        
         
    def CheckBuyPosition(self):
        
        '''
        Conditions that have to meet: 
        self.tenkanSen[0] > self.tenkanSenP (current > previous)
        self.tenkanSen[0] > float(self.kijunSen[0] * 1.0025)
        self.current['C'] < self.tenkanSen[0]  (if price is hovering above )
        '''
        
        
        if ((self.tenkanSen[0] < float(self.kijunSen[0] * 1.0025)) or
            (self.current['C'] > self.kijunSen[0])): 
                self.Buy = 0
        else:
            self.Buy = 1
              
        print("Buy Position: %d" % (self.Buy))
        
        
        
        
    def UpdateOrder(self):
        
        '''
        if order is sell: 
            - Sell must be tenkanSen
            - Buy must be  kijunSen
        '''        
        if (self.Order == 2): ## buy order            
            self.cycle = self.cycle + 1    
            print("cycle is at: %d" % (self.cycle))
            if (self.cycle == 60):
                print("Cancelling order, timeout")
                data = self.account.cancel(self.OrderID) ##Cancel that Buy Price because we can't make any +%0.05 retur
                self.cycle = 0
            else:
                print("buy order is still okay!")
                
        elif (self.Order == 1): ##sell order
        
            if (self.OrderPrice < float(self.tenkanSen[0] * self.SellBuffer * 0.994) or self.OrderPrice > float(self.tenkanSen[0] * self.SellBuffer * 1.001)): ##making sure that order is in line with tenkansen 
                data = self.account.cancel(self.OrderID) ##Cancel that Sell Price
                print("updating sell Order!")
                self.SellPair() ##readjust
                
            else:
                print("All Orders are okay!")
                
                
    def Action(self):
        
        if (self.Order > 0):
            print("will check order!")
            self.UpdateOrder()
            
        elif (self.Order == 0):
                print("No orders detected")
                
                if (self.active == 1 and self.balanceBTC < 0.01 and self.Buy == 1): ##No balance 
                    self.BuyPair() ##put in a buy order
                elif (self.balanceBTC > 0.002): ##there is balance
                    print("selling order")
                    self.SellPair() ##put in sell orders
        
        self.UploadData()  
    
            
                
                      
                
##program start here

entry = GetEntry() ##Get arguments to define Pair and Fib levels
pair = MyPair(entry)


while True:  ##Forever loop 

    ##get Data
    pair.GetWatchSignal()

    ##if (pair.watch):
    ##   print("this pair needs to be watched")
    
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
    pair.CheckBuyPosition()
   # pair.Action()
    
   
    time.sleep(60) ## enoguh delay for an order to be complete







