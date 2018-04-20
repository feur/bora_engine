from bittrex.bittrex import *
import argparse
from statistics import mean
import os
import MySQLdb
import subprocess

#from settings import *



def GetEntry():
    parser = argparse.ArgumentParser(description='Process TA for pair')
    parser.add_argument('-p', '--pair',
                        action='store',  # tell to store a value
                        dest='pair',  # use `paor` to access value
                        help='The Pair to be watched')
    parser.add_argument('-a', '--high1',
                        type=float,
                        action='store',  # tell to store a value
                        dest='a',  # use `a` to access value
                        help='fib zone 1')
    parser.add_argument('-b', '--low1',
                        type=float,
                        action='store',  # tell to store a value
                        dest='b',  # use `d` to access value
                        help='fib zone 1')
    parser.add_argument('-c', '--high2',
                        type=float,
                        action='store',  # tell to store a value
                        dest='c',  # use `b` to access value
                        help='fib zone 2')
    parser.add_argument('-d', '--low2',
                        type=float,
                        action='store',  # tell to store a value
                        dest='d',  # use `c` to access value
                        help='fib zone 2')
    parser.add_argument('-e', '--high3',
                        type=float,
                        action='store',  # tell to store a value
                        dest='e',  # use `e` to access value
                        help='fib zone 3')
    parser.add_argument('-f', '--Low3',
                        type=float,
                        action='store',  # tell to store a value
                        dest='f',  # use `e` to access value
                        help='fib zone 3')
    pair = parser.parse_args()
    return pair
    
    


##program start here

#entry = GetEntry() ##Get arguments to define Pair and Fib levels
pid = os.getpid()  ##Get process pid

print("pid is: %d" % pid)

conn = MySQLdb.connect("localhost","root","asdfqwer1","Bora")

cursor = conn.cursor()

            
try:
    cursor.execute ("SELECT * from Config")
    data = cursor.fetchall()
    
    
    for i in range(len(data)):
        print("watching %s " % str(data[i][0]))
        process = subprocess.call("python ~/Documents/sailfin/python/bittrex/main.py " + "-p " + str(data[i][0]) + " > /dev/null 2>&1 & ",  shell=True)
    
    
except MySQLdb.Error as error:
    print(error)
    conn.close()
    

while True: 
    print("balance is: ")


