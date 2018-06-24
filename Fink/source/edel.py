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
        self.conn = MySQLdb.connect(Fink_DB_HOST,Fink_DB_USER,Fink_DB_PW,Fink_DB_NAME) 
        
        self.TimeInterval = "HOUR"
        self.TimeIntervalINT = 60
        
        ##get api key and secret
        cursor = self.conn.cursor()
        query = "SELECT * FROM `Settings` WHERE 1"
    
        try:
            cursor.execute(query)
            data = cursor.fetchone()
            self.api = data[0]
            self.secret = data[1]
        
        except MySQLdb.Error as error:
            print(error)
        
        ##insert PID into Database
        query = "UPDATE `Components` SET `PID`=%d WHERE Unit='edel'" % (self.pid)
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
        self.pairName = pair
        
        while True: 
            self.account = Bittrex(self.api,self.secret, api_version=API_V2_0)
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
        
        if (self.diNeg[-1] > 20 or self.diPos[-1] > 20): ## both trends are significatn
            
            if (self.diNeg[-1] > self.diPos[-1]): ##Downtrend
                self.Direction = 0 
            elif (self.diNeg[-1] == self.diPos[-1]): ##possible crossover
                self.Direction = 0
            else:
                self.Direction = 1 ##uptrend 
                
        else:
            self.Direction = 0 ##no determined direction
              
           
        print("Direction is: %d" % self.Direction)   
        
        if (self.Direction == 1 and self.EMATrend == 1):
            self.Trend = 1
            print("Pair is on an uptrend")
        else:
            print("Pair is not on an uptrend")
      

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
                
      
            
    def GetActive(self):
        
        #self.momentum = GetMomentum(self.data)    
        #print("Momentum: %.9f" % self.momentum)
        #self.rating = self.momentum * (self.diPos[-1] - self.diNeg[-1])
        
        print("Rating is %.9f" % self.rating)
        
        if (self.IchState == 1 and self.Trend == 1):
            self.active = 1
            print("Pair is active")
        else:
            self.active = 0
            print("Pair is not active")
        
    
    def UploadData(self):
    
        cursor = self.conn.cursor()
        query = "UPDATE `Pairs` SET Active = %d WHERE Pair = '%s'" % (self.active,self.pairName)

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
    CurrentPair.conn.close()    


while True:
    
    ## for every pair
    for i in range(len(ListofPairs)):
        CurrentPair.GetData(ListofPairs[i]) ##get 4 hour data for Pair
        CurrentPair.GetTrend()              ##get EMA Trend and Direction
        CurrentPair.GetIchState()           ##get ICH 
        CurrentPair.GetActive()
        CurrentPair.UploadData()            ##upload data
    
    time.sleep(60)



