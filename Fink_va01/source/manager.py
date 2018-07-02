import argparse
import time
import MySQLdb
from settings import *
from task import *


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
    parser.add_argument('-st', '--strat',
                        action='store',  # tell to store a value
                        dest='st',  # use `paor` to access value
                        help='Strategy')
    parser.add_argument('-f', '--fib',
                        action='store',  # tell to store a value
                        dest='FibZone',  # use `paor` to access value
                        help='Fib buy zone')
    parser.add_argument('-d', '--distance',
                        action='store',  # tell to store a value
                        dest='distance',  # use `FibZone` to access value
                        help='Distance between Tenkansen & Kijunsen')
    
   
    action = parser.parse_args()
    return action



              
##program start here
                
pid = os.getpid()  ##Get process pid
entry = GetEntry() ##Get params
ListofPairs = []   ##list of Pairs, e.g. BTC-ADA, ETH-ADA
ListofCurrencies= [] ##list of Currencies e.g. ADA, OMG

print("pid is: %d" % pid)


PersonalAccount = Account()
PersonalAccount.SetParams(entry)

cursor = PersonalAccount.conn.cursor()
query = "SELECT * FROM Pairs"

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

while True:
     
    print(" ")
    print("Checking account tracker:")
    PersonalAccount.StartAccount(entry)
    print(" ")
    print("Checking all Fink agents:")
    print(" ")
    for i in range(len(ListofPairs)):
        PersonalAccount.StartAgent(ListofPairs[i],entry)
    print("______________________________________________________")
    quit()
    
    #time.sleep(60)
