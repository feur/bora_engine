from bittrex.bittrex import *
import argparse
from statistics import mean
import os
import time
import datetime
import MySQLdb
import subprocess
import psutil
from settings import *


def GetEntry():
    parser = argparse.ArgumentParser(description='Process TA for pair')
    parser.add_argument('-k', '--key',
                        action='store',  # tell to store a value
                        dest='api',  # use `paor` to access value
                        help='Your API Key')
    parser.add_argument('-s', '--secret',
                        action='store',  # tell to store a value
                        dest='secret',  # use `paor` to access value
                        help='Your API Secret')
    parser.add_argument('-l', '--limit',
                        action='store',  # tell to store a value
                        dest='limit',  # use `paor` to access value
                        help='Your Buy Limit')
    parser.add_argument('-m', '--buybuffer',
                        action='store',  # tell to store a value
                        dest='buyBuffer',  # use `paor` to access value
                        help='your buy buffer')
    parser.add_argument('-n', '--sellbuffer',
                        action='store',  # tell to store a value
                        dest='sellBuffer',  # use `paor` to access value
                        help='your sell buffer')
    parser.add_argument('-t', '--time',
                        action='store',  # tell to store a value
                        dest='time',  # use `paor` to access value
                        help='Time Interval')
    parser.add_argument('-ex', '--simulate',
                        action='store',  # tell to store a value
                        dest='ex',  # use `paor` to access value
                        help='Simulation on or off')
    parser.add_argument('-r', '--reset',
                        action='store',  # tell to store a value
                        dest='r',  # use `paor` to access value
                        help='reset tables')
   
    action = parser.parse_args()
    return action



