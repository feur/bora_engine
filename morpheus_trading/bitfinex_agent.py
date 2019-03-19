
import time
import datetime
import os.path
import argparse

import bitfinex_api as Client
from common_objects import *

import base64
import hashlib
import hmac
import json
import requests


data_source = []
data_source.append({'key': 'vmY34UGhFaTyFVz4R5nDjCHQP9oohKW6kxiVSH3GXFn', 'secret': 'z9gfn0JMTWQzIEcjlTiaLfdv6kBIHfKQiNe2QduZkml'})  
data_source.append({'key': '8DRfO5aIcF0ESv6PqntprFiBSnGsZWExTKd3SVQ8Jod', 'secret': 'yoE8RqEooBzRRZCZaGxySV1obTyrznyLaXKvCntZoXs'})    
master_ip = "138.197.194.3" 
        

class trading_account(object):
    
    def __init__(self):
        

        self.get_params()
        
        print("*******************************************")
        
        self.exchange_fee = 0.2
        self.base_btc_min = 0.0005
        self.base_usd_min = 10
        
        self.high = []
        self.low = []
        self.open = []
        self.time = []
        self.close = []
        self.vol = []
        
        self.M  = []
        self.K = []
        
        self.bid = []
        self.ask = []
        
        self.profit = 0
        self.loss = 0
        self.total_return = 0
        
        self.ticker_close = 0
        
        self.balance_unit = 0
        self.balance_base = 0
        
        
        self.back_orders = []
        self.support_needed = 0   
        
        ##Get Lot Size
        self.symbolData = Client.get_symbol_details(self.currency,self.base)
        print("Price Precision: ", self.symbolData.price_precision)
        
        ##for storing backlog or activites
        self.csv_title = self.symbol + '.csv'
        self.csv_activities = self.symbol + '_activites.csv'
        ## check balance if balance is 0 and no orders exist -- delete order and delete any csv
        
        self.max_activities = 3
    
        ##for graphing purpose
        self.current_price = []
        self.action_buy = []
        self.action_sell = []
        
        
        if self.rebuild_state():
            print("Agent state rebuilt")
            
        ##update status
        self.SetStatusOnline()
            
            
    def get_params(self):
        parser = argparse.ArgumentParser(description='Agent trading for pair')
    
        parser.add_argument('-uid', '--uid',
                        action='store',  # tell to store a value
                        dest='uid',  # use `pair` to access value
                        help='Agnet UID')
        parser.add_argument('-s', '--datasource',
                        action='store',  # tell to store a value
                        dest='source',  # use `pair` to access value
                        help='Data source')
    
        action = parser.parse_args()
        
        self.agentUID = str(action.uid)
        self.data_api_key = data_source[int(action.source)-1]['key']
        self.data_api_secret = data_source[int(action.source)-1]['secret']
        
        print("____pulling all configs")
        url = "http://"+master_ip+":8000/api/v1/agent?uid="+self.agentUID
        response = requests.get(url).json()
        
        config = response['objects'][0]
        self.currency = str(config['currency']).upper()
        self.base = str(config['base']).upper()
        self.agent_weight = float(config['weight']) 
        self.symbol = self.currency + self.base
        self.api_key = str(config['key'])
        self.api_secret = str(config['secret']).encode()
        
       
    def SetStatusOnline(self):
        
        pid = os.getpid()  
        
        ##get ID first 
        url = "http://"+master_ip+":8000/api/v1/agent?uid="+self.agentUID
        response = requests.get(url).json()
        objectID = str(response['objects'][0]['id'])
        
        url = "http://"+master_ip+":8000/api/v1/agent/"+objectID+"/"
        payload = {
                "status": "online",
                "pid": str(pid)
                }
         
        payload = json.dumps(payload)
        
        headers = {
                'content-type': "application/json",
                'cache-control': "no-cache",
                'postman-token': "f0ca5cae-0ec9-042f-664d-2aea65def078"
                }

        response = requests.request("PATCH", url, data=payload, headers=headers)
              
        
        
        
    def rebuild_state(self):
        print("")
        print("Rebuilding State..... for Symbol ", self.symbol)
        self.get_ticker()
        if os.path.isfile(self.csv_title):
                print("backorder file exist.....re-building backorders")
                self.reconstruct_backlog()
                print("Backorder reconstructed.....")
          
        
            
    def update_backlog_file(self):
        f = open(self.csv_title,'w')
        csv_row = ''
        for block in self.back_orders:
            csv_row += str(block.buy_uid) + ","
            csv_row += str(block.sell_uid) + ","
            csv_row += str(block.buy_price) + ","
            csv_row += str(block.sell_price) + ","
            csv_row += str(block.quantity_units) + ","
            csv_row += str(block.quantity_base) + ","
            csv_row += str(block.position) + ","
            csv_row += str(block.weight) + "\n"
            
        f.write(csv_row) #Give your csv text here.
        ## Python will convert \n to os.linesep
        f.close()
        
    def add_to_backlog(self,block):       
        print("Adding block to Backlog !!!!!!!!!!")
        self.back_orders.append(block)
        #self.update_backlog_file()
        
        
    def remove_last_backlog(self):
        print("removing last block from Backlog !!!!!!!!!!")
        del self.back_orders[-1]
        #self.update_backlog_file()
        
    def update_last_backlog(self,block):
        print("Updating last block from Backlog !!!!!!!!!!")
        self.back_orders[-1] = block
        #self.update_backlog_file()
        
        
    def log_activities(self,price,buy_price,sell_price):
        now = datetime.datetime.now()
        
        f = open(self.csv_activities,'a')
        csv_row = str(price) + ","
        csv_row += str(buy_price) + ","
        csv_row += str(sell_price) + ","
        csv_row += str(now) +"\n"
        
        f.write(csv_row) 
        f.close()
        
        
    def reconstruct_backlog(self):
        
        import csv
        with open(self.csv_title,'r') as backlogFile:
            reader = csv.reader(backlogFile)
            for row in reader:
                block = Block(row[0],row[1],row[2],row[3],row[4],row[5],row[6],row[7])
                self.back_orders.append(block)
        
        if len(self.back_orders) > 0 and self.back_orders[-1].sell_uid == 0:
            if self.GetOrderProperties(self.back_orders[-1].buy_uid)['status'] == 'NEW':
                self.CancelOrder(self.back_orders[-1].buy_uid) ##cancel order
                self.remove_last_backlog() ##remove it
        
        return 1
        
        
    def get_ticker(self):
        
        print("")
        print("getting last price....")     
        while True:
            data = Client.get_symbol_ticker_last(self.currency,self.base)
            if data != 0:
                self.ticker_close = data
                print("Last Price: ", self.ticker_close)
                return 1
            else:
                time.sleep(70)
           
                            
    def get_historical_data(self):
        
        self.time *= 0
        self.open *= 0
        self.close *= 0
        self.high *= 0
        self.low *= 0
        self.vol *= 0
        
        req = Client.get_symbol_candles(self.currency,self.base)
        
        for i in range (len(req)):
            self.time.append(i)
            self.open.append(float(req[len(req)-i-1][1]))
            self.close.append(float(req[len(req)-i-1][2]))
            self.high.append(float(req[len(req)-i-1][3]))
            self.low.append(float(req[len(req)-i-1][4]))
            self.vol.append(float(req[len(req)-i-1][5]))
                        
        return 1
    
    
    def get_balance(self):
        
        self.balance_base = Client.get_asset_balance(self.base)
        self.balance_unit = Client.get_asset_balance(self.currency)
        self.balance_base_holding = self.balance_unit * self.ticker_close
        self.total_base_balance = self.balance_base_holding + self.balance_base
                
        if (self.base == "USD" and self.balance_base_holding > self.base_usd_min) or (self.base == "BTC" and self.balance_base_holding > self.base_btc_min):
            return 1
        else:
            return 0
        
        
    
    def GetOrderProperties(self,order_uid):
        return Client.get_order_status(self.api_key,self.api_secret,order_uid) 
    
        
    def CancelOrder(self,order_uid):
        ##check if order exists first
        print("Cancelling order: ", order_uid)
        status = self.GetOrderProperties(order_uid)
        print("Status of order: ")
        print(status)
        
        if status == 0:
            return 0
        
        if str(status['status']) == "FILLED":
            print("Order has been filled...can't cancel")
            return 0
        elif str(status['status']) == "CANCELED":
            print("Order has been canceled...can't cancel")
            return 0
        else:
            
            while True:
                
                if Client.cancel_order(self.api_key,self.api_secret,order_uid) == 1:
                    time.sleep(1)
                
                    ##double check if the order is cancelled 
                    status = self.GetOrderProperties(order_uid)
                    if str(status['status']) == "CANCELED":
                        print("Order has been successfuly cancelled")
                        return 1
                    elif str(status['status']) == "FILLED":
                        print("Order has been unfortunately filled :::::::::::")
                        return 1
                    else:
                        print("Order has not been cancelled________retrying_______")
                
                else:
                    print("Error cancelling order")
                    return 0
            
        
                  
            
    ##make buy order at specified position 
    def MakeBuyOrder(self,order_block):
         
        buy_order = order_block
        buyprice = buy_order.buy_price
        buy_order.quantity_units = buy_order.quantity_base / float(buyprice)
        #buyprice = '%.8f' % buy_order.buy_price

        #buy_order.quantity_units = self.agent_weight / float(buyprice) ## converting it to units based on the agent weight & poition pricing
        #buy_order.quantity_units = buy_order.quantity_units - (buy_order.quantity_units % self.pair_stepSize)
        #buy_order.quantity_base = buy_order.quantity_units * buy_order.buy_price
        
        print("Making Buy order for ",buy_order.quantity_units,self.currency,"at ",buyprice,self.base)  
        response = Client.run_order(self.api_key,self.api_secret,self.symbol,buy_order.quantity_units,str(buyprice),"buy")
        if response != 0:
            buy_order.buy_uid = response
            print("Buy Order in place !!!!! ID: ", buy_order.buy_uid)
            ##Then backlog it 
            self.update_last_backlog(buy_order)
            self.log_activities(self.ticker_close,str(buy_order.buy_price),"")
            return 1
            
        else:
            print("BUY ORDER ERROR")
            return 0
        
       

        
    
    #make sell order at specified position 
    def MakeSellOrder(self,order_block):
        
        
        sell_order = order_block
        OrderAmount = sell_order.quantity_units 
        OrderBase = OrderAmount * sell_order.sell_price
        sellprice = sell_order.sell_price
       
        #OrderAmount = OrderAmount - (OrderAmount % self.pair_stepSize)
        #sellprice = '%.8f' % order_block.sell_price
        
        print("")
        print("Making Sell order for ", OrderAmount,self.currency, ".....", OrderBase,self.base," at ",sellprice)
        response = Client.run_order(self.api_key,self.api_secret,self.symbol,OrderAmount,str(sellprice),"sell")
        
        if response != 0:
            print("Sell Order in place !!!! ID: ", self.back_orders[-1].sell_uid)            
            print("")
            self.back_orders[-1].sell_uid = response
            self.back_orders[-1].sell_price = sellprice
            self.log_activities(self.ticker_close,"",str(self.back_orders[-1].sell_price))
            return 1
        else:
            print("SELL ORDER ERROR______") 
            self.get_balance()
            sell_order.quantity_units = self.balance_unit 
            sell_order.quantity_base = sell_order.quantity_units * sell_order.buy_price
            self.MakeSellOrder(sell_order)
    
    
                
         
        
    def get_orderbook(self):
        
        ##clear out current orderbook
        self.bid *= 0 
        self.ask *= 0     
        time.sleep(2)
        print("_____GETTING ORDERBOOKS")
        while True:
            data = Client.get_orderbooks(self.symbol)
            
            if data != 0:
                self.bid = data[0]
                self.ask = data[1]
        
                self.ticker_close = self.bid[0].buy_price
                print("Assumed Closing Price: ", self.ticker_close)
                
                return 1
            
        
        
            
    def Optimise(self,entry,rl,sl):
        
        datalen = len(self.close)
        scenario = 0
        
        i = 0
        while i <= datalen-2:
            x = i+1
            while x <= datalen-2:
                if self.close[x] <= self.close[i] * sl:  ##we found entry
                    z = i+1
                    r = 0
                    while z <= datalen-2 and self.close[z] >= self.close[x]:
                        if self.close[z] >= self.close[x] * rl: #we found exit
                            r = 1
                            break
                        z+=1
                        
                    if r == 1:
                        scenario += rl
                    else:
                        scenario = scenario - rl
                    break   
                    
                x+=1
            i+=1
                            
        #print(scenario, "scenarios encountered")
        return scenario
       
            
    
    def market_study(self):
        #print("Studying Data with FINK Algorithm.........")
    
        self.get_historical_data()
        self.get_orderbook()
        
        rl = 0
        w_max = 0
        
        short_pos = 0
        long_pos = 0
        
        ##now go through each orderbook blocks
        ## find x and y 
        for b in self.bid:
            for a in self.ask:
                
                if a.weight >= b.weight: ##first condition 
                    x = b.position - 1
                    y = a.position - 1
  
                    if x > 0 and y > 0 and self.bid[x].buy_price >= min(self.close):
                        sl = self.bid[x].buy_price / self.ticker_close
                        rl  = self.ask[y].sell_price / self.bid[x].buy_price
                        if rl  > (1 + self.exchange_fee):
                            #print("")
                            #print("Bid: ", self.bid[x].price, "___", self.bid[x].weight)
                            #print("Ask: ", self.ask[y].price, "___", self.ask[y].weight)
                            #print("Rl: ", rl, " SL: ",sl)
                            #print("")
                            
                            w = self.Optimise(self.bid[x].buy_price,rl,sl)
                            #print('*', end='')
                            
                            if w > w_max:
                                
                                short_pos = x
                                long_pos = y
                                w_max = w
                            
                            #print("_________________________________")
                    break
               
        #print("\n Results: ")
        if short_pos > 0 and long_pos > 0:
            print("W_max:", w_max)
            print("Short at ", self.bid[short_pos].buy_price, " then Long at ", self.ask[long_pos].sell_price)
            return self.Get_Entry_Position(self.bid[short_pos],rl)
        else:
            print("No trading decisions ready")
            return 0
            
        
        
        
        
    #### The whole point of this function is to:
    #### - Is there an Extrema on the Bid Order Book
    #### - If there is, is there an existing Extrama on the Ask Order Book
    #### - Is there distance between the Extrema's greater then exchange fee
    #### - If yes to all... take buy position
    
    def Get_Entry_Position(self, entry_block,rl):

        if len(self.back_orders) > 1:
            if self.back_orders[-1].sell_uid != 0:
                previous_entry = self.back_orders[-1]
            else:
                previous_entry = self.back_orders[-2]
        elif len(self.back_orders) == 1:
            previous_entry = self.back_orders[-1]

        
        if self.support_needed:            
            if self.ticker_close >= previous_entry.buy_price or len(self.back_orders) == 0:
                print("_____SUPPORT NO LONGER NEEDED")
                self.support_needed = 0 
                return -1
            else:
                loss = previous_entry.quantity_base * ( 1 - (self.ticker_close / previous_entry.buy_price)) 
                print("Backorder Loss: ", loss)
        else:
            loss = 0
            
        p = rl - self.exchange_fee
        additional_weight = (loss / (1 + p))
        print("Additional Weight required: ", additional_weight)
        
        quantity_base = self.agent_weight + additional_weight ##calculate how many btc we need to recover previous loss
        quantity_units = quantity_base / entry_block.buy_price
        
        entry_block.quantity_units = quantity_units
        entry_block.quantity_base = quantity_base
        
        print("Making Entry at Block: ", entry_block.position, "..... Rate: ", entry_block.buy_price, ".... Base: ",entry_block.quantity_base, "... Units: ",entry_block.quantity_units)
        print("")
        
        return entry_block
        
        
        
        
    def GetExitPosition(self):
        
        #time.sleep(4)
        self.get_orderbook()       
        #self.get_ticker()
        exit_order = 0
        
        entry = self.back_orders[-1] ##get last entry position
       
        
        if entry == 0:
            target_weight = self.agent_weight
        else:
            print("updating exit position.... entry was at:  ", entry.buy_price, " ... with weight of: ", entry.weight)
            target_weight = entry.weight
            
            
        if self.ticker_close < entry.buy_price:
            print("!!!!! Market is below entry price !!!!") 
            self.support_needed = 1 
            return -1 
            
        
        ##find whether we need to shift up or down the price to match weight
        for i in self.ask:
            exit_order = i
            if (i.weight > target_weight):
                break
                        
        if isinstance(exit_order, Block): 
            d = (exit_order.sell_price / entry.buy_price) 
            print("Identified Exit at ",exit_order.sell_price,"....Distance from entry ", d)
            if d > (1 + self.exchange_fee):
                
                exit_order.quantity_units = entry.quantity_units
                exit_order.quantity_base = exit_order.quantity_units * exit_order.sell_price
                
                print("Exit at Block: ",exit_order.position, "..... Rate: ",exit_order.sell_price," ....Base: ",exit_order.quantity_base,"....Units:",exit_order.quantity_units)              
                self.log_activities(self.ticker_close,"",str(exit_order.sell_price))
                return exit_order
            else:
                print("SUPPORT NEEDED ^^^^^^^^^^^^^^")
                self.support_needed = 1 
                return -1
        else:
            print("No Exit found")
            self.log_activities(self.ticker_close,"","")
            return 0
        
        
        
    def trade(self):
        
        while True:      
            
            StartTime = datetime.datetime.now()   
            
            
            print("")
            print("TRADING SYMBOL ", self.symbol)
            print("")
                   
            print("Back Orders: ", len(self.back_orders))
            
            if len(self.back_orders) != 0:     
                for x in self.back_orders:
                    print("Back order at Buy Price: ", x.buy_price,"...Sell Price: ", x.sell_price,"...Base: ", x.quantity_base, " or Units: ", x.quantity_units, "..Buy_UID", x.buy_uid, "...Sell_UID: ", x.sell_uid)
        
                ##SELL ORDER HANLDER
        
                ##check if we have a sell order registered
                if self.back_orders[-1].sell_uid != 0:
                    
                    status = self.GetOrderProperties(self.back_orders[-1].sell_uid)
                    print("")
                    print(status)
                    print("")
                    
                    executed_qty = float(status['executedQty'])
                    original_qty = float(status['origQty'])
                    remaining_qty = original_qty - executed_qty
                    
                    self.back_orders[-1].quantity_units = remaining_qty ##updated quantiy in back order
                    self.back_orders[-1].quantity_base = self.back_orders[-1].quantity_units * self.back_orders[-1].sell_price   
                    
                    if str(status['status']) == "NEW" or str(status['status']) == "PARTIALLY_FILLED":  ##we look to update sell order     
                        sell_pos = self.GetExitPosition()                             ##get updated Exit position
                        if isinstance(sell_pos, Block):
                            if sell_pos.sell_price != self.back_orders[-1].sell_price:        ##we get a different exit position
                                if self.CancelOrder(self.back_orders[-1].sell_uid) == 1 :                          ##cancel the current order
                                    self.MakeSellOrder(sell_pos)                                  ##execute order   
                            else:
                                self.log_activities(self.ticker_close,"",str(sell_pos.sell_price))
                                print("SELL ORDER IS GOOD ***********")
                                print("")
                        elif sell_pos <= 0:                                 ##we need a support buy block
                            buy_pos = self.market_study()                  ##find a buy position
                            if isinstance(buy_pos, Block):
                                self.add_to_backlog(buy_pos)                         ##back log it
                                if self.MakeBuyOrder(buy_pos) <= 0:                 ##execute order  
                                    self.remove_last_backlog()                      ##remove the last block if we can't execute that buy order
                                                 
                    elif str(status['status'])== "FILLED":
                        print("SELL ORDER FILLED ****************")
                        print("")
                        self.remove_last_backlog() ##remove the last block since its filled
                        
                    elif str(status['status']) == "CANCELED":
                        print("SELL ORDER CANCELED ****************")
                        print("")
                        
                        if (self.base == "USDT" and self.back_orders[-1].quantity_base > self.base_usd_min) or (self.base == "BTC" and self.back_orders[-1].quantity_base > self.base_btc_min):
                            print("remaining balance of cancelled order still needs to be cleared out")
                            sell_pos = self.GetExitPosition()                                                    ##get Exit position    
                            if isinstance(sell_pos, Block): 
                                self.MakeSellOrder(sell_pos)                   ##execute order   
                            elif sell_pos < 0:                                 ##we need a support buy block
                                buy_pos = self.market_study()                  ##find a buy position
                                if isinstance(buy_pos, Block):
                                    self.add_to_backlog(buy_pos)               ##back log it
                                    if self.MakeBuyOrder(buy_pos) <= 0:        ##execute order  
                                        self.remove_last_backlog()             ##remove the last block since its been cancelled  
                                    
                        else:
                            self.remove_last_backlog()                        ##remove the last block since its been cancelled 
                   
                
                ##BUY ORDER HANDLER
                
                ##check if we have a buy order registered
                elif self.back_orders[-1].buy_uid != 0:
                    
                    status = self.GetOrderProperties(self.back_orders[-1].buy_uid)
                    
                    print("")
                    print(status)
                    print("")
                    
                    executed_qty = float(status['executedQty'])
                    original_qty = float(status['origQty'])
                    remaining_qty = original_qty - executed_qty
                    
                    
                    self.back_orders[-1].quantity_units = executed_qty
                    self.back_orders[-1].quantity_base = self.back_orders[-1].quantity_units * self.back_orders[-1].buy_price
                    
                    if str(status['status']) == "NEW":
                        buy_pos = self.market_study() ## do a study
                        if isinstance(buy_pos, Block):
                            if buy_pos.buy_price != self.back_orders[-1].buy_price:                                ##we get a different exit position
                                if self.CancelOrder(self.back_orders[-1].buy_uid) == 1 :                          ##cancel the current order
                                    self.MakeBuyOrder(buy_pos)          
                            else:
                                self.log_activities(self.ticker_close,str(buy_pos.buy_price),"")
                                print("Buy ORDER IS GOOD ***********")
                                print("")
                        elif buy_pos <= 0:
                            if self.CancelOrder(self.back_orders[-1].buy_uid) == 1 :                          ##cancel the current order
                                self.remove_last_backlog()                                                    ##remove the last block since its not needed   
                                
                    elif str(status['status']) == "PARTIALLY_FILLED" or str(status['status']) == "FILLED":           ## order has been touched 
                        print("BUY ORDER TOUCHED ****************")
                        print("")
                                         
                        ##cancel buy order and find exit position
                        if str(status['status']) == "PARTIALLY_FILLED":
                            if self.CancelOrder(self.back_orders[-1].buy_uid) == 1 :                          ##cancel the current order
                                self.remove_last_backlog()                                                           ##remove the last block since its not needed 
                        
                        sell_pos = self.GetExitPosition()                                                    ##get Exit position    
                        if isinstance(sell_pos, Block): 
                            self.MakeSellOrder(sell_pos)                   ##execute order   
                        elif sell_pos < 0:                                 ##we need a support buy block
                            buy_pos = self.market_study()                  ##find a buy position
                            if isinstance(buy_pos, Block):
                                self.add_to_backlog(buy_pos)               ##back log it
                                if self.MakeBuyOrder(buy_pos) <= 0:        ##execute order  
                                    self.remove_last_backlog()             ##remove the last block since its been cancelled  
                                    
                        
                                
                    elif str(status['status']) == "CANCELED":
                        print("BUY ORDER CANCELED ****************")
                        print("")
                        
                        
                        if executed_qty > 0: 
                            sell_pos = self.GetExitPosition()                  ##get Exit position    
                            if isinstance(sell_pos, Block): 
                                self.MakeSellOrder(sell_pos)                   ##execute order   
                            elif sell_pos < 0:                                 ##we need a support buy block
                                buy_pos = self.market_study()                  ##find a buy position
                                if isinstance(buy_pos, Block):
                                    self.add_to_backlog(buy_pos)               ##back log it
                                    if self.MakeBuyOrder(buy_pos) <= 0:        ##execute order  
                                        self.remove_last_backlog()             ##remove the last block since its been cancelled  
                        else:
                            self.remove_last_backlog()                         ##remove the last block since its been cancelled    
                                          
            else:
                buy_pos = self.market_study()                                  ##find buy position
                if isinstance(buy_pos, Block):                          
                    self.add_to_backlog(buy_pos)                               ##back log it
                    if self.MakeBuyOrder(buy_pos) <= 0:                        ##execute order, if unable to  
                        self.remove_last_backlog()                             ##remove the last block since its been cancelled  \

                                
                        
            print("UPDATING BACKLOG FILE")
            self.update_backlog_file()
            
            EndTime = datetime.datetime.now()
            tdiff = EndTime - StartTime 
            timetaken = int(tdiff.total_seconds())
            
            if timetaken == 0:
                timetaken = 1
            
            
            print("")
            print("Time taken: ",timetaken)
            print("______________DONE___________________")
            print("")
                    
                
                
            

def main():
     
    target = trading_account()   
    target.trade()

    
        

if __name__ == '__main__':
    main()
