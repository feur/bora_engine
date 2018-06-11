from bittrex.bittrex import *
import argparse
from statistics import mean
import os
import time
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
                        dest='key',  # use `paor` to access value
                        help='Your API Secret')
    parser.add_argument('-l', '--limit',
                        action='store',  # tell to store a value
                        dest='limit',  # use `paor` to access value
                        help='Your Buy Limit')
   
    action = parser.parse_args()
    return action
    
    
 
def InsertAPI(fink, api, key,limit):   
    '''
    Get API key, Secret and limit from command entry
    And insert into Database
    '''  

    ###Checkinf if a limit has been put otherwise put in default limit
    if (limit != None):
        BuyLimit = limit
    else:
        BuyLimit = 0.04
    
    cursor = fink.cursor()    
    
    query = "INSERT INTO `Settings`(`API_Key`, `API_Secret`, `BuyLimit`) VALUES ('%s','%s',%.9f)" % (api,key,float(BuyLimit))
    
    try:       
        cursor.execute (query)
        fink.commit()
        return 1
              
    except MySQLdb.Error as error:
        print(error)
        fink.rollback()
        fink.close()
        
        
        
def UpdateLimit(fink, limit):
    '''
    This just updates the limit
    '''
    
    cursor = fink.cursor()    
    
    query = "UPDATE `Settings` SET `BuyLimit`=%.9f WHERE 1" % (limit)
    
    try:       
        cursor.execute (query)
        fink.commit()
        return 1
              
    except MySQLdb.Error as error:
        print(error)
        fink.rollback()
        fink.close()
   
   
def UpdateUID(fink):
    '''
    This just updates the limit
    '''
    
    cursor = fink.cursor()    
    
    UID = "Admin"
    
    query = "UPDATE `Settings` SET `UID`='%s' WHERE 1" % (UID)
    
    try:       
        cursor.execute (query)
        fink.commit()
        return 1
              
    except MySQLdb.Error as error:
        print(error)
        fink.rollback()
        fink.close()   
   
   
    
def InitPairs(fink,edel):    
   
    '''
    Will get all the Pairs that are currently registerd by Edel and populate 
    Fink DB
    '''
    
    ###First make sure all Tables are clear
    cursor = fink.cursor()    
    
    try:       
        cursor.execute ("DELETE FROM `Pairs`")
        fink.commit()
        
        cursor.execute ("DELETE FROM `Settings`")
        fink.commit()
        
        cursor.execute ("DELETE FROM `AccountBalance`")
        fink.commit()
        
        cursor.execute ("DELETE FROM `AccountHistory`")
        fink.commit()
        
        cursor.execute ("DELETE FROM `SignalLog`")
        fink.commit()
              
    except MySQLdb.Error as error:
        print(error)
        fink.rollback()
        fink.close()
        
        
    ###Get a list of all Pairs and Currency
    cursor = edel.cursor()  
      
    try:
        cursor.execute ("SELECT `Pair`, `Currency` FROM `Pair_List` WHERE 1 ")
        data = cursor.fetchall()
        
        cursor = fink.cursor()
        
        for i in range(len(data)):
        
            ##now insert the list into the local database 
            
            query = "INSERT INTO `Pairs`(`Pair`, `Currency`) VALUES ('%s','%s')" % (str(data[i][0]),str(data[i][1]))
    
            try: 
                cursor.execute(query)
                fink.commit()
    
            except MySQLdb.Error as error:
                print(error)
                fink.close()
       
    except MySQLdb.Error as error:
        print(error)
        edel.close()
        


##program start here
  
fink = MySQLdb.connect(Fink_DB_HOST,Fink_DB_USER,Fink_DB_PW,Fink_DB_NAME) ##connect to DB
edel = MySQLdb.connect(Edel_DB_HOST,Edel_DB_USER,Edel_DB_PW,Edel_DB_NAME) ##connect to DB


entry = GetEntry() ##Get arguments for API Key, Secret, Buy limits and an action to refill Pair table

if (entry.api != None and entry.key != None ):  ##A new API and secret has been put in

    if (InitPairs(fink,edel)):
        print ("Successfully populated table")
    
    if (InsertAPI(fink, entry.api, entry.key, entry.limit)):  
        print ("Succesfully updated api")
        
elif (entry.limit != None): ##no new api or key just limit
    
    if (UpdateLimit(fink, entry.limit)):
        print ("Successfully updated Limit")
        

UpdateUID(fink)   
    
    

    
