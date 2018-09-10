import argparse
import time
import MySQLdb
import os
import time
import datetime
from bittrex.bittrex import *
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
    parser.add_argument('-u', '--uid',
                        action='store',  # tell to store a value
                        dest='uid',  # use `paor` to access value
                        help='Your FINK UID')
    parser.add_argument('-l', '--limit',
                        action='store',  # tell to store a value
                        dest='limit',  # use `paor` to access value
                        help='Your Buy Limit')
    parser.add_argument('-t', '--time',
                        action='store',  # tell to store a value
                        dest='time',  # use `paor` to access value
                        help='Time Interval')
    parser.add_argument('-r', '--reset',
                        action='store',  # tell to store a value
                        dest='r',  # use `paor` to access value
                        help='reset tables')
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
    
    parser.add_argument('-id', '--systemid',
                        action='store',  # tell to store a value
                        dest='id',  # use `pair` to access value
                        help='System ID')
    
    
    
   
    action = parser.parse_args()
    return action

class Account(object): 
    
    def __init__(self):
    
        self.edel = MySQLdb.connect(Edel_DB_HOST,Edel_DB_USER,Edel_DB_PW,Edel_DB_NAME) ##connect to DB
        
        
    def SetParams(self,entry):
        print("Applying parameters")
        print(" " )
        
        if (entry.api != None and entry.secret != None and entry.uid != None):
            self.api = entry.api
            self.secret = entry.secret
            self.UID = entry.uid
        else:
            print("Please insert api & secret key & UID")
            quit()
            
        if (entry.id != None):
            self.id = int(entry.id)
            
        else:
             self.id = 0
             print("Assigned to default MASTER")
            
        if (entry.r != None):
            print("clearing tables")
            self.Reset()
            
        if (int(entry.st) > 0 and int(entry.ex) > 0): ##system not in standalone mode
            print("System in standalone or experiment mode, you cannot use this program to start agents")
            exit()
            
            
        if (entry.ip != None): ##slave with ip given
            self.ip = entry.ip 
        else:
            self.ip = "localhost"
            
        print("System ID of %d") % self.id
        print("Buy limit set to: %.9f") % float(entry.limit)
        print("Trading interval set to: %d") % int(entry.time)
        
        print("Database set to %s") % self.ip
        
        self.conn = MySQLdb.connect(self.ip,Fink_DB_USER,Fink_DB_PW,Fink_DB_NAME) 
            

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
            
            cursor.execute ("DELETE FROM `ExLog`")
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
            
            
    def StartAccount(self, entry):
        cursor = self.conn.cursor()
    
        try:       
            cursor.execute ("SELECT PID FROM `Components` WHERE Unit='account'")
            pid = cursor.fetchone() #find PID for Unit
            print(pid[0])
            exist = psutil.pid_exists(pid[0])
            if (exist == 1):
                print("account tracker is still running with pid %s" % (pid[0]))
            else:
                print("re-running account tracker because PID %d doesn't exist" % (pid[0]))
                process = subprocess.call("~/Fink/source/account/account -k " + entry.api + " -s " + entry.secret +" > /dev/null 2>&1 & ",  shell=True)
              
        except MySQLdb.Error as error:
            print(error)
            self.conn.close()  
            
            
            
    def StartAgent(self, pair, currency, entry):
    
    ##get a list of all Pairs in database and find it's pid and check it     
        cursor = self.conn.cursor()
        query = "SELECT `PID` FROM `Pairs` WHERE Pair='%s'" % (pair)
  
        try:
            cursor.execute(query)
            data = cursor.fetchone()
            print(data[0])
            exist = psutil.pid_exists(data[0])
            if (exist == 1):
                print("agent for %s is still running with pid %s" % (pair, data[0]))
            else:
                print("Agent with PID: %s is not running, re-running agent for this pair %s" % (data[0],pair))
                agent = subprocess.call("~/Fink/source/fink/fink " + " -p " + pair + " -c " + currency + " -k " + entry.api + " -s " + entry.secret + " -u " + entry.uid + " -t "
                + entry.time + " -l " + entry.limit  + " -st " + entry.st  + " -ex " + entry.ex +  " -ip " + entry.ip
                + " > /dev/null 2>&1 & ",  shell=True)
                
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

cursor = PersonalAccount.conn.cursor()
query = "SELECT * FROM Pairs Where ID = %d" % (PersonalAccount.id)

try:
    cursor.execute(query)
    data = cursor.fetchall()   
    for i in range(len(data)):
        ListofPairs.append(str(data[i][0]))
        ListofCurrencies.append(str(data[i][1]))
       
        
except MySQLdb.Error as error:
    print(error)
    PersonalAccount.conn.close()    


print("Number of pairs: %d") % len(ListofPairs)
print(" ")


print(" ")
if (PersonalAccount.id == 0): ##IF MASTER, as master handles account logging
    print("Checking account tracker:")
    PersonalAccount.StartAccount(entry)
print(" ")
print("Checking all Fink agents:")
print(" ")
for i in range(len(ListofPairs)):
    PersonalAccount.StartAgent(ListofPairs[i],ListofCurrencies[i],entry)
print("______________________________________________________")

    