class Account(object): 
    
    def __init__(self):
        
        self.conn = MySQLdb.connect(Fink_DB_HOST,Fink_DB_USER,Fink_DB_PW,Fink_DB_NAME)
        self.edel = MySQLdb.connect(Edel_DB_HOST,Edel_DB_USER,Edel_DB_PW,Edel_DB_NAME) ##connect to DB
        
        
    def SetParams(self,entry):
        print("Applying parameters")
        print(" " )
        
        if (entry.api != None and entry.secret != None):
            self.api = entry.api
            self.secret = entry.secret
            self.account = Bittrex(self.api, self.secret, api_version=API_V2_0) ##now connect to bittrex with api and key
        else:
            print("Please insert api & secret key")
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
            self.TimeInterval = "FIVEMIN"
            self.TimeIntervalINT = 5
            print("Time interval set to default 5 minutes")
            
        if (entry.limit != None):
            self.BuyLimit = float(entry.limit)
            print("Buy buffer set to : %.9f") % self.BuyLimit
        else:
            self.BuyLimit = 0.02
            print("Buy Buffer set to default 0.02 BTC")
            
        if (entry.buyBuffer != None):
            self.BuyBuffer = float(entry.buyBuffer)
            print("Buy buffer set to : %.9f") % self.BuyBuffer
        else:
            self.BuyBuffer = 0.95
            print("Buy Buffer set to default 5%")
            
            
        if (entry.sellBuffer != None):
            self.SellBuffer = float(entry.sellBuffer)
            print("Sell buffer set to : %.9f") % self.SellBuffer
        else:
            self.SellBuffer = 1.03
            print("Sell Buffer set to default 3%")
            
        if (entry.ex != None):
            self.ex = 1
            print("experiment mode on all agents")
        else:
            self.ex = 0
            
        if (entry.r != None):
            print("clearing tables")
            self.Reset()
            
        print(" ")    
        print("___Parameters Applied !_____")
        print(" " )
            
            
            
            
    def Reset(self):    
   
        '''
        Will get all the Pairs that are currently registerd by Edel and populate 
        Fink DB
        '''
    
        ###First make sure all Tables are clear
        cursor = self.conn.cursor()    
            
        try:       
            cursor.execute ("DELETE FROM `Pairs`")
            self.conn.commit()
            
            cursor.execute ("DELETE FROM `AccountBalance`")
            self.conn.commit()
        
            cursor.execute ("DELETE FROM `AccountHistory`")
            self.conn.commit()
        
            cursor.execute ("DELETE FROM `SignalLog`")
            self.conn.commit()
            
        except MySQLdb.Error as error:
            print(error)
            self.conn.rollback()
            self.conn.close()
        
        
        ###Get a list of all Pairs and Currency
        cursor = self.edel.cursor() 
        print("inserting pairs")
        try:
            cursor.execute ("SELECT `Pair`, `Currency` FROM `Pair_List` WHERE 1 ")
            data = cursor.fetchall()
        
            cursor = self.conn.cursor()
            
            for i in range(len(data)):
                
                ##now insert the list into the local database 
            
                query = "INSERT INTO `Pairs`(`Pair`, `Currency`) VALUES ('%s','%s')" % (str(data[i][0]),str(data[i][1]))
    
                try: 
                    cursor.execute(query)
                    self.conn.commit()
    
                except MySQLdb.Error as error:
                    print(error)
                    self.conn.close()
                    
        except MySQLdb.Error as error:
            print(error)
            self.edel.close()
            
        print("Done......!")
            
            
    def StartAccount(self):
        cursor = self.conn.cursor()
    
        try:       
            cursor.execute ("SELECT PID FROM `Components` WHERE Unit='account'")
            pid = cursor.fetchone() #find PID for Unit
        
            if psutil.pid_exists(pid[0]):
                print("account tracker is still running with pid %d" % (pid[0]))
            else:
                print("re-running account tracker ecause PID %s doesn't exist" % (pid[0]))
                process = subprocess.call("python ~/Fink/source/account.py -k" + self.api + "-s" + self.key +" > /dev/null 2>&1 & ",  shell=True)
                    
        except MySQLdb.Error as error:
            print(error)
            self.conn.close()  
            
            
            
    def StartAgent(self, pair):
    
    ##get a list of all Pairs in database and find it's pid and check it     
        cursor = self.conn.cursor()
        query = "SELECT `PID` FROM `Pairs` WHERE Pair='%s'" % (pair)
  
        try:
            cursor.execute(query)
            data = cursor.fetchone()
            
            if psutil.pid_exists(data[0]):
                print("agent for %s is still running with pid %d" % (pair, data[0]))
            else:
                print("Agent with PID: %s is not running, re-running agent for this pair %s" % (data[0],pair))
                agent = subprocess.call("python ~/Fink/source/fink.py " + "-p " + pair + "-k " + self.api + "-s " + self.secret + "-t " + self.time + "-m " + self.buyBuffer + "-n " + self.sellBuffer + "-ex " + self.ex + " > /dev/null 2>&1 & ",  shell=True)
   
        except MySQLdb.Error as error:
            print(error)
            self.conn.close()
              
                
##program start here
                
pid = os.getpid()  ##Get process pid
entry = GetEntry() ##Get params
ListofPairs = []   ##list of Pairs, e.g. BTC-ADA, ETH-ADA
ListofCurrencies= [] ##list of Currencies e.g. ADA, OMG

print("pid is: %d" % pid)


PersonalAccount = Account()
PersonalAccount.SetParams(entry)


##get a list of all Pairs in database    

try:
    cursor.execute ("SELECT `Pair`, `Currency` FROM `Pairs` WHERE 1")
    data = cursor.fetchall()
    
    
    for i in range(len(data)):
        ListofPairs.append(str(data[i][0]))
        ListofCurrencies.append(str(data[i][1]))
          
except MySQLdb.Error as error:
    print(error)
    PersonalAccount.conn.close()
    

while True:
     
    print(" ")
    print("Checking account tracker:")
    PersonalAccount.StartAccount()
    print(" ")
    print("Checking all Fink agents:")
    print(" ")
    for i in range(len(ListofPairs)):
        PersonalAccount.StartAgent(ListofPairs[i])
    print("______________________________________________________")
    
    
    time.sleep(60)
