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
                        dest='pair',  # use `pair` to access value
                        help='The Pair to be watched')
    parser.add_argument('-k', '--key',
                        action='store',  # tell to store a value
                        dest='api',  # use `paor` to access value
                        help='Your API Key')
    parser.add_argument('-s', '--secret',
                        action='store',  # tell to store a value
                        dest='secret',  # use `paor` to access value
                        help='Your API Secret')
    parser.add_argument('-l', '--limit',
                        action='store',  # tell to store a value
                        dest='limit',  # use `paor` to access value
                        help='Your Buy Limit')
    parser.add_argument('-m', '--buybuffer',
                        action='store',  # tell to store a value
                        dest='buyBuffer',  # use `paor` to access value
                        help='your buy buffer')
    parser.add_argument('-n', '--sellbuffer',
                        action='store',  # tell to store a value
                        dest='sellBuffer',  # use `paor` to access value
                        help='your sell buffer')
    parser.add_argument('-ex', '--simulate',
                        action='store',  # tell to store a value
                        dest='ex',  # use `paor` to access value
                        help='Simulation on or off')
    parser.add_argument('-t', '--time',
                        action='store',  # tell to store a value
                        dest='time',  # use `paor` to access value
                        help='Time Interval')
   
    action = parser.parse_args()
    return action
    
    
    

