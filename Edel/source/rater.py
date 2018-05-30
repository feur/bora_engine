from bittrex.bittrex import *
import argparse
from statistics import mean
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
        self.conn = MySQLdb.connect(DB_HOST,DB_USER,DB_PW,DB_NAME)
        
        ##insert PID into Database
        query = "UPDATE `Components` SET `PID`=%d WHERE Unit='Rater'" % (self.pid)
        cursor = self.conn.cursor()

        try:
            cursor.execute(query)
            self.conn.commit()
        
        except MySQLdb.Error as error:
            print(error)
            self.conn.rollback()
            self.conn.close()
                     
    
     
    def GetData(self,pair): 
        
        self.EMA = [0,0,0,0]  ##55,21,13,8
        self.data = []
        
        while True: 
            self.account = Bittrex("f5d8f6b8b21c44548d2799044d3105f0", "b3845ea35176403bb530a31fd4481165", api_version=API_V2_0)
            data = self.account.get_candles(pair, tick_interval=TICKINTERVAL_HOUR)
        
            if (data['success'] == True and data['result']):
                self.pairName = pair
                self.Rawdata = data['result']
                
                ##filter Data for 4 hour period  
                
                offset = (len(self.Rawdata) - 1) % 4
                
                while (offset < len(self.Rawdata)):                    
                    self.data.append(self.Rawdata[offset])
                    offset += 4
                    
                
                self.current = self.data[-1]
                print("Current 4hr price: %.9f for pair %s" % (self.current['C'],self.pairName))
                
                break

    
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
        
        if (self.diNeg[-1] > 20 or self.diPos[-1] > 20): ## both trends are significatn
            
            if (self.diNeg[-1] > self.diPos[-1]): ##Downtrend
                self.Direction = 0 
            elif (self.diNeg[-1] == self.diPos[-1]): ##possible crossover
                self.Direction = 0
            else:
                self.Direction = 1 ##uptrend 
                
        else:
            self.Direction = 1 ##no determined direction
              
           
        print("Direction is: %d" % self.Direction)   
      

    def GetIchState(self):
        
        
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
                 
    
        print("IchState: %d"% self.IchState)
                
      
            
    def GetRating(self):
        
        self.momentum = GetMomentum(self.data)    
        print("Momentum: %.9f" % self.momentum)
        self.rating = self.momentum * (self.diPos[-1] - self.diNeg[-1])
        
        print("Rating is %.9f" % self.rating)
        
        if (self.IchState == 1 and self.EMATrend == 1 and self.rating > 0):
            self.watch = 1
            print("Pair needs to be watched")
        else:
            self.watch = 0
            print("Pair does not need to be watched")
        
    
    def UploadData(self):
    
        cursor = self.conn.cursor()
        query = "UPDATE `Pair_List` SET Rating = %d, Watch = %d WHERE Pair = '%s'" % (self.rating,self.watch,self.pairName)

        try:
            cursor.execute(query)
            self.conn.commit()
        
        except MySQLdb.Error as error:
            print(error)
            self.conn.rollback()
            self.conn.close()
                     
    
                      
                
    
##program start here
CurrentPair = MyPair()
ListofPairs = []     ##list of Pairs, e.g. BTC-ADA, ETH-ADA
ListofCurrencies= [] ##list of Currencies e.g. ADA, OMG

cursor = CurrentPair.conn.cursor()
        
 ##Get list of pairs
print("getting pairs")

try:
    cursor.execute ("SELECT * from Pair_List")
    data = cursor.fetchall()
        
    for i in range(len(data)):
        ListofPairs.append(str(data[i][0]))
       
        
except MySQLdb.Error as error:
    print(error)
    conn.close()    


while True:
    
    ## for every pair
    for i in range(len(ListofPairs)):
        CurrentPair.GetData(ListofPairs[i]) ##get 4 hour data for Pair
        CurrentPair.GetTrend()              ##get EMA Trend and Direction
        CurrentPair.GetIchState()           ##get ICH 
        CurrentPair.GetRating()             ##get Rating
        CurrentPair.UploadData()            ##upload data
    
    time.sleep(60)



