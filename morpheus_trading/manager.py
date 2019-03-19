#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Mar  6 22:56:58 2019

@author: Taras WOronjanski
"""

#import sys
import time
import subprocess
import base64
import hashlib
import hmac
import json
import time
import requests
import os
import signal
import psutil



agents = []
host_ip = "167.99.104.226"
master_ip = "138.197.194.3"

"""
startAgent pulls the list of agents from the database 
and starts trading agents
"""

#return subprocess.Popen(command, shell=True, stdout=subprocess.PIPE)
def RunAgent(agentID,source,strategy,exchange):
    
    directory = os.getcwd()
    command = 0
    if strategy.upper() == "LONG" and exchange.upper() == "BITFINEX":
        command = "python3 " + directory + "/bitfinex_agent.py -uid " + str(agentID) + " -s " + source + " > /dev/null 2>&1 & "
        print(command)
    
    if command != 0:
        subprocess.call(command, shell=True)
        time.sleep(10)
    else:
        return 0


        
def SetAgentStatus(agentID,status):
    print("____pulling all configs")
    url = "http://"+master_ip+":8000/api/v1/agent?host="+host_ip
    
    ##get ID first 
    url = "http://"+master_ip+":8000/api/v1/agent?uid="+agentID
    response = requests.get(url).json()
    objectID = str(response['objects'][0]['id'])
        
    url = "http://"+master_ip+":8000/api/v1/agent/"+objectID+"/"
    payload = {
            "status": str(status),
            }
         
    payload = json.dumps(payload)
        
    headers = {
            'content-type': "application/json",
            'cache-control': "no-cache",
            'postman-token': "f0ca5cae-0ec9-042f-664d-2aea65def078"
            }

    response = requests.request("PATCH", url, data=payload, headers=headers)
    
    
    
def PurgeAgent(agentObject):
    os.kill(int(agentObject['pid']), signal.SIGTERM)
    time.sleep(3)
    return 1
    

def CheckAgents(agents):
    
    print("____checking all agents")
    url = "http://"+master_ip+":8000/api/v1/agent?host="+host_ip
    response = requests.get(url).json()
    
    for i in response['objects']:
        
        if i['action'] == 'run' :   ## check if action is "run"
            agentID = str(i['uid'])
            agentPID = int(i['pid'])
            print("AGENT ID: ", agentID, " with PID: ", agentPID)
            strategy = str(i['strategy'])
            exchange = str(i['exchange'])
            if agentPID > 0: ##check that agent is still running                 
                exist = psutil.pid_exists(agentPID)
                if (exist == 1):
                    ##PID exist but maybe agent is hanging on an error? 
                    if i['status'] == "error":
                        print ("AGENT ERROR CODE: " + str(i['errorCode']))
                    else:
                        print("AGENT " + str(agentPID) +" STILL ONLINE")
                else:
                    SetAgentStatus(agentID, "error")
                    print("TRYING TO RE-RUN AGENT " + str(agentID))
                    print(RunAgent(agentID, '1',strategy,exchange)) ##agent doesn't exist anymore, re-run
            else: ##we don't have a PID 
                print("RUNNING AGENT " + str(agentID))
                RunAgent(agentID, '1',strategy,exchange) ##run agent
                
        if i['action'] == 'purge' :   ## check if action is "purge"
            agentID = i['agentID']
            agentPID = int(i['pid'])
            print("AGENT ID: ", agentID, " with PID: ", agentPID)
            if agentPID > 0: ##check that agent is still running                 
                exist = psutil.pid_exists(agentPID)
                if (exist == 1):
                    ##PID exist but maybe agent is hanging on an error? 
                    if i['status'] == "error":
                        print ("AGENT ERROR CODE: " + str(i['errorCode']))
                        SetAgentStatus(agentID, "purged")                     
                    else:
                        PurgeAgent(i)
                        print("AGENT " + str(agentID) +" STILL ONLINE")
                else:
                    SetAgentStatus(agentID, "purged")
                    #print("TRYING TO RE-RUN AGENT " + str(agentID))
                    #RunAgent(agentID, '1') ##agent doesn't exist anymore, re-run
            else: ##we don't have a PID 
                SetAgentStatus(agentID, "purged")
            

                        
def GetAgentList():
    print("____pulling all agents for this host")
    url = "http://"+master_ip+":8000/api/v1/agent?host="+host_ip
    response = requests.get(url).json() 
    
    agents = response['objects']
    if len(agents) > 0:
        return agents
    else:
        return 0
     
        
    
def main():
    
    agents = []

    print ("AGENT MANAGER V0.2_______") 
        
    while True:
        
        r = GetAgentList()
        if r != 0:
            agents = r
            
        if len(agents) > 0:
            CheckAgents(agents)
        else:
            print("NO AGENTS")
         
        time.sleep(1)
        
            
       

if __name__ == '__main__':
    main()
