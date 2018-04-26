from bittrex.bittrex import *
import argparse
from statistics import mean
import os
import MySQLdb
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

    def __init__(self, entry):
        """
            {u'C': 3.079e-05, u'H': 3.079e-05, u'L': 3.079e-05, u'O': 3.079e-05, u'BV': 0.04902765, u'T': u'2018-04-13T07:10:00', u'V': 1592.32422805}
            """
            
        while True:  
            account = Bittrex("f5d8f6b8b21c44548d2799044d3105f0", "b3845ea35176403bb530a31fd4481165", api_version=API_V2_0)
            data = account.get_candles(entry.pair, tick_interval=TICKINTERVAL_HOUR)
        
            if (data['success'] == True and data['result']):
                self.pairName = entry.pair
                self.data = data['result']
                self.current = self.data[-1]
                self.entry = entry
                break
            
            
    
    def GetTrend(self):
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
    
        """
               
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
            
              
        if (self.diNeg[-1] > 20) and (self.diNeg[-1] > self.diPos[-1]):
            self.trend = 0 #down trend
        elif (self.diNeg[-1] < 20) and (self.diPos[-1] < 20):
            self.trend = 1  #no trend
        elif (self.diPos[-1] > 20) and (self.diPos[-1] > self.diNeg[-1]):
            self.trend = 2 #up trend
            
           
    #    print("Trend: %d" % self.trend)   
      

    def GetSignal(self):
        
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
        
        period = 9
        
        for x in range (y/period):  
            
            for z in range(y - (x+1)*period, y-(period*x + 1)):
                highest.append(high[z])
                lowest.append(low[z])
                
            self.tenkanSen.append((max(highest) + min(lowest))/2) 
            highest *= 0
            lowest *= 0
                    
         
        period = 26
        
        for x in range (y/period):  
            
            for z in range(y - (x+1)*period, y-(period*x + 1)):
                highest.append(high[z])
                lowest.append(low[z])
                
            self.kijunSen.append((max(highest) + min(lowest))/2) 
            highest *= 0
            lowest *= 0
                    
       
        period = 52
        
        for x in range (y/period):  
            
            for z in range(y - (x+1)*period, y-(period*x + 1)):
                highest.append(high[z])
                lowest.append(low[z])
                
            self.senkouB.append((max(highest) + min(lowest))/2) 
            highest *= 0
            lowest *= 0
            
            
        period = 27
        
        for x in range(period-1):
            self.senkouA.append((self.tenkanSen[x] + self.kijunSen[x])/ 2)
            
            
       # print("red at: %.9f" % self.tenkanSen[0])  
       # print("blue at: %.9f" % self.kijunSen[0])  
        
        #find crossover 
        if (self.tenkanSen[1] > self.kijunSen[1]) and (self.tenkanSen[0] < self.kijunSen[0]):
            self.crossover = 1
        elif (self.tenkanSen[1] < self.kijunSen[1]) and (self.tenkanSen[0] > self.kijunSen[0]):
            self.crossover = 1    
        elif (self.tenkanSen[0] == self.kijunSen[0]): 
            self.crossover = 1 
        else:
            self.crossover = 0
            
     #   print("crossover: %d" % self.crossover)    
        
        
        #find incloud
        
        if ((self.current['C'] < self.senkouA[0]) and (self.current['C'] < self.senkouB[0])):
            self.InCloud = 0
        elif ((self.current['C'] > self.senkouA[0]) and (self.current['C'] > self.senkouB[0])):
            self.InCloud = 2    
        else:
            self.InCloud = 1
            
        print(self.InCloud)
                    
      #  print("cloud: %d"% self.InCloud)
                    
        if self.trend == 1 or self.crossover == 0:  ##no trend or no crossover 
            self.signal = 2 ##no buy or sell signal
        elif self.InCloud == 0:
            if self.crossover and self.trend ==  0:   ##crossover happened with downtrend under the cloud
                self.signal = 0 ##strong sell signal 
            if self.crossover and self.trend == 2:    ##crossover happeend with uptrend under the cloud
                self.signal = 3 ##weak buy signal
        elif self.InCloud == 1:
            if self.crossover and self.trend ==  0:   ##crossover happened with downtrend under the cloud
                self.signal = 1 ##weak sell signal 
            if self.crossover and self.trend == 2:    ##crossover happeend with uptrend under the cloud
                self.signal = 3 ##weak buy signal
        elif self.InCloud == 1:
            if self.crossover and self.trend ==  0:   ##crossover happened with downtrend under the cloud
                self.signal = 3 ##weak sell signal 
            if self.crossover and self.trend == 2:    ##crossover happeend with uptrend under the cloud
                self.signal = 4 ##strong buy signal
        else:
            self.signal = 2 #no buy or sell signal
       
            
        print("signal: %d"% self.signal)    
                
      
            
        
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
        self.rating = self.fib * (self.diPos[-1] + self.diNeg[-1]) * self.momentum
        
        print(self.rating)
        
    
    def UploadData(self,pid,conn):
    
        """
        Insert self.rating into Rating 
        Insert self.signal into signal 
        Insert self.PID into PID
    
        UPDATE Pairs SET Rating = 160, TradeSignal = 145, PID = 159 WHERE Pair = 'BTC-ADA';

        """


        cursor = conn.cursor()
        query = "UPDATE Pairs SET Rating = %d, TradeSignal = %d, PID = %d WHERE Pair = '%s'" % (self.rating,self.signal,pid,self.pairName)
    
        try:
            cursor.execute(query)
            conn.commit()
        
        except MySQLdb.Error as error:
            print(error)
            conn.rollback()
            conn.close()
 
      





##program start here

entry = GetEntry() ##Get arguments to define Pair and Fib levels
pid = os.getpid()  ##Get process pid

print("pid is: %d" % pid)


##Write PID to Database

conn = MySQLdb.connect(DB_HOST,DB_USER,DB_PW,DB_NAME)

cursor = conn.cursor()
query = "UPDATE Pairs SET PID = %d WHERE Pair = '%s'" % (pid,entry.pair)

try:
    cursor.execute(query)
    conn.commit()
    
except MySQLdb.Error as error:
    print(error)
    conn.rollback()
    conn.close()
    

while True:  ##Forever loop 

    pair = MyPair(entry)

    print("current price is: %.9f" % pair.current['C'])
    
    
    pair.GetTrend()
    pair.GetSignal()
    pair.GetRating(conn)
    pair.UploadData(pid,conn)