class MyPair(object):

    def __init__(self,entry):
        
        ##Get process pid
        self.pid = os.getpid()  
        print("pid is: %d" % self.pid)

        self.pairName = entry.pair
        self.conn = MySQLdb.connect(Fink_DB_HOST,Fink_DB_USER,Fink_DB_PW,Fink_DB_NAME) 
        self.edel = MySQLdb.connect(Edel_DB_HOST,Edel_DB_USER,Edel_DB_PW,Edel_DB_NAME) ##connect to DB
        
        self.UID = "admin"
       
        ##experimental stuff
        self.ExBuyPrice = 0
        self.Exhold = 0
        self.ExOrder = 0
        self.ExReturn = 0
        self.ExSellPrice = 0
        
        ## Insert PID
        cursor = self.conn.cursor()
        query = "UPDATE Pairs SET PID = %d WHERE Pair='%s'" % (self.pid,self.pairName) ##Null IchState, put in PID and entry pair

        try:
            cursor.execute(query)
            self.conn.commit()
            print("intialized")
    
        except MySQLdb.Error as error:
            print(error)
            self.conn.rollback()
            self.conn.close()
          
        ## get currency
        cursor = self.conn.cursor()
        query = "SELECT Currency from `Pairs` WHERE Pair='%s' " % (self.pairName)
        
        try:
            cursor.execute(query)
            data = cursor.fetchone()
            self.currency = data[0]
        
        except MySQLdb.Error as error:
            print(error)
            self.conn.close()
            
            
            
    def SetParams(self,entry):
        
        print("Applying parameters")
        print(" " )
        
        if (entry.api != None and entry.secret != None):
            self.api = entry.api
            self.secret = entry.secret
            self.account = Bittrex(self.api, self.secret, api_version=API_V2_0) ##now connect to bittrex with api and key
        else:
            print("Please insert api & secret key")
            quit()
        
        if (int(entry.time) == 1): 
            self.TimeInterval = "ONEMIN"
            self.TimeIntervalINT = 1
            print("Time interval set to 1 minute")
            print("This is not a suggested time interval for Fink Lite")
        elif (int(entry.time)  == 5): 
            self.TimeInterval = "FIVEMIN"
            self.TimeIntervalINT = 5
            print("Time interval set to 5 min")
        elif (int(entry.time)  == 30): 
            self.TimeInterval = "THIRTYMIN"
            self.TimeIntervalINT = 30
            print("Time interval set to 30 min")
        elif (int(entry.time)  == 60): 
            self.TimeInterval = "HOUR"
            self.TimeIntervalINT = 60
            print("Time interval set to 60 min")
        else:
            self.TimeInterval = "FIVEMIN"
            self.TimeIntervalINT = 5
            print("Time interval set to default 5 minutes")
            
        if (entry.buyBuffer != None):
            self.BuyBuffer = float(entry.buyBuffer)
            print("Buy buffer set to : %.9f") % self.BuyBuffer
        else:
            self.BuyBuffer = 0.95
            print("Buy Buffer set to default 5%")
            
            
        if (entry.sellBuffer != None):
            self.SellBuffer = float(entry.sellBuffer)
            print("Sell buffer set to : %.9f") % self.SellBuffer
        else:
            self.SellBuffer = 1.03
            print("Sell Buffer set to default 3%")
            
        if (int(entry.ex) == 1):
            self.ex = 1
            print("experiment mode on!")
        else:
            self.ex = 0
            
        print(" ")    
        print("___Parameters Applied !_____")
        print(" " )
            
            
            
    def GetActivationStatus(self):
        
        ##Check that Activated = 1 on that UID
        
        cursor = self.edel.cursor()
        query = "SELECT Active from `User_List` WHERE UID='%s' " % (self.UID)
        
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
            
            if (self.TimeIntervalINT == 1):
                result = self.account.get_candles(self.pairName, tick_interval=TICKINTERVAL_ONEMIN)
            elif (self.TimeIntervalINT == 5):
                result = self.account.get_candles(self.pairName, tick_interval=TICKINTERVAL_FIVEMIN)
            elif (self.TimeIntervalINT == 30):
                result = self.account.get_candles(self.pairName, tick_interval=TICKINTERVAL_THIRTYMIN)
            elif (self.TimeIntervalINT == 60):
                result = self.account.get_candles(self.pairName, tick_interval=TICKINTERVAL_HOUR)
        
            if (result['success'] == True and result['result']):
                self.raw = result['result']
                self.SortData()
            
            break
        
        
    def SortData(self): 
         self.data = []
            
         self.data.append(self.raw[0]) ##get the first data in 
         
         ##this is where we check the intervals between every data and fill in the blanks
         for i in range(1,len(self.raw)):
             tdiff = datetime.datetime.strptime(self.raw[i]['T'],"%Y-%m-%dT%H:%M:%S") - datetime.datetime.strptime(self.raw[i-1]['T'],"%Y-%m-%dT%H:%M:%S") 
             td_mins = int(round(tdiff.total_seconds() / 60))
            # print(td_mins)
                           
             ##here we insert the missing numbers
             if (td_mins > self.TimeIntervalINT):         
                 interval = td_mins / self.TimeIntervalINT
                 for x in range(1,interval):
                     self.data.append(self.raw[i-1])  
                     self.data[-1]['L'] = self.data[-1]['C']
                     self.data[-1]['H'] = self.data[-1]['C']
                     self.data[-1]['O'] = self.data[-1]['C']

                 self.data.append(self.raw[i])
             else: 
                 
                 self.data.append(self.raw[i])
                 
         ##this is where we check if the last data time is the current time if not, fill in blanks
                 
         
         currentTime = datetime.datetime.now()
         tdiff = currentTime - datetime.datetime.strptime(self.data[-1]['T'],"%Y-%m-%dT%H:%M:%S") 
         td_mins = int(round(tdiff.total_seconds() / 60)) - 600
         
         if (td_mins > 0):
             interval = td_mins / self.TimeIntervalINT
             
             for x in range(1,interval):
                     self.data.append(self.data[-1])  
                     self.data[-1]['L'] = self.data[-1]['C']
                     self.data[-1]['H'] = self.data[-1]['C']
                     self.data[-1]['O'] = self.data[-1]['C']
             
         #print(self.data)
                 
         
         self.current = self.data[-1]
         self.prev = self.data[-2]
        
     
            
    def GetBalance(self): 
        
        data = self.account.get_balance(self.currency)
        
        if (data['success'] == True and data['result'] != None):
            result = data['result']           
            #print(result)
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
        
        
        ###Get EMA Trend fidef GetTrend(self):
        
        
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
             if (self.trMax[i] != 0):
                self.diPos.append(float(self.dmPosMax[i] / self.trMax[i]) * 100)
                self.diNeg.append(float(self.dmNegMax[i] / self.trMax[i]) * 100)
            
        print("DI- is: %.9f" % self.diNeg[-1])    
        print("DI+ is: %.9f" % self.diPos[-1])        
        
        if (self.diNeg[-1] > self.diPos[-1]): ##Downtrend
            self.Direction = 0 
        elif (self.diNeg[-1] == self.diPos[-1]): ##possible crossover
            self.Direction = 0
        elif (self.diNeg[-1] < self.diPos[-1] and self.diPos[-1] > 25): ##uptrend
            self.Direction = 1
        else:
            self.Direction = 0
                
           
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
       
    
        if (self.IchState == 1 and self.Direction == 1 and self.EMATrend == 1 ):
            self.active = 1
            print ("Pair is active")
        else:
            print ("Pair is not active")
            self.active = 0
        
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
            self.trMax.append(float(self.trMax[i-1] - float(self.trMax[i-1]/14) + self.tr[i+13]))
            self.dmPosMax.append(float(self.dmPosMax[i-1] - float(self.dmPosMax[i-1]/14) + self.dmPos[i+13]))
            self.dmNegMax.append(float(self.dmNegMax[i-1] - float(self.dmNegMax[i-1]/14) + self.dmNeg[i+13]))
            
            
        
        #calculate diPos & diNeg
        for i in range(0, len(self.trMax)):
            if (self.trMax[i] != 0):
                self.diPos.append(float(self.dmPosMax[i] / self.trMax[i]) * 100)
                self.diNeg.append(float(self.dmNegMax[i] / self.trMax[i]) * 100)
            
        print("DI- is: %.9f" % self.diNeg[-1])    
        print("DI+ is: %.9f" % self.diPos[-1])        
        
        if (self.diNeg[-1] > self.diPos[-1]): ##Downtrend
            self.Direction = 0 
        elif (self.diNeg[-1] == self.diPos[-1]): ##possible crossovertrMAX
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
            
        
    
    def GetCandleState(self):
        
        '''
        This verifies if we're entering the Ichstate properly
        '''
        
        print("current low: %.9f" %(self.prev['L']))
        print("current close: %.9f" %(self.prev['C']))
        print("current high: %.9f" %(self.current['H']))
        
        if ((self.current['O'] < self.kijunSen[0] * 0.997) and (self.current['C'] < self.tenkanSen[0])) and (self.current['C'] > self.current['O']):
            self.CandleState = 1
        else:
            self.CandleState = 0
        
        print("CandleState: %d" % (self.CandleState))
        
                
      
    def UploadData(self):

        cursor = self.conn.cursor()
        query = "UPDATE Pairs SET TradeSignal = %d, HoldBTC=%.9f, PID = %d WHERE Pair = '%s'" % (self.Buy,self.balanceBTC, self.pid,self.pairName)

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
        
        if (self.active == 0 and self.current['L'] < self.BuyPrice and self.State == 1):
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
        #if (self.active == 0):
        #    self.SellPrice = float(self.tenkanSen[0] * self.SellBufferL) 
        #else:
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
        
            if (self.active == 1):
                if (self.OrderPrice < SellPriceL or self.OrderPrice > SellPriceH):  ##make sure its in the Sell Order zone 
                    data = self.account.cancel(self.OrderID)                        ##Cancel that Sell Order
                    print("updating sell Order!")
                    self.SellPair() ##readjust
                else:
                    print("Sell Order is still okay!")
            else:
                data = self.account.cancel(self.OrderID)                        ##Cancel that Sell Order
                print("cancelled order, not in selling zone")
                
        elif (self.Order == 2): ##Buy order in place
        
            if (self.Buy == 0): ##we're in buy zone, check order
                data = self.account.cancel(self.OrderID)                        ##Cancel that Buy Order
                print("Cancelling Buy order, no longer in Buy Zone")
            else:
                print("Buy Order is still okay!")
                    
                    
                    
    def ExAction(self):
        
        '''
            Experimental Stuff
        '''
        
        
        if (self.ExOrder == 0):
            
            if (self.Exhold == 0 and self.Buy == 1 and self.current['L'] < float(self.kijunSen[0] * self.BuyBuffer)):
                self.ExOrder = 2 ##buy
                self.ExBuyPrice = self.kijunSen[0] * self.BuyBuffer ##buy price
                print("Experimental Buy order in at %.9f" % (self.ExBuyPrice))
             
            if (self.Exhold == 1 and self.active == 1):
                self.ExOrder = 1
                self.ExSellPrice = self.tenkanSen[0] * self.SellBuffer ##sell buffer
                print("Experimental Sell order in at %.9f" % (self.ExSellPrice))
           
            
        elif (self.ExOrder == 2): ## buy order
            if (self.ExBuyPrice > self.current['L']):
                print ("Buy complete")
                self.ExOrder = 0
                self.Exhold = 1
                
                ##log the action
                ts = time.time()
                timestamp = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')
                cursor = self.conn.cursor()
                query = "INSERT INTO `ExLog`(`Pair`, `Action`, `Price`, `Profit`, `Time`) VALUES ('%s','Buy',%.9f,0,'%s')" % (self.pairName,self.ExBuyPrice,timestamp)

        
                try:
                    cursor.execute(query)
                    self.conn.commit()
                
    
                except MySQLdb.Error as error:
                    print(error)
                    self.conn.rollback()
                    self.conn.close()
                    
            else:
                if (self.active == 1 or self.current['L'] > float(self.kijunSen[0] * self.BuyBuffer)):
                    self.ExOrder = 0
                else:
                    self.ExBuyPrice = self.kijunSen[0] * self.BuyBuffer ##buy price
                    print("re-adjusting buy price to %.9f") % (self.ExBuyPrice)
                
        elif (self.ExOrder == 1): #sell order
        
            if (self.ExSellPrice < self.current['H']):
                self.ExReturn = float(self.ExSellPrice / self.ExBuyPrice - 1.005)
                print ("Sell Complete -- > Return: %.9f" % (self.ExReturn))
                
                ##log the action
                ts = time.time()
                timestamp = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')
                cursor = self.conn.cursor()
                query = "INSERT INTO `ExLog`(`Pair`, `Action`, `Price`, `Profit`, `Time`) VALUES ('%s','SELL',%.9f,%.9f,'%s')" % (self.pairName,self.ExSellPrice,self.ExReturn,timestamp)

        
                try:
                    cursor.execute(query)
                    self.conn.commit()
                    self.ExOrder = 0
                    self.Exhold = 0
                
                except MySQLdb.Error as error:
                    print(error)
                    self.conn.rollback()
                    self.conn.close()
                    
            else:
                if (self.active == 1):
                    self.ExSellPrice = self.tenkanSen[0] * self.SellBuffer ##sell buffer
                    print("re-adjusting sell price to %.9f") % (self.ExSellPrice)
                elif (self.active == 0): 
                    self.ExOrder = 0
            
                
                
        
         
    
            
                
                      
                
