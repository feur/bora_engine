import argparse
import time
from ac import *



def GetEntry():
    parser = argparse.ArgumentParser(description='Get Account info')
    parser.add_argument('-k', '--key',
                        action='store',  # tell to store a value
                        dest='api',  # use `paor` to access value
                        help='Your API Key')
    parser.add_argument('-s', '--secret',
                        action='store',  # tell to store a value
                        dest='secret',  # use `paor` to access value
                        help='Your API Secret')
    
    action = parser.parse_args()
    return action



entry = GetEntry() ##Get params
PersonalAccount = Account(entry)


while True:
    
    print("*******************************************************************")
    print("getting balances")
    print("___________________________________________________________________")
    PersonalAccount.GetTotalBalance()
    print(" ")
    print("Total Account: %.9f BTC / $ %.9f USD") % (PersonalAccount.TotalBTC, PersonalAccount.TotalUSD)
    print("___________________________________________________________________")
    
    
    PersonalAccount.LogAccountBalance()
    
    PersonalAccount.TotalBTC = 0
    PersonalAccount.TotalUSD = 0

    
    time.sleep(60)
