from bittrex.bittrex import *
import statistics 
import os
import MySQLdb
import time
import datetime
from settings import *
from ta import *
import numpy as np




class MyPair(object):

    def __init__(self,entry):
        
        ##Get process pid
        self.pid = os.getpid()  
        print("pid is: %d" % self.pid)

        
        self.edel = MySQLdb.connect(Edel_DB_HOST,Edel_DB_USER,Edel_DB_PW,Edel_DB_NAME) ##connect to DB
        
               
        self.balance = 0
        self.Prevbalance = 0
        self.RMI = 0
        self.Rup = []
        self.Rdn = []
        
        self.LastOptimizeTime = 0
        
        self.LastBuyPrice = 0
        self.BuyPrice = 0
        self.order = 2
        
        self.mode = 2
        self.prevmode = 2
        self.signal = 2
        self.ready = 0
        
        
        self.BestSMABuyLimit = 0
        self.BestSMASellLimit = 0
        self.BestFibMax = 0
        self.BestFibMin = 0
        self.bestBuyAt = 0
        
        """ TA """
        self.SMA = []
        self.SMAIchD  = []
        self.SMAIchDSMA = []
        
        self.tenkanSen = []
        self.kijunSen = []
        self.IchD = []
        self.senkouB = []
        self.senkouA = []
        
        self.data = []
        self.low = []
        self.high = []
        self.open = []
        self.close = []
        self.time = []
        
        self.RollingFib = []
        
        self.initial = 0
        self.position = 0
        
        self.BestRoof = 0
        self.BestFloor = 0
        self.rl = 0
        
        self.state = 0
        
        
        
          

            
            
    def SetParams(self,entry):
        
        print("Applying parameters")
        print(" " )
        
        if (entry.api != None and entry.secret != None and entry.uid != None):
            self.api = entry.api
            self.secret = entry.secret
            self.UID = entry.uid
            self.account = Bittrex(self.api, self.secret, api_version=API_V2_0) ##now connect to bittrex with api and key
        else:
            print("Please insert api & secret key & UID")
            quit()
            
            
        if (entry.pair != None or entry.currency != None):
            self.pairName = entry.pair
            self.currency = entry.currency
        else:
            print("Please insert a valid Pair or Currency")
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
            self.TimeInterval = "HOUR"
            self.TimeIntervalINT = 60
            print("Time interval set to default 60 minutes")
            
        if (entry.limit != None):
            self.BuyLimit = float(entry.limit)
            print("Buy limit set to : %.9f") % self.BuyLimit
        else:
            self.BuyLimit = 0.02
            print("Buy limit set to default 0.02 BTC")
            
        if (entry.agLvl != None):
            self.agLvl = float(entry.agLvl)
            print("Aggresion Level set to level %d") % self.agLvl
        else:
            self.agLvl = 0
            print("Aggresion Level set to level 0")

            
        if (entry.lp != None):
            self.lp = int(entry.lp)
            print("Looking back %d periods") % self.lp
        else:
            self.lp = int((24*14*60)/self.TimeIntervalINT)
            print("Looking back at default of 2 weeks, period: %d")%(self.lp)
            
            
        if (entry.sl != None):
            self.sl = float(entry.sl)
            print("Stop limit at %.9f") % self.sl
        else:
            self.sl = 0.9
            print("Stop limit at default 10%")
            
            
        if (int(entry.st) == 0): ##system not in standalone mode
            
            self.st = 0
            
            if (entry.ip != None): ##slave with ip given
                self.ip = entry.ip 
            else:
                self.ip = "localhost"
        else:
            self.st = 1
            print("System in standalone mode")
            
        if (int(entry.ex) == 1):
            self.ex = 1
            
            import matplotlib.pyplot as plt
            print("experimentation on, trading disabled")
        else:
            self.ex = 0 
            
            
        print(" ")    
        print("___Parameters Applied !_____")
        print(" " )
        
        
        ## Insert PID
        if (self.st == 0):
            self.conn = MySQLdb.connect(self.ip,Fink_DB_USER,Fink_DB_PW,Fink_DB_NAME) 
            cursor = self.conn.cursor()
            query = "UPDATE Pairs SET PID = %d, TradeSignal = 0, HoldBTC = 0, ReturnLimit = 0, OptimizeTime = 0 WHERE Pair='%s'" % (self.pid,self.pairName) ##Null IchState, put in PID and entry pair

            try:
                cursor.execute(query)
                self.conn.commit()
                print("intialized")
    
            except MySQLdb.Error as error:
                print(error)
                self.conn.rollback()
                self.conn.close()
        

        
    def GenerateKey(self):
        
        ##Generate Key 
        
        api = str(self.api)
        key = str(self.secret)
        
        self.UIK = api[0] + api[5] + key[0] + key[5] + self.UID
                  
            
    def GetActivationStatus(self):
        
        ##Check that Activated = 1 on that UID and that the key matches
        self.GenerateKey() ##generate UIK
        
        ##check if UIK exists

        cursor = self.edel.cursor()
        query = "SELECT Active, UIK from `User_List` WHERE UID='%s' " % (self.UID)
        
        try:
            cursor.execute(query)
            data = cursor.fetchone()
            
            if (data[1] == None and data[0] == 1): ##no UIK yet inserted
            
                ##insert UIK
                cursor = self.edel.cursor()
                query = "UPDATE `User_List` SET `UIK`='%s' WHERE UID='%s'" % (self.UIK,self.UID)
        
                try:
                    cursor.execute(query)
                    self.edel.commit()
                    self.activation = 1
        
                except MySQLdb.Error as error:
                    print(error)
                    self.edel.close()
                    
            elif (data[1] == self.UIK and data[0] == 1):
                self.activation = 1
            else:
                self.activation = 0
        
        except MySQLdb.Error as error:
            print(error)
            self.edel.close()
            
         
            
        
            
    def GetData(self): 
        
        
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
        
         self.data *= 0
         self.low *= 0
         self.high *= 0
         self.open *= 0
         self.close *= 0
         self.time *= 0
         
            
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
             
        
         self.current = self.data[-1]
         self.prev = self.data[-2]
         
             
         
         for i in self.data:
             self.high.append(i['H'])
             self.low.append(i['L'])
             self.open.append(i['O'])
             self.close.append(i['C'])
             self.time.append(datetime.datetime.strptime(i['T'],"%Y-%m-%dT%H:%M:%S") )
        
     
            
    def GetBalance(self): 
        
        data = self.account.get_balance(self.currency)
        
        
        if (data['success'] == True and data['result'] != None):
            result = data['result']   
            self.balance = result['Balance']
            
        else: 
           self.balance = 0
          
        self.balanceBTC = float(self.balance * self.close[-1])
        
        if (self.balanceBTC > 0.005):
            self.hold = 1
        else:
            self.hold = 0
      
        
        if (self.initial == 0):
            self.initial = self.close[-1]
            
        
            
    def BuyPair(self):   

        
        print("buying pair")      
        
        ##Buy Price is at blue line
        self.OrderAmount = float(self.BuyLimit/ self.BuyPrice)
        
        print("buying %s at amount %.9f for price %.9f" % (self.pairName,self.OrderAmount,self.BuyPrice))
     
        data = self.account.trade_buy(self.pairName, ORDERTYPE_LIMIT,self.OrderAmount,self.BuyPrice, TIMEINEFFECT_GOOD_TIL_CANCELLED,CONDITIONTYPE_NONE, target=0.0) ##now placing buy order
            
        if (data['success'] == True):
            print("Buy Order in place")
            
            self.initial = self.BuyPrice
            
            ##log the action
            if (self.st == 0):
                ts = time.time()
                timestamp = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')
                cursor = self.conn.cursor()
                query = "INSERT INTO `AccountHistory`(`PID`, `Pair`, `Amount`, `Price`, `Action`, `ActionTime`) VALUES ('%s','%s',%.9f,%.9f,'BUY','%s')" % (self.pid,self.pairName,self.OrderAmount,self.BuyPrice,timestamp)
            
                try:
                    cursor.execute(query)
                    self.conn.commit()
                
                except MySQLdb.Error as error:
                    print(error)
                    self.conn.rollback()
                    self.conn.close()    
                    
    
        else:
            print(data)
            self.signal = 2
               
            
            
    def SellPair(self):   
        
        ##get pair and amount to sell
        print("Creating Sell order")
        amount = float(self.balance * 0.999)
        print("selling %s of amount %.9f at %.9f" % (self.pairName, amount, self.SellPrice))
    
            
        data = self.account.trade_sell(self.pairName, ORDERTYPE_LIMIT, amount, self.SellPrice, TIMEINEFFECT_GOOD_TIL_CANCELLED,CONDITIONTYPE_NONE, target=0.0) ##now placing sell order
            
        if (data['success'] == True):
            print("Sell Order in place")
            
            ##log the signal
            if (self.st == 0):
                ts = time.time()
                timestamp = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')
                cursor = self.conn.cursor()
                query = "INSERT INTO `AccountHistory`(`PID`, `Pair`, `Amount`, `Price`, `Action`, `ActionTime`) VALUES ('%s','%s',%.9f,%.9f,'SELL','%s')" % (self.pid,self.pairName,amount,self.SellPrice,timestamp)
            
                try:
                    cursor.execute(query)
                    self.conn.commit()
                
                except MySQLdb.Error as error:
                    print(error)
                    self.conn.rollback()
                    self.conn.close()  
                    
        else:
            print(data)
            self.signal = 2
        
        
        
        
    def GetIchT(self,kPeriod):
        
   
        self.tenkanSen = []
        self.kijunSen = []
        self.IchD = []
        self.senkouB = []
        self.senkouA = []
        
        tPeriod = 9
        #kPeriod = 800
        high = 0
        low = 1
        
        #get Tenkansen 
        
        ##first fill in the 0s
        for z in range (0, tPeriod):
            self.tenkanSen.append(self.data[0]['C'])
        
        for x in range (tPeriod-1, len(self.data)):
            
            ## find the highest & lowest for 9 periods
            for y in range (x - (tPeriod), x):
                if high < self.high[y]:
                    high = self.high[y]
                if low > self.low[y]:
                    low = self.low[y]
              
            self.tenkanSen.append(float((high + low)/2))
            high = 0
            low = 1
            
            
        #get kijunSen 
        
        ##first fill in the 0s
        for z in range (0, kPeriod):
            self.kijunSen.append(self.data[0]['C'])
        
        for x in range (kPeriod-1, len(self.data)):
            
            ## find the highest & lowest for 32 periods
            for y in range (x - (kPeriod), x):
                if high < self.high[y]:
                    high = self.high[y]
                if low > self.low[y]:
                    low = self.low[y]
                
            self.kijunSen.append(float((high + low)/2))
            high = 0
            low = 1
            
            
        ## now get the differences    
        for z in range (0,len(self.kijunSen)):
            if (self.tenkanSen[z] == 0 or self.kijunSen[0] == 0):
                self.IchD.append(0)
            else:
                self.IchD.append(float(self.tenkanSen[z] / self.kijunSen[z]))
                
                

    
            
    def GetSMA(self):
        
        
        self.SMA = []
        self.SMAIchD  = []
        self.SMAIchDSMA = []
        SMAPeriod = 4
        SMAPeriodD = 10
        w = 0
        
        ##SMA 4 periods of close
        
        ##first fill in the 0s
        for z in range (0, SMAPeriod):
            self.SMA.append(self.close[0])
        
        for x in range (SMAPeriod-1, len(self.data)):
            
            ## find the highest & lowest for 9 periods
            for y in range (x - (SMAPeriod), x):
                w = float(w+self.close[y])
                
            self.SMA.append(float(w/SMAPeriod))
            w = 0
            
        #print(len(self.SMAIchD))
            
         ## now get the differences    
        for z in range (0,len(self.kijunSen)):
            if (self.SMA[z] == 0 or self.kijunSen[0] == 0):
                self.SMA.append(0)
            else:
                self.SMAIchD.append(float(self.SMA[z]/self.kijunSen[z]))
                
        ##get a SMA of SAMICHD
            
         ##SMA 4 periods of close
        
        ##first fill in the 0s
        for z in range (0, SMAPeriodD):
            self.SMAIchDSMA.append(self.SMAIchD[z])
        
        for x in range (SMAPeriodD-1, len(self.SMAIchD)):
            
            ## find the highest & lowest for 9 periods
            for y in range (x - (SMAPeriodD), x):
                w = float(w+self.SMAIchD[y])
                
            self.SMAIchDSMA.append(float(w/SMAPeriodD))
            w = 0
            
        
        
    def GetOrder(self):
        
        data = self.account.get_open_orders(self.pairName)  
        
        if (data['success'] == True):
            order = data['result']
            if (order != []):
                self.OrderID = order[0]['OrderUuid']
                self.OrderPrice = order[0]['Limit']
                
                if (order[0]['OrderType'] == 'LIMIT_BUY'):
                    self.Order = 0
                elif (order[0]['OrderType'] == 'LIMIT_SELL'):
                    self.Order = 1
                    
                print("There is an %s at %.9f with id: %s" % (order[0]['OrderType'],order[0]['Limit'],order[0]['OrderUuid']))
            else:
            	self.Order = 2
        else:
            self.Order = 2
            
            
    def GetOrderPrice(self):
        
        fee = 0.0055 ##0.55% fee
        
        self.BuyPrice = self.close[-1]
        
        absolutemin = float(self.initial * (1+fee))      ##absolute minimum is to cover the fee
        minimum = float(self.close[-1] * (self.rl + fee))    ##minium is just slighlty above the fee
        maximum = float(self.initial * self.rl)          ## maximum return limit
        
        
        self.position = float(self.close[-1] / self.initial)
        print("position at: %.9f") % (self.position)
        
        
        if (self.position < 1 and minimum > absolutemin):
            self.SellPrice = minimum
        elif (self.position >= 1): ##current closing price at initial or above
            self.SellPrice = maximum
        elif self.position <= self.sl: ##stop loss
            print("we just hit stop loss")
            self.SellPrice = self.close[-1] 
        else:
            self.SellPrice = absolutemin
            

            
    def MaintainOrder(self):
        
        
        self.GetOrderPrice()
        
        if (self.state == 1 and self.hold == 0 and self.order == 2):##we're not holding something and we got a buy signal, make a buy order
        
            self.BuyPair()
            
            if (self.st == 0):
                ts = time.time()
                timestamp = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')
                cursor = self.conn.cursor()
            
                query = "INSERT INTO `SignalLog`(`Pair`, `BuyPrice`, `SellPrice`, `TimeInterval`, `Time`) VALUES ('%s',%.9f,0.0,'%s','%s')" % (self.pairName,self.BuyPrice,self.TimeInterval,timestamp)
                
                ##log signal 
                try:
                    cursor.execute(query)
                    self.conn.commit()
            
                except MySQLdb.Error as error:
                    print(error)
                    self.conn.rollback()
                    self.conn.close()       
                        
                        
        elif (self.hold == 1 and self.order == 2):##we're not holding something and we got a buy signal, make a sell order
            self.SellPair()
            
            if (self.st == 0):
                ts = time.time()
                timestamp = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')
                cursor = self.conn.cursor()
            
                query = "INSERT INTO `SignalLog`(`Pair`, `BuyPrice`, `SellPrice`, `TimeInterval`, `Time`) VALUES ('%s',0.0,%.9f,'%s','%s')" % (self.pairName,self.SellPrice,self.TimeInterval,timestamp)
                
                ##log signal 
                try:
                    cursor.execute(query)
                    self.conn.commit()
                    
                except MySQLdb.Error as error:
                    print(error)
                    self.conn.rollback()
                    self.conn.close()
          
    
        
        if (self.Order == 1): ## we have a sell order
        
            if (self.OrderPrice < self.SellPrice * 0.994 or self.OrderPrice > self.SellPrice * 1.001): ##Need to readjust order
                data = self.account.cancel(self.OrderID)                                                
                print("updating sell Order!")
                self.SellPair() ##readjust    
            else:
                print("Sell order still good!")
                
            
        elif (self.Order == 0): ## we have a Buy order  
        
            if (self.OrderPrice < self.BuyPrice * 0.994 or self.OrderPrice > self.BuyPrice * 1.001) and self.BuyPrice > 0 and self.state == 1: ##Need to readjust order
                data = self.account.cancel(self.OrderID)                                                
                print("updating buy Order!")
                self.BuyPair() ##readjust           
            elif (self.state == 0):
                data = self.account.cancel(self.OrderID)                                                
                print("Cancelling buy order")
            else:
                print("Buy order still good!")
                
    
        
        
      
    def GetSignal(self):
        
        """ Just Reset Everything """
        
        self.GetBalance()
            
        print("Balance: %.9f" % (self.balance))
        print("**************************************")
        print(" ")


        if (self.hold == 0 or self.rl == 0):
            self.Optimise() ##let's optimize to find the best parameters before any trades
        
        if (self.ready == 1 and self.rl != 0 ):
            
            self.GetIchT(self.IchPeriod)
            self.GetSMA()
        
            print("Last data time: %s") % self.time[-1]
            print("close is: %.9f" % self.close[-1])  
            print("open is:  %.9f" % self.open[-1])  
            print("sma is:   %.9f" % self.SMA[-1]) 
            print("lenght of data: %d") % len(self.close)
            print(" ")
            
            print("******* TA *******")
            print("Momentum: %.9f, Floor: %.9f") % (self.SMAIchDSMA[-1], self.BestFloor)
            print("")
            
            if (self.SMAIchD[-1] <= self.BestFloor):
                self.state = 1 ##buy
            #elif self.initial != 0 and (self.SMAIchD[-1] >= self.BestRoof or float(self.close[-1])/float(self.initial) > self.rl or float(self.close[-1])/float(self.initial) <= self.sl):
            #    self.state = 2 ##sell
            else:
                self.state = 0 ##to prevent buying or selling when we're not meant to sell
                
            if (self.ex == 0):
                self.MaintainOrder()
            else:
                self.PlotData()
     
        else:
            print("NOT READY TO TRADE")
             
        
        
            
            
            
    def Optimise(self):
        
        self.SMA *= 0
        self.SMAIchD  *= 0
        self.SMAIchDSMA *= 0
        self.tenkanSen *= 0
        self.kijunSen *= 0
        self.IchD *= 0
        self.senkouB *= 0
        self.senkouA *= 0
        self.RollingFib *= 0
        
        
        profit = 0
        bestprofit = -100
        buy = 0
        sell = 0
        hold = 0
        buyPrice = 0
        sellPrice = 0
        #self.signals = []
        
        
        wins = 0
        loss = 0
        
      
        bestsignals = 1
        bestwins = 0
        bestloss= 0
        initial = 0
        

        BuyOrder = []
        BuyTime = []
        SellOrder = []  
        SellTime = []
        BuySignals = []
        SellSignals = []
        BuySignalsTime = []
        SellSignalsTime = []
        
        self.BuyOrder = []
        self.BuyTime = []
        self.SellOrder = [] 
        self.SellTime = []
        self.BuySignals = []
        self.SellSignals = []
        self.BuySignalsTime = []
        self.SellSignalsTime = []
        
        
        self.rl = 0
        #Roof = max(self.SMAIchD)
    
        
        
        IchtPeriod = 40
        
        
        print(" ")
        print("...Optimizing Params, Figuring out what's the best for us....")
        print("")
        
        OptimizeStartTime = datetime.datetime.now() 
        
        while (IchtPeriod > 4):
            
            self.GetIchT(IchtPeriod)
            self.GetSMA()
            
            rl = 1.1

            IchtPeriod = IchtPeriod - 4 
        
            while (rl > 1.008):
                
                rl = float(rl - 0.002)
                Floor = max(self.SMAIchD)
                
                while (Floor >= min(self.SMAIchD)):
                    
                    Floor = float(Floor - 0.001)
                
                    profit = 0
                    wins = 0
                    loss = 0
                    r = 0
                    bought = 0
                    
                    BuyOrder *= 0
                    BuyTime *= 0
                    SellOrder *= 0 #reset it
                    SellTime *= 0
                    initial = 0
                    BuySignals *= 0
                    SellSignals *= 0
                    BuySignalsTime *= 0
                    SellSignalsTime *= 0
                
                    hold = 0 
                    order = 0
                    state = 0
                    
                    print("Ichimoku Period at: %d Return Limit at: %.9f Roof at: %.9f") %(IchtPeriod, rl,Floor)
                
                    fee = 0.0055 ##0.55% fee
                
    
                    for i in range (len(self.close)-1-self.lp,len(self.close)-2):
                        
                        if (self.SMAIchD[i] <= Floor):
                            state = 1
                        else: 
                            state = 0
                            order = 0
                            
                        if (hold == 0 and state == 1 and (order == 0 or order == 1)):
                            buyPrice = self.close[i]
                            bought += 1
                            BuySignals.append(self.open[i])
                            BuySignalsTime.append(self.time[i])
                        
                            order = 1
                        
                            
                        elif (hold == 1 and (order == 0 or order == 2)):
                            absolutemin = float(initial * (1+fee))      ##absolute minimum is to cover the fee
                            minimum = float(self.close[i] * (rl + fee))    ##minium is just slighlty above the fee
                            maximum = float(initial * rl)          ## maximum return limit

                            position = float((self.close[i]) / initial)
                        
                            if (position < 1 and minimum > absolutemin):
                                sellPrice = minimum
                            elif (position >= 1): ##current closing price at initial or above
                                sellPrice = maximum
                            elif position <= self.sl: ##stop loss
                                sellPrice = self.close[i] 
                            else:
                                sellPrice = absolutemin
                        
                            order = 2
                                         
         
                        if order == 1 and buyPrice >= self.low[i+1]: ## to make sure order is completed 
                            buy = buyPrice
                            hold = 1    
                            order = 0
                            initial = buy ##initial position
                            BuyOrder.append(buy)
                            BuyTime.append(self.time[i]) 
                    
                        
                        if order == 2 and sellPrice <= self.high[i+1]:
                            sell = sellPrice
                            hold = 0 
                            order = 0
                            r = float(float(float(sell)/float(buy) - 1.005)*100)
                        
                            if (r < 0):
                                loss += 1
                            elif (r > 0):
                                wins += 1
                            
                            profit = float(profit)+float(r)
                        
                            SellOrder.append(sell)
                            SellTime.append(self.time[i]) 
                                
                                
                                
                    if (hold == 1): ##take care of unifnihsed business
                        sell = self.close[i]
                        SellOrder.append(sell)
                        SellTime.append(self.time[i])                                    
                                    
                        r = float(float(float(sell)/float(buy) - 1.005)*100)
                        
                        if (r < 0):
                            loss += 1
                        elif (r > 0):
                            wins += 1
                            
                        profit = float(profit)+float(r)
                                
                                
                    print("profit %.9f") % profit       
                    if (self.agLvl == 0 and profit > bestprofit and profit > 0 and loss == 0 ) or (self.agLvl == 1 and profit > bestprofit and profit > 0 and bought > bestsignals and loss == 0) or (self.agLvl == 2 and profit > 0 and bought > bestsignals and loss == 0):       
                
                        bestprofit = profit
                        bestwins = wins
                        bestloss= loss
                    
                   
                        bestsignals = bought
                        print("")
                        print("Best profit at %.9f" ) % bestprofit
                        print("Amount of Signals: %d") % (bestsignals)
                        print("Amount of wins: %d") % (bestwins)
                        print("Amount of Lossess: %d") % (bestloss)
                        print("")
                    
                        self.BuyOrder *= 0
                        self.BuyTime *= 0
                        self.SellOrder *= 0 
                        self.SellTime *= 0
                    
                        self.BuyOrder = list(BuyOrder)
                        self.BuyTime = list(BuyTime)
                        self.SellOrder = list(SellOrder) 
                        self.SellTime = list(SellTime)
                    
                        self.BuySignals = list(BuySignals)
                        self.SellSignals = list(SellSignals)
                        self.BuySignalsTime = list(BuySignalsTime)
                        self.SellSignalsTime = list(SellSignalsTime)
                    
                        self.rl = rl
                        self.BestFloor = Floor
                        self.IchPeriod = IchtPeriod
                           
                          
                            
         

        hold = float((float(self.close[-1]) / float(self.close[len(self.close)-1-self.lp]) - 1.005) * 100)
        OptimizeFinishTime = datetime.datetime.now()
        
        tdiff = OptimizeFinishTime - OptimizeStartTime 
        self.optimizeTime = int(round(tdiff.total_seconds() / 60))
        print("")
        print("")
        print("______________DONE___________________")
        print("")
        print("%d minutes for Optimizing") % (self.optimizeTime)
        print("")
        
        print("______________!!!!!!___________________ ")
        print("")
        print("Total Best return = %.9f " % (bestprofit))
        print("If HOLD = %.9f ") % hold
        print("")
        print("Amount of wins: %d") % (bestwins)
        print("Amount of Lossess: %d") % (bestloss)
        
        print("")
        print("______________PARAMS___________________ ")
        print("")
        print("Return Limit:  %.9f") % self.rl
        print("FLOOR: %.9f") % self.BestFloor
        print("Ichimoku Period: %d") % self.IchPeriod
        print("")
        
        
        if (bestprofit > 0):
            self.ready = 1
            print("READY TO TRADE NOW")
        else:
            self.ready = 0
    
    
    def PlotData(self):
        
        ##Got to cut the data down
        SMA = []
        tenkanSen = []
        kijunSen = []
        SMAIchD = []
        IchD = []
        RollingFib = []
        timeD = []
        SMAIchDSMA = []
        close = []
        roc = []
        
        
        for i in range (len(self.close)-self.lp-1, len(self.close)-1):
            close.append(self.close[i])
            SMA.append(self.SMA[i])
            tenkanSen.append(self.tenkanSen[i])
            kijunSen.append(self.kijunSen[i])
            #RollingFib.append(self.RollingFib[i])
            IchD.append(self.IchD[i])
            timeD.append(self.time[i])
            SMAIchD.append(self.SMAIchD[i])
            SMAIchDSMA.append(self.SMAIchDSMA[i])
                    
        
        #plt.plot(self.time, self.close, label='Closing Price',color='black', linewidth=0.1)
        plt.figure(1)
        
        plt.subplot(211)
        plt.plot(self.BuyTime, self.BuyOrder, '^', markersize=7, color='g', label = 'Bought')
        plt.plot(self.SellTime, self.SellOrder, 'v', markersize=7, color='r', label = 'Sold')
        plt.plot(self.BuySignalsTime, self.BuySignals, '^', markersize=3, color='blue', label ='Buy Signal')
        plt.plot(self.SellSignalsTime, self.SellSignals, 'v', markersize=3, color='blue', label = 'Sell Signal')
        plt.plot(timeD, close, label='Close',color='black',linewidth=0.3)
        
        
       # plt.plot(timeD, SMA, color = 'red', label='SMA')
       # plt.plot(timeD, kijunSen, color = 'blue', label='kijunSen')
        
        plt.title(self.pairName)
        plt.ylabel('price')
        plt.xlabel('period')
        
        
 
        plt.legend(loc=0)

        plt.subplot(212)
        #plt.plot(timeD, IchD, color = 'red', label='ICHD')
        plt.plot(timeD, SMAIchD, color = 'red', label='Difference')
        #plt.plot(timeD, SMAIchDSMA, color = 'blue', label='SMA')
        plt.title("Custom Relative Momentum Indicator")
        plt.xlabel('period')
        
        #plt.subplot(313)
        #plt.plot(timeD, RollingFib, color = 'blue')
        #plt.title("Fib Retracement Level")
        #plt.xlabel('period')
        
        
        plt.show()
            
            
    def UploadData(self):

        cursor = self.conn.cursor()
        query = "UPDATE Pairs SET TradeSignal = %d, HoldBTC=%.9f, PID = %d, ReturnLimit = %.9f, OptimizeTime = %d WHERE Pair = '%s'" % (self.ready, self.balanceBTC, self.pid,self.rl,self.optimizeTime,self.pairName)

        try:
            cursor.execute(query)
            self.conn.commit()
        
        except MySQLdb.Error as error:
            print(error)
            self.conn.rollback()
            self.conn.close()
        
        
                        
    def Trade(self):
        
        print(" ")
        print("Pair %s" % (self.pairName))
        
        print(" ")
        self.GetData()
        self.GetOrder()
        
        self.GetActivationStatus()   
        if (self.activation == 0):
            print("sorry your agent system is not activated, please activate it !")
            quit()
            
         
        
        self.GetSignal()              ##get Signal
        if (self.st == 0):
            self.UploadData()
        
      
     
        print("____________________________________")
        print(" ")
         
            
            
        print("________________DONE!!!________________")
        
        
        
       
        
        
   
            
                