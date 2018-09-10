from bittrex.bittrex import *
from binance.client import Client
import argparse
import time
import os
import subprocess
import psutil
import MySQLdb
import time
import datetime
import numpy as np
#from pair import *
from settings import *
import statistics
#from ta import *



def GetEntry():
    
    parser = argparse.ArgumentParser(description='Agent trading for pair')
    
    parser.add_argument('-k', '--key',
                        action='store',  # tell to store a value
                        dest='api',  # use `paor` to access value
                        help='Your API Key')
    parser.add_argument('-s', '--secret',
                        action='store',  # tell to store a value
                        dest='secret',  # use `paor` to access value
                        help='Your API Secret')
    parser.add_argument('-u', '--uid',
                        action='store',  # tell to store a value
                        dest='uid',  # use `paor` to access value
                        help='Your FINK UID')
    
    parser.add_argument('-p', '--pair',
                        action='store',  # tell to store a value
                        dest='pair',  # use `pair` to access value
                        help='The Pair to be watched')
    parser.add_argument('-c', '--currency',
                        action='store',  # tell to store a value
                        dest='currency',  # use `pair` to access value
                        help='The currency for the pair')
    
    parser.add_argument('-l', '--limit',
                        action='store',  # tell to store a value
                        dest='limit',  # use `paor` to access value
                        help='Your Buy Limit')
    parser.add_argument('-t', '--time',
                        action='store',  # tell to store a value
                        dest='time',  # use `paor` to access value
                        help='Time Interval')
    
    parser.add_argument('-st', '--standalone',
                        action='store',  # tell to store a value
                        dest='st',  # use `pair` to access value
                        help='If you want to work without a database')
    parser.add_argument('-ex', '--experiment',
                        action='store',  # tell to store a value
                        dest='ex',  # use `pair` to access value
                        help='Experimentation no trading')
    
    parser.add_argument('-ip', '--masterip',
                        action='store',  # tell to store a value
                        dest='ip',  # use `pair` to access value
                        help='IP address of master')
    
    
   
    action = parser.parse_args()
    return action









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
        self.CRMI  = []
        
        self.tenkanSen = []
        self.kijunSen = []
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
        self.entry = 0
        
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
        print("")
        print("Getting Data....")
        
        while True: 
            self.client = Client("o7F2kS6QGIzbMm73iTXmwXlDqbAV4bIHFJcKsPw6dMf447nk7okcRVyprbT8t2Fu","8bzSZklysXWhv4yxU9RKGlVbwmuZuzm0o1VaqjfIs4eZLKGmCeNY3XdSlAeHFj1k") ##binance
            
            ##Convert Pair name 
            BinancePair = self.currency + "BTC"
            
            if (self.TimeIntervalINT == 1):
                result = self.client.get_historical_klines(BinancePair, Client.KLINE_INTERVAL_1MINUTE, "1 Jan, 2018")
            elif (self.TimeIntervalINT == 5):
                result = self.client.get_historical_klines(BinancePair, Client.KLINE_INTERVAL_5MINUTE, "1 Jan, 2018")
            elif (self.TimeIntervalINT == 30):
                result = self.client.get_historical_klines(BinancePair, Client.KLINE_INTERVAL_30MINUTE, "1 Jan, 2018")
            elif (self.TimeIntervalINT == 60):
                result = self.client.get_historical_klines(BinancePair, Client.KLINE_INTERVAL_1HOUR, "1 Jan, 2018")
                
            #print(result)
            self.SortData(result)
            
            
            break
        
        
    def SortData(self,result):
        
         for i in result:
             self.high.append(float(i[2]))
             self.low.append(float(i[3]))
             self.open.append(float(i[1]))
             self.close.append(float(i[4]))
             self.time.append(int(i[0]))
         print("Done")
         print("")
         
         if self.TimeIntervalINT == 60:
             self.lp = len(self.close) - 40
         elif self.TimeIntervalINT == 30:
             self.lp = len(self.close) - 80
         elif self.TimeIntervalINT == 5:
             self.lp = len(self.close) - 480
         elif self.TimeIntervalINT == 1:
             self.lp = len(self.close) - 2400
         
         
             
     
            
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
        
        self.kijunSen *= 0
        
        datalen = len(self.close)
        
        #get kijunSen 
        
        ##first fill in the 0s
        z = 0
        while z <= kPeriod-1:
            self.kijunSen.append(0)
            z+=1
        
        x = kPeriod
        while x <= datalen - 1:
            y = x - kPeriod
            high = 0
            low = 1
            while y <= x:
                if high < self.high[y]:
                    high = self.high[y]
                if low > self.low[y]:
                    low = self.low[y]
                y+=1
                
            self.kijunSen.append((high + low)/2)
            x+=1
            

            
    def GetSMA(self):

        SMAPeriod = 4
        
        self.SMA *= 0
        datalen = len(self.close)
        
        ##first fill in the 0s
        z = 0
        while z <= SMAPeriod-1:
            self.SMA.append(0)
            z+=1
        
        x = SMAPeriod
        while x <= datalen - 1:
            w = 0
            y = x - SMAPeriod
            while y <= x:
                w = float(w+self.close[y])
                y+=1
                
            self.SMA.append(float(w/SMAPeriod))
            x+=1
            
            
        
            
    def GetCRMI(self):
        
        self.CRMI  *= 0
        datalen = len(self.kijunSen)
  
         ## now get the differences    
        z = 0
        while z <= datalen - 1:
            if (self.SMA[z] == 0 or self.kijunSen[z] == 0):
                self.CRMI.append(1)
            else:
                self.CRMI.append(float(self.SMA[z]/self.kijunSen[z]))
            z+=1
        
            
        
        
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
        
        self.SMA *= 0
        self.GetBalance()
        self.GetSMA()
            
        print("Balance: %.9f" % (self.balance))
        print("**************************************")
        print(" ")
        self.hold = 0

        if ((self.hold == 0 and self.Order == 2) or self.rl == 0):
            self.Optimise() ##let's optimize to find the best parameters before any trades
        
        if (self.ready == 1 and self.rl != 0 ):
            
            self.GetIchT(self.IchtPeriod)
            self.GetCRMI()
        
            print("Last data time: %s") % self.time[-1]
            print("close is: %.9f" % self.close[-1])  
            print("open is:  %.9f" % self.open[-1])  
            print("sma is:   %.9f" % self.SMA[-1]) 
            print("Length of data: %d") % len(self.close)
            print(" ")
            
            print("******* TA *******")
            print("Momentum: %.9f, Floor: %.9f") % (self.CRMI[-1], self.BestFloor)
            print("")
            
            if (self.CRMI[-1] <= self.BestFloor):
                self.state = 1 ##buy
            else:
                self.state = 0 ##to prevent buying or selling when we're not meant to sell
                
            if (self.ex == 0):
                self.MaintainOrder()
            else:
                self.PlotData()
                print("Experiment Done")
     
        else:
            print("NOT READY TO TRADE")
            
            
            
            
    def Optimise(self):
        
        m = 0 
        datalen = len(self.close)
        
        print(" ")
        print("...Optimizing Params, Figuring out what's the best for us....")
        print("")
        
        StartTime = datetime.datetime.now()
        
        if self.TimeIntervalINT == 60:
            IchtPeriodMax = 36
            IchtPeriodSteps = 4
        elif self.TimeIntervalINT == 30:
            IchtPeriodMax = 72
            IchtPeriodSteps = 8
        elif self.TimeIntervalINT == 5:
            IchtPeriodMax = 432
            IchtPeriodSteps = 48
        elif self.TimeIntervalINT == 1:
            IchtPeriodMax = 2160
            IchtPeriodSteps = 240
        
        IchtPeriod = 0
        while IchtPeriod <= IchtPeriodMax:
            IchtPeriod += IchtPeriodSteps 
            self.GetIchT(IchtPeriod)
            self.GetCRMI()
            
            #rl = 1.006
            rl = 1.018
            while rl < 1.02:
                rl += 0.002 ##starting at 0.008
                middle = statistics.median(self.CRMI)
                Floor = min(self.CRMI)
                
                while Floor < middle:
                    Floor += 0.01
                    i = datalen-self.lp
                    w = 0.0 ##wins
                    l = 0 ##lossess
                    x = 0 ##second position
                    r = 0 ##return
                    while i <= datalen-2:
                        if self.CRMI[i] <= Floor and self.close[i] > self.low[i+1]:
                            x = i + 1
                            r = 0
                            while x <= datalen-2:
                                if (self.close[i] * rl) < self.high[x+1]:
                                    r = 1
                                    break
                                x+=1
                            if r > 0:
                                w += rl
                            else:
                                l += 1
                                break ##there's a loss stop, get new parameters
                        i+=1
                        
                    print("Ichimoku Period at: %d Return Limit at: %.9f Floor at: %.9f ||||||||||") %(IchtPeriod, rl, Floor)
                    print("wins: %d, loss: %d") %(w, l)
                        
                    if (l == 0 and w > m):
                        m = w
                        self.sl = 0.7
                        self.rl = rl
                        self.BestFloor = Floor
                        self.IchtPeriod = IchtPeriod
                
        
        
                          
        OptimizeFinishTime = datetime.datetime.now()
        
        tdiff = OptimizeFinishTime - StartTime 
        self.optimizeTime = int(tdiff.total_seconds())
        print("")
        print("")
        print("______________DONE___________________")
        print("")
        print("%d seconds for Optimizing") % (self.optimizeTime)
        
        
        
        if (m > 0):
            self.ready = 1
            print("")
            print("Stop Loss:  %.2f percent") % ((1-self.sl) * 100)
            print("Return Limit:  %.2f percent") % ((self.rl - 1) * 100)
            print("FLOOR: %.9f") % self.BestFloor
            print("Ichimoku Period: %d") % self.IchtPeriod
            print("")
            print("____READY TO TRADE NOW_____________")
            print("")
        else:
            self.ready = 0
            
            
    
            
            
    def UploadData(self):
        
        entry = self.CRMI[-1] / self.BestFloor

        cursor = self.conn.cursor()
        query = "UPDATE Pairs SET TradeSignal = %d, HoldBTC=%.9f, PID = %d, ReturnLimit = %.9f, StopLoss = %.9f, Position = %.9f, Entry = %.9f, OptimizeTime = %d WHERE Pair = '%s'" % (self.ready, self.balanceBTC, self.pid,self.rl,self.sl,self.position,entry,self.optimizeTime,self.pairName)

        try:
            cursor.execute(query)
            self.conn.commit()
        
        except MySQLdb.Error as error:
            print(error)
            self.conn.rollback()
            self.conn.close()
            
            
    def PlotData(self):
        
        import matplotlib.pyplot as plt
        
        CRMI = []
        timeD = []
        close = []
        
        BuyOrder = []
        BuyTime = []
        SellOrder = []  
        SellTime = []
        BuySignals = []
        BuySignalsTime = []
        
        
                    
        datalength = len(self.close)
                    
        i = datalength-self.lp
        
        
        print("")
        print("Ploting.....")
        profit = 0
        loss = 0
        
        
        while i<=datalength-2:
            if self.CRMI[i]<=self.BestFloor:
                initial=self.close[i]
                BuySignals.append(initial)
                BuySignalsTime.append(self.time[i])
                x = i
                while x<=datalength-2:
                    if self.CRMI[x]>self.BestFloor:
                        initial=0
                        break
                    if initial>self.low[x+1]:
                        BuyOrder.append(initial)
                        BuyTime.append(self.time[x])
                        break
                    x+=1
                if (initial): 
                    x+=1
                    while x<=datalength-2:
                        if initial*self.rl<self.high[x+1]:
                            r=self.rl-1.005
                            SellOrder.append(initial*self.rl)
                            SellTime.append(self.time[x])
                            break
                        #elif self.close[x] <= initial * self.sl:
                        #    r=(self.close[x]/initial)-1.005
                        #    SellOrder.append(self.close[x])
                        #    SellTime.append(self.time[x])
                        #    break
                        else:
                            r=(self.close[x]/initial)-1.005
                        x+=1
                    if r<0:
                        loss+=1
                    profit+=r      
                i = x
            i+=1 
                
        hold = float((float(self.close[-1]) / float(self.close[len(self.close)-1-self.lp]) - 1.005) * 100)
        
        print("")
        print("Total Best return = %.9f " % (profit*100))
        print("If HOLD = %.9f ") % hold
        print("")
        
        
    
 
            
        i = datalength-self.lp
        while i<=datalength-1:
            close.append(self.close[i])
            CRMI.append(self.CRMI[i])
            timeD.append(self.time[i])
            i+=1
            
                    
        
        #plt.plot(self.time, self.close, label='Closing Price',color='black', linewidth=0.1)
        plt.figure(1)
        
        plt.subplot(211)
        plt.plot(BuyTime, BuyOrder, '^', markersize=7, color='g', label = 'Bought')
        plt.plot(SellTime, SellOrder, 'v', markersize=7, color='r', label = 'Sold')
        plt.plot(BuySignalsTime, BuySignals, '^', markersize=3, color='blue', label ='Buy Signal')
        plt.plot(timeD, close, label='Close',color='black',linewidth=0.3)
        
        
       # plt.plot(timeD, SMA, color = 'red', label='SMA')
       # plt.plot(timeD, kijunSen, color = 'blue', label='kijunSen')
        
        plt.title(self.pairName)
        plt.ylabel('price')
        plt.xlabel('period')
        
        
 
        plt.legend(loc=0)

        plt.subplot(212)
        #plt.plot(timeD, IchD, color = 'red', label='ICHD')
        plt.plot(timeD, CRMI, color = 'red', label='Difference')
        #plt.plot(timeD, SMAIchDSMA, color = 'blue', label='SMA')
        plt.title("Custom Relative Momentum Indicator")
        plt.xlabel('period')
        
        #plt.subplot(313)
        #plt.plot(timeD, RollingFib, color = 'blue')
        #plt.title("Fib Retracement Level")
        #plt.xlabel('period')
        
        
        plt.show()
        
        
                        
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
        
        
        
       
    
entry = GetEntry() 
pair = MyPair(entry)
pair.SetParams(entry)

if (pair.ex == 1):
    pair.Trade()
else:

    while(True):
        pair.Trade()
        time.sleep(50) ## should be enough delay to not throttle the api






