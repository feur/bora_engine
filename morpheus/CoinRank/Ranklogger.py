  GNU nano 2.5.3                                                        File: Ranklogger.py                                                                                                                        

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

    def GetCoinData(self):
        ##get listings 
        x = self.market.listings()

        for data in x['data']:
            ticker = self.market.ticker(int(data["id"]), convert='AUD') ##get ticker data
            print "Symbol: %s rank: %d" % (data["symbol"],ticker["data"]["rank"])
            self.LogCoinData(data["symbol"],ticker["data"]["rank"]) ##log it into db
            time.sleep(2) ##rate limit to 30 / min, so 2 seconds delay 

        #time.sleep(3600) ##wait for 1 hour

    def LogCoinData(self,symbol,rank):

        if rank < 100:
            zone = 0
        elif rank <= 120 and rank >= 100:
            zone = 1
        else:
            zone = 2

        ts = time.time()
        timestamp = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')
        cursor = self.db.cursor()

        query = "INSERT INTO `CapLog`(`SYMBL`, `RANK`, `ZONE`, `TIME`) VALUES ('%s',%d,%d,'%s')" % (symbol,rank,zone,timestamp)

        ##log signal 
        try:
            cursor.execute(query)
            self.db.commit()

        except MySQLdb.Error as error:
            print(error)
            self.db.rollback()
            self.db.close()

coinmarketcap = CoinMarket()
coinmarketcap.GetCoinData()
