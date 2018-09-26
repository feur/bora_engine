import time
import os
import MySQLdb
import time
import datetime

from coinmarketcap import Market

class CoinMarket(object):

    def __init__(self):
        
        ##Get process pid
        self.pid = os.getpid()  
        print("pid is: %d" % self.pid)
        
        self.db = MySQLdb.connect("138.197.194.3","Morph","O3bh8gEtZBGsEhxR","CoinCap") ##connect to DB
        self.market = Market()
        
    def GetCoinSignal(self):
        ##get listings 
        x = self.market.listings()

        ##So far we're just logging movement...
        for data in x['data']:
            position = self.GetZoneMovement(data["symbol"])
            if (position[0] > position[1]): ##pair has moved up
                print("Symbol: %s has moved up") % data["symbol"]
                self.LogMovementSignal(data["symbol"],position[0],"up")
            elif (position[0] < position[1]): ##pair has moved down
                self.LogMovementSignal(data["symbol"],position[0],"down")
                print("Symbol: %s has moved down") % data["symbol"]
            else:
                print("Symbol: %s no movement") % data["symbol"]
        
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
coinmarketcap.GetCoinSignal()






