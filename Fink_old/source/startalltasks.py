from bittrex.bittrex import *
import argparse
from statistics import mean
import os
import time
import MySQLdb
import subprocess
import psutil
from settings import *


            
def StartAllUnits(conn):
    
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
        
        
def StartAgents(conn):
    
    ##get a list of all Pairs in database and find it's pid and check it        
    cursor = conn.cursor()
  
    try:
        cursor.execute ("SELECT `Pair`, `PID` FROM `Pairs` WHERE 1")
        data = cursor.fetchall()

        for i in range(len(data)):
            
            pair = str(data[i][0])
            
            if psutil.pid_exists(data[i][1]):
                print("agent for %s is still running with pid %d" % (pair, data[i][1]))
            else:
                print("Agent with PID: %s is not runnign, re-running agent for this pair %s" % (data[i][1],pair))
                agent = subprocess.call("python ~/Fink/source/agent.py " + "-p " + pair + " > /dev/null 2>&1 & ",  shell=True)
   
    except MySQLdb.Error as error:
        print(error)
        conn.close()
              
        
        
##program start here
    
pid = os.getpid()               ##Get process pid
print("pid is: %d" % pid)

conn = MySQLdb.connect(Fink_DB_HOST,Fink_DB_USER,Fink_DB_PW,Fink_DB_NAME) ##connect to DB

StartAllUnits(conn) ##start all components and agents
StartAgents(conn)
time.sleep(10)
    
   

    



    
