from bittrex.bittrex import *
import argparse
from statistics import mean
import os
import time
import MySQLdb
import subprocess
import psutil
from settings import *


            
def GetPID(conn,component):
    
    cursor = conn.cursor()
        
    if (component == "manager"):     
        query = "SELECT PID from Pairs WHERE Pair = '%s'" 
    elif (componetn == "buyer"):
        query = "SELECT PID from Pairs WHERE Pair = '%s'"   
    elif (componetn == "seller"):
        query = "SELECT PID from Pairs WHERE Pair = '%s'"  
        
    try:
        
        cursor.execute (query)
        data = cursor.fetchone() #find PID for PAIR
        
        #check if pid is running
        if psutil.pid_exists(data[0]):
            print("process %s is still running with pid %d" % (component, data[0]))
        else:
            print("re-running process for this component %s" % (component))
            process = subprocess.call("python ~/bora_local/python/bittrex/" + component + ".py > /dev/null 2>&1 & ",  shell=True)
    
    except MySQLdb.Error as error:
        print(error)
        conn.close()   
        
    return 1    
                

    
##program start here

pid = os.getpid()               ##Get process pid
print("pid is: %d" % pid)

conn = MySQLdb.connect(DB_HOST,DB_USER,DB_PW,DB_NAME) ##connect to DB

cursor = conn.cursor()

result = GetPID(conn,"manager") ##Check if Manager is running, if not re-run manager
result = GetPID(conn,"manager") ##Check if buyer is running, if not re-run buyer
result = GetPID(conn,"seller") ##Check if seller is running, if not re-run seller    




    