##program start here

entry = GetEntry() ##Get arguments to define Pair and Fib levels
pair = MyPair(entry)
pair.SetParams(entry)


while True:  ##Forever loop 


    print(" ")
    print("Pair %s" % (pair.pairName))
        
    print(" ")
    pair.GetData()
    pair.GetBalance() 
        
        
    print("Balance: %.9f" % (pair.balance))
    print("**************************************")
    print(" ")
    print("current is: %.9f" % pair.current['C'])   
    print("Open is: %.9f" % pair.current['C']) 
    print("Low is: %.9f" % pair.current['C']) 
    print("High is: %.9f" % pair.current['C']) 
    print("____________________________________")
    print(" ")  
        
    pair.GetActivationStatus()   
    if (pair.activation == 0):
        print("sorry your agent system is not activated, please activate it !")
        quit()
    
    pair.GetTrend()              ##get EMA Trend and Direction
    pair.GetActive()             ##get Active Zone 
    pair.CheckBuyPosition()        ##get Buy Zone
        
    print("____________________________________")
    print(" ")
        
    print("checking order")
    pair.GetOrder()
    if (pair.ex == 0):    
        pair.CheckOrder()
    else:
        pair.ExAction()
    print("________________DONE!!!________________")
           
    pair.UploadData() 
   
   
    time.sleep(3) ## enoguh delay for an order to be complete







