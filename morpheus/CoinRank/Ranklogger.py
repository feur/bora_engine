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


    def GetCoinData(self):
        
        ##get listings 
        x = self.market.listings()
        
        print(self.coins)
        
        for coin in self.coins:
            for data in x['data']:
                if data["symbol"] == coin:
                    ticker = self.market.ticker(int(data["id"]), convert='AUD') ##get ticker data
                    rank = ticker["data"]["rank"]
                    print "Symbol: %s rank: %d" % (coin,rank)
                    if rank < 80:
                        zone = 0
                    elif rank <= 120 and rank >= 80:
                        zone = 1
                    else:
                        zone = 2
                    self.LogCoinData(coin,rank,zone) ##log it into db
                    time.sleep(5) ##rate limit to 1 minute
                    
        

    def LogCoinData(self,symbol,rank,zone):
        
        ts = time.time()
        timestamp = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')
        cursor = self.db.cursor()

        log = "INSERT INTO `CapLog`(`SYMBL`, `RANK`, `ZONE`, `TIME`) VALUES ('%s',%d,%d,'%s')" % (symbol,rank,zone,timestamp)
        main = "UPDATE `Coinlist` SET `Rank`=%d,`Zone`=%d,`UpdateTime`='%s' WHERE Coin = '%s'" % (rank,zone,timestamp,symbol)
        ##log signal 
        try:
            cursor.execute(log)
            self.db.commit()
            cursor.execute(main)
            self.db.commit()

        except MySQLdb.Error as error:
            print(error)
            self.db.rollback()
            self.db.close()
            

coinmarketcap = CoinMarket()
coinmarketcap.GetCoinList()

while (True): 
    coinmarketcap.GetCoinData()
    time.sleep(3600) ##sleep for 1 hour
