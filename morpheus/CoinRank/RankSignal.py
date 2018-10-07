import time
import os
import MySQLdb
import datetime

from coinmarketcap import Market

class CoinMarket(object):

    def __init__(self):
        
        ##Get process pid
        self.pid = os.getpid()  
        print("pid is: %d" % self.pid)
        
        self.db = MySQLdb.connect("138.197.194.3","Morph","O3bh8gEtZBGsEhxR","CoinCap") ##connect to DB
        self.market = Market()
        self.coins = []
        
        
    def GetCoinList(self):
        
        cursor = self.db.cursor()
        query = "SELECT Coin FROM `Coinlist` WHERE 1" 

        try:
            cursor.execute(query)
            data = cursor.fetchall()   
            
            for i in range(len(data)):
                self.coins.append(str(data[i][0]))
       
        except MySQLdb.Error as error:
            print(error)
            self.db.conn.close()    

        
    def GetCoinSignal(self):
        
        ##So far we're just logging movement...
        for coin in self.coins:
            position = self.GetZoneMovement(coin)
            if (position[0] > position[1]): ##pair has moved up
                print("Symbol: %s has moved up") % coin
                self.LogMovementSignal(coin,position[0],"up")
            elif (position[0] < position[1]): ##pair has moved down
                self.LogMovementSignal(coin,position[0],"down")
                print("Symbol: %s has moved down") % coin
            else:
                print("Symbol: %s no movement") % coin
        
        time.sleep(3600) ##wait for 1 hour
        
    def GetZoneMovement(self,symbol):
        
        lookback = 2 ##how many periods you'd like ot look back (1 period should be 1 hour)
          
        cursor = self.db.cursor()
        query = "SELECT `ZONE` FROM `CapLog` WHERE SYMBL = '%s' ORDER BY TIME desc limit %d" % (symbol,lookback)
  
        try:
            cursor.execute(query)
            data = cursor.fetchall()
            return int(data[0][0]), int(data[-1][0]) ##return the current and previous zone
                
        except MySQLdb.Error as error:
            print(error)
            self.db.close()
            
    def LogMovementSignal(self,symbol,zone,direction):
            
        ts = time.time()
        timestamp = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')
        cursor = self.db.cursor()
        
        query = "INSERT INTO `SignalLog`(`SYMBL`, `Zone`, `Direction`, `TIME`) VALUES ('%s',%d,'%s','%s')" % (symbol,zone,direction,timestamp)
        
        ##log signal 
        try:
            cursor.execute(query)
            self.db.commit()
                
        except MySQLdb.Error as error:
            print(error)
            self.db.rollback()
            self.db.close()
          
    
        
coinmarketcap = CoinMarket()
coinmarketcap.GetCoinList()

while (True):
    time.sleep(3600) ##wait till we get a proper list of coins first
    coinmarketcap.GetCoinSignal()






