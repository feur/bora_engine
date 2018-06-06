from bittrex.bittrex import *
import argparse
from statistics import mean
import os
import time
import MySQLdb
import subprocess
import psutil
from settings import *


            
def StartAllUnits():
    
    conn = MySQLdb.connect(Fink_DB_HOST,Fink_DB_USER,Fink_DB_PW,Fink_DB_NAME) ##connect to DB
    cursor = conn.cursor()
    
    try:       
        cursor.execute ("SELECT * FROM `Components` WHERE 1")
        data = cursor.fetchall() #find PID for Unit
        
        #check if pid is running
        for i in range (len(data)):
            
            if psutil.pid_exists(data[i][1]):
                print("process %s is still running with pid %d" % (data[i][0], data[i][1]))
            else:
                    print("re-running process for this component %s because PID %s doesn't exist" % (data[i][0],data[i][1]))
                    process = subprocess.call("python ~/Doge/source/" + data[i][0] + ".py > /dev/null 2>&1 & ",  shell=True)
              
    except MySQLdb.Error as error:
        print(error)
        conn.close()   
        
                

    
##program start here

pid = os.getpid()               ##Get process pid
print("pid is: %d" % pid)


while True: 
    
    StartAllUnits()
    time.sleep(10)
    
   

    



    
