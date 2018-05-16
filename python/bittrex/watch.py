from bittrex.bittrex import *
import argparse
from statistics import mean
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

    def __init__(self,entry,conn):
        
        self.pid = os.getpid()  ##Get process pid
        print("pid is: %d" % self.pid)
        
        self.BuyLimit = 0.15
        self.TimeInterval = "FIVEMIN"
        
        cursor = conn.cursor()
        query = "UPDATE Pairs SET `IchState`= NULL, PID = %d WHERE Pair = '%s'" % (self.pid,entry.pair) ##Null IchState, put in PID and entry pair

        try:
            cursor.execute(query)
            conn.commit()
    
        except MySQLdb.Error as error:
            print(error)
            conn.rollback()
            conn.close()
    

     
    def GetData(self,entry): 
        
        self.EMA = [0,0,0,0]  ##55,21,13,8
        
        while True: 
            self.account = Bittrex("f5d8f6b8b21c44548d2799044d3105f0", "b3845ea35176403bb530a31fd4481165", api_version=API_V2_0)
            data = self.account.get_candles(entry.pair, tick_interval=TICKINTERVAL_FIVEMIN)
        
            if (data['success'] == True and data['result']):
                self.pairName = entry.pair
                self.data = data['result']
                self.current = self.data[-1]
                self.entry = entry
                break

    
    def GetTrend(self,conn):
        """
        
        1. Get Di+ (self.diPos)
        2. Get Di- (self.diNeg)
        3. Define Trend (self)
        4. Get DAX
        
        trend --> 0,1 ,2 
        0 when (di- > 20) && (di- > di+)  [down trend]
        1 when (di- < 20) && (di+ < 20)   [no trend]
        2 when (di+ > 20 ) && (di+ > di-) [up trend]
        
        To get di+
            1. Get TrMax --> self.trMax
            2. Get dmPosMax --> self.dmPosMax
            3. self.diPos[i] = (self.dmPosMax[i] / self.trMax[i]) * 100
            
             if (self.EMA[0] == 0):

            cursor = conn.cursor()
            
            query = "SELECT * FROM Pairs WHERE PAIR = '%s'" % (self.pairName)
        
            try:
                cursor.execute (query)
                data = cursor.fetchone()
                
                self.EMA[0] = float(data[2]) ##Previous EMA55
                self.EMA[1]= float(data[3])  ##previous EMA21
                self.EMA[2] = float(data[4]) ##previous EMA13
                self.EMA[3] = float(data[5]) ##previous EMA8
            
            except MySQLdb.Error as error:
                print(error)
           
    
        """
        
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
            
        
        if (self.diNeg[-1] > 20 and self.diPos[-1] > 20): ## both trends are significatn
            
            if (self.diNeg[-1] > self.diPos[-1]): ##Downtrend
                self.Direction = 0 
            elif (self.diNeg[-1] == self.diPos[-1]): ##possible crossover
                self.Direction = 0
            else:
                self.Direction = 1 ##uptrend 
                
        else:
            self.Direction = 1 ##no determined direction
              
           
        print("Direction is: %d" % self.Direction)   
      

    def GetSignal(self,conn):
        
        """
        
        signal --> 0, 1, 2, 3, 4
        self.trend = 1 => self.signal = 2 [no signal]
        crossover = 0 ==> self.signal = 2 [no signal]
        crossover = 1, self.trend = 0, self.InCloud = 0 => self.signal = 0 [sell signal]
        crossover = 1, self.trend = 0 , self.InCloud = 1 => self.signal = 1 [weak sell signal]
        crossover = 1, self.trend = 0 , self.InCloud = 1 => self.signal = 1 [weak sell signal]
        
        
        Initial: 
            1. Find tenkanSen - (mean(high) + mean(low))/2 for 9 periods
            2. find IchimokuAverage - (mean(high) + mean(low) / 2) for 26 periods
            3. senkouA = (tenkanSen + kijunSen) / 2
            4. senkouB - (mean(high) + mean(low) / 2)
   
        
        1. Find crossover 
            Get SigTop where Pair = self.pairName
            
            if kijunSen > tenkanSen
                Top = 1
            elif kijunSen < tenkanSen
                Top = 0
                
            
            if (SigTop == Null) :
                insert Sigtop = Top where Pair = self.pairName
            elif (Top == SigTop) : 
                crossover = 0
            elif (Top < Sigtop or Top > SigTop): 
                crossover = 1
            
                
        2. Get self.InCloud
        
            if ((senkouAPrev > senkouBPrev) and (self.current['H'] < senkouAPrev)) or ((senkouBPrev > senkouAPrev) and (self.current['H'] < senkouBPrev)):
                self.Incloud = 1
            else: 
                self.InCloud = 0
                
        3. Get self.signal 
        
            if self.trend == 1:
                self.signal = 2
            elif self.trend == 0 and self.Incloud == 0 and crossover == 1:
                self.signal = 0
            elif self.trend == 0 and self.Incloud == 1 and crossover == 1:
                self.signal = 1
            elif self.trend == 2 and self.Incloud == 1 and crossover == 1:
                self.signal = 3
             elif self.trend == 2 and self.Incloud == 0 and crossover == 1:
                self.signal = 4
                
        """
        
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
    
        #find previous state of TenkanSen & KijunSen to find Crossover
            
        cursor = conn.cursor()
            
        query = "SELECT * FROM `Pairs` WHERE PAIR = '%s'" % (self.pairName)
        
        try:
            cursor.execute (query)
            data = cursor.fetchone()
                
            IchPrevState = data[6] ##prev IchState 
            
        except MySQLdb.Error as error:
            print(error)
                 
        print("IchState: %d" % (self.IchState) )  
        
        if (IchPrevState >= 0 and self.IchState != IchPrevState):  ##IchPrevState was previoulsy recorded 
            self.crossover = 1
        else: 
            self.crossover = 0
            
            
        print("crossover: %d" % self.crossover)    
        
        
        ##signal is now represented by its strength 
       ## self.signal = ( self.EMATrend + self.crossover ) * self.Direction   ##amplified by confidence of Direction, 
        
        if (self.crossover == 1 and self.IchState == 1):
            if (self.EMATrend == 1 or self.Direction == 1):
                self.signal = 2
            else: 
                self.signal = 0
        elif (self.crossover == 1 and  self.IchState == 0):
            self.signal = 1
        else:
            self.signal = 0 
            
            
        #Log when signals have a buy or sell    
        
        if (self.signal > 0):
            ts = time.time()
            timestamp = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')
            
            query = "INSERT INTO `SignalLog`(`TradeSignal`, `Pair`, `TimeInterval`, `Time`) VALUES (%d,'%s','%s','%s')" % (self.signal,self.pairName,self.TimeInterval,timestamp)
        
            try:
                cursor.execute(query)
                conn.commit()
        
            except MySQLdb.Error as error:
                print(error)
                conn.rollback()
                conn.close()
     
                
    
        print("Signal: %d"% self.signal)
                
      
            
        
    def GetRating(self,conn):
        
        
        self.momentum = GetMomentum(self.data)    
        
        #Get a,b,c,d,e,f from database
        cursor = conn.cursor()
    
        query = "SELECT * FROM Config WHERE PAIR = '%s'" % (self.pairName)
        
        try:
            cursor.execute (query)
            data = cursor.fetchone()
        
            a = float(data[1])
            b = float(data[2])
            c = float(data[3])
            d = float(data[4])
            e = float(data[5])
            f = float(data[6])
        
        except MySQLdb.Error as error:
            print(error)
            
        
        self.fib = GetFib(self.current['C'], a, b, c, d, e, f)
        self.rating = (1-self.fib) * self.momentum
        
        print(self.rating)
        
    
    def UploadData(self,conn):
    
        """
        Insert self.rating into Rating 
        Insert self.signal into signal 
        Insert self.PID into PID
    
        UPDATE Pairs SET Rating = 160, TradeSignal = 145, PID = 159 WHERE Pair = 'BTC-ADA';

        """


        cursor = conn.cursor()
        query = "UPDATE Pairs SET Rating = %d,`EMA55`=%.9f,`EMA21`=%.9f,`EMA13`=%.9f,`EMA8`=%.9f,`IchState`=%.9f, TradeSignal = %d, PID = %d WHERE Pair = '%s'" % (self.rating,self.EMA[0],self.EMA[1],self.EMA[2],self.EMA[3],self.IchState,self.signal,self.pid,self.pairName)

        try:
            cursor.execute(query)
            conn.commit()
        
        except MySQLdb.Error as error:
            print(error)
            conn.rollback()
            conn.close()
                     
    def SellPair(self,conn):   
        
        ##get pair and amount to sell
        
        cursor = conn.cursor()
        query = "SELECT Hold, HoldBTC FROM `Pairs` where Pair='%s'" % (self.pairName)
        
        try:
            cursor.execute (query) ##getting a list of Pairs ordered by their signals to work out which one to sell 
            data = cursor.fetchone() 
            
            if (data[1] > 0.01): ##theres some amount being held 
                amount = float(float(data[0]) * 0.95)
            
            print("selling %s of amount %.9f" % (self.pairName, amount))
        
            while True: 
                data = self.account.get_orderbook(self.pairName, depth_type=BOTH_ORDERBOOK) ##check orderbook and complete sell order 
            
                if (data['success'] == True):
                    result = data['result']['buy']
                    SellPrice = float(result[1]['Rate'])
                    
                    print("selling %d at %.9f" % (amount, SellPrice))
                
                    data = self.account.trade_sell(self.pairName, ORDERTYPE_LIMIT, amount, SellPrice, TIMEINEFFECT_GOOD_TIL_CANCELLED,CONDITIONTYPE_NONE, target=0.0) ##now placing sell order
                    if (data['success'] == True):
                        print("Sell Order in place")
                        
                        ## logging action
                        ts = time.time()
                        timestamp = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')
                        cursor = conn.cursor()
                        query = "INSERT INTO `AccountHistory`(`PID`, `Pair`, `Amount`, `Price`, `Action`, `ActionTime`) VALUES (%d,'%s',%d,%.9f,'Sell','%s')" % (self.pid,self.pairName,amount,SellPrice,timestamp)
        
                        try:
                            cursor.execute(query)
                            conn.commit()
        
                        except MySQLdb.Error as error:
                            print(error)
                            conn.rollback()
                            conn.close()
                        
                        break
            
                
               
        except MySQLdb.Error as error:
            print(error)
            conn.close()
            
            
    def GetBuyPosition(self,conn):
        
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
                self.BTCAvailable = float(result['Balance'])
                break
        
        print("BTC balance: %.9f" % self.BTCAvailable)
        
        if (self.BTCAvailable >= self.BuyLimit):
        
            try:
                cursor = conn.cursor()
                cursor.execute ("SELECT Pair, HoldBTC, TradeSignal FROM `Pairs` ORDER BY Rating DESC") ##getting a list of Pairs ord$
                data = cursor.fetchall() 
    
                ##now filter out the list
                for i in range(len(data)):
                    #print("Pair %s has a signal of %d" % (str(data[i][0]), data[i][1]))
                    if (data[i][0] == self.pairName): ##pair is of top ranking
                        self.BuyPosition = 1
                        print("in Buying Position")
                        break
                    elif (data[i][1] <= self.BuyLimit and data[i][2] == 2 ): #The Pair has a buy signal and has room to hold more
                        self.BuyPosition = 0
                        print("not in buying Position")
                        break
            
            except MySQLdb.Error as error:
                print(error)
                conn.close()
        else:
            self.BuyPosition = 0
            print ("not enough balance")
                
    
    
    def BuyPair(self,conn):   
        
        print("buying pair")
         
        while True:
            data = self.account.get_latest_candle(self.pairName, tick_interval=TICKINTERVAL_ONEMIN)
            
            if (data['success'] == True and data['result']):
                result = data['result']
                amount = float(self.BuyLimit/result[0]['C'])
                break
        
        print("buying %s at amount %.9f" % (self.pairName, amount))
        
        while True:
            data = self.account.get_orderbook(self.pairName, depth_type=BOTH_ORDERBOOK)
            
            if (data['success'] == True):
                result = data['result']['buy']
                BuyPrice = float(result[1]['Rate'])
                print("buying %.9f at %.9f" % (amount, BuyPrice))
                
                data = self.account.trade_buy(self.pairName, ORDERTYPE_LIMIT, amount, BuyPrice, TIMEINEFFECT_GOOD_TIL_CANCELLED,CONDITIONTYPE_NONE, target=0.0) ##now placing sell order
                if (data['success'] == True):
                    print("Buy Order in place")
                     ## logging action
                    ts = time.time()
                    timestamp = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')
                    cursor = conn.cursor()
                    query = "INSERT INTO `AccountHistory`(`PID`, `Pair`, `Amount`, `Price`, `Action`, `ActionTime`) VALUES (%d,'%s',%d,%.9f,'Buy','%s')" % (self.pid,self.pairName,amount,BuyPrice,timestamp)
        
                    try:
                        cursor.execute(query)
                        conn.commit()
        
                    except MySQLdb.Error as error:
                        print(error)
                        conn.rollback()
                        conn.close()
                        
                    break
                
    
##program start here

entry = GetEntry() ##Get arguments to define Pair and Fib levels
conn = MySQLdb.connect(DB_HOST,DB_USER,DB_PW,DB_NAME)
pair = MyPair(entry,conn)


while True:  ##Forever loop 

    ##get Data
    pair.GetData(entry)

    print("current price is: %.9f" % pair.current['C'])
    
    pair.GetTrend(conn)
    pair.GetSignal(conn)
    pair.GetBuyPosition(conn)
    
    if (pair.signal == 1):
        pair.SellPair(conn) ##sell signal --> sell pair
    elif (pair.signal == 2 and pair.BuyPosition):
        pair.BuyPair(conn) ##buy signal --> check to buy pair
    
    
    pair.GetRating(conn)
    pair.UploadData(conn)
    
    time.sleep(10) ## enoguh delay for an order to be complete







