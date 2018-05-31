from bittrex.bittrex import *
import argparse
from statistics import mean
import os
import time
import MySQLdb
import subprocess
import psutil
from settings import *


            
def StartAllUnits(conn, listofpairs):
    
    cursor = conn.cursor()
    
    try:       
        cursor.execute ("SELECT * FROM `Components` WHERE 1")
        data = cursor.fetchall() #find PID for Unit
        
        #check if pid is running
        for i in range (len(data)):
            
            if psutil.pid_exists(data[i][1]):
                print("process %s is still running with pid %d" % (data[i][0], data[i][1]))
            else:
                print("re-running process for this component %s" % (data[i][0]))
                process = subprocess.call("python ~/Fink/source/" + data[i][0] + ".py > /dev/null 2>&1 & ",  shell=True)
              
    except MySQLdb.Error as error:
        print(error)
        conn.close()
        
        
def StartAgent(pair,conn):
        
    ##making sure all agents run
        cursor = conn.cursor()
        query = "SELECT PID from Pairs WHERE Pair = '%s'" % (pair)
        
        try:
            cursor.execute (query)
            data = cursor.fetchone() #find PID for PAIR
            
            #check if pid is running
            if psutil.pid_exists(data[0]):
                print("agent for %s is still running with pid %d" % (pair, data[0]))
            else:
                print("re-running agent for this pair %s" % (pair))
                process = subprocess.call("python ~/Fink/source/agent.py " + "-p " + pair + " > /dev/null 2>&1 & ",  shell=True)
               
        except MySQLdb.Error as error:
            print(error)
            conn.close()
        
                

    
##program start here
    
ListofPairs = []   ##list of Pairs, e.g. BTC-ADA, ETH-ADA
ListofCurrencies= [] ##list of Currencies e.g. ADA, OMG

pid = os.getpid()               ##Get process pid
print("pid is: %d" % pid)

conn = MySQLdb.connect(Fink_DB_HOST,Fink_DB_USER,Fink_DB_PW,Fink_DB_NAME) ##connect to DB


##get a list of all Pairs in database        
cursor = conn.cursor()
  
try:
    cursor.execute ("SELECT `Pair`, `Currency` FROM `Pairs` WHERE 1")
    data = cursor.fetchall()
    
    for i in range(len(data)):
        ListofPairs.append(str(data[i][0]))
        ListofCurrencies.append(str(data[i][1]))
          
except MySQLdb.Error as error:
    print(error)
    conn.close()
    


while True: 
    
    StartAllUnits(conn) ##start all components and agents
    for i in range(len(ListofPairs)):
        StartAgent(ListofPairs[i],conn)
    time.sleep(10)
    
   

    



    
