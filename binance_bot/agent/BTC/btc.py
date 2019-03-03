import base64
import hashlib
import hmac
import json
import time
import datetime

import requests
import os.path
from binance.client import Client
from binance.exceptions import BinanceAPIException


## Order book block
class Block(object):

    def __init__(self,buy_uid,sell_uid,buy_price,sell_price,quantity,base,position,booksum):
        
        self.buy_uid = int(buy_uid)
        self.sell_uid = int(sell_uid)
        self.buy_price = float(buy_price)
        self.sell_price = float(sell_price)
        self.quantity_units = float(quantity)
        self.quantity_base = float(base)
        self.position = int(position)
        self.weight = float(booksum)
        
    
    
        

class trading_account(object):
    
    def __init__(self, currency,base,key,secret,weight):
        
        self.api_key = key
        self.api_secret = secret
        
        self.account = Client(self.api_key,self.api_secret) ##binance
        print("*******************************************")
        
        self.exchange_fee = 0.003
        self.base_btc_min = 0.0005
        self.base_usd_min = 10
        
        self.symbol = currency + base
        self.currency = currency 
        self.base = base
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
        
        ##Get Lot Size
        data = self.account.get_symbol_info(symbol=self.symbol)
        self.pair_stepSize = float(data['filters'][2]['stepSize'])
        self.support_needed = 0   
        
        self.agent_weight = float(weight) ##how much the agent is using for the order in base
        
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
        
        
        
    def rebuild_state(self):
        print("")
        print("Rebuilding State..... for Symbol ", self.symbol)
        self.get_ticker()
        if self.get_balance():
            print("")
            print("Current Closing price: ", self.ticker_close, self.base)
            print("Unit balance: ", self.balance_unit, "..... ", self.balance_base, self.base)
            print("")
            print("there is some balance left.....checking if backorder file exist")
            if os.path.isfile(self.csv_title):
                print("backorder file exist.....re-building backorders")
                self.reconstruct_backlog()
                print("Backorder reconstructed.....")
                    
                
            else:
                print("no backorder exist....will need to purge balance")
        else:
            print("balance is empty....fresh start!")
        
        
        
    def get_ticker(self):
        
        print("")
        print("getting data....")
                
        while True: 
            try:
                data = self.account.get_symbol_ticker(symbol=self.symbol)
                if (data != 0):
                    self.ticker_close = float(data['price'])
                    break
            except BinanceAPIException as e:
                print (e.status_code)
                print (e.message)
                print("can't get data... retrying ...")
                
        
        
    def get_historical_data(self):
        
        self.time *= 0
        self.open *= 0
        self.close *= 0
        self.high *= 0
        self.low *= 0
        self.vol *= 0
        
        while True:
            try:
                result = self.account.get_historical_klines(self.symbol, Client.KLINE_INTERVAL_12HOUR, "1 Jan, 2017") ##Get 12 Hours in Data)
                index = 0
                for i in result:
                    self.high.append(float(i[2]))
                    self.low.append(float(i[3]))
                    self.open.append(float(i[1]))
                    self.close.append(float(i[4]))
                    self.time.append(index)
                    index += 1
                return 1
            
            except BinanceAPIException as e:
                print ("Unable to get K line... retrying...")
                print (e.status_code)
                print (e.message)
               
                
        
        return 1
    
    
    def get_balance(self):
        
        
        while True:
            
            try:
                ##get base balance
                data = self.account.get_asset_balance(self.base)
                #print(data)
                if data != 0:
                    self.balance_base = float(data['free'])
                else:
                    self.balance_base = 0
                    
            except BinanceAPIException as e:
                print (e.status_code)
                print (e.message)
                
            try:
                ##get currency balance
                data = self.account.get_asset_balance(self.currency)
               # print(data)
                if data != 0:
                    self.balance_unit = float(data['free'])
                else:
                    self.balance_unit = 0  

                
                self.balance_base_holding = self.balance_unit * self.ticker_close
                self.total_base_balance = self.balance_base_holding + self.balance_base
                
                if (self.base == "USDT" and self.balance_base_holding > self.base_usd_min) or (self.base == "BTC" and self.balance_base_holding > self.base_btc_min):
                    return 1
                else:
                    return 0
                
            except BinanceAPIException as e:
                print (e.status_code)
                print (e.message)
            
            
     
    
        
            
            
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
        
        
    def log_activities(self,buy_price,sell_price):
        now = datetime.datetime.now()
        
        f = open(self.csv_activities,'a')
        csv_row = str(self.ticker_close) + ","
        csv_row += buy_price + ","
        csv_row += sell_price + ","
        #csv_row += str(self.total_base_balance) + ","
        #csv_row += str(self.balance_base_holding) + ","
        #csv_row += str(self.balance_base) + ","
        #csv_row += str(self.balance_unit) + ","
        csv_row += str(now) +"\n"

            
        f.write(csv_row) 
        f.close()
        
        
        

    def GetOrderProperties(self,order_uid):
        if order_uid != 0:
            try:
                r = self.account.get_order(symbol=self.symbol,orderId=order_uid) 
                return r
            except BinanceAPIException as e:
                print(e)
                print("Order UID is invalid....")
                return 0
        else:
            print("Order UID is invalid.....")
            return 0
        
        
    def CancelOrder(self,order_uid):
        ##check if order exists first
        print("Cancelling order: ", order_uid)
        status = self.GetOrderProperties(order_uid)
        print("Status of order: ")
        print(status)
        
        if status == 0:
            return -2
        
        if str(status['status']) == "FILLED":
            print("Order has been filled...can't cancel")
            return 0
        elif str(status['status']) == "CANCELED":
            print("Order has been canceled...can't cancel")
            return -1
        else:
            try:
                self.account.cancel_order(symbol=self.symbol,orderId=order_uid)  
                time.sleep(1)
                return 1
            except BinanceAPIException as e:
                print(e)
                print("Order UID is invalid....")
                return -2
        
    
        
    ##incomplete    
    def reconstruct_backlog(self):
        
        import csv
        with open(self.csv_title,'r') as backlogFile:
            reader = csv.reader(backlogFile)
            for row in reader:
                block = Block(row[0],row[1],row[2],row[3],row[4],row[5],row[6],row[7])
                self.back_orders.append(block)
        
        return 1
                
        
                  
            
    ##make buy order at specified position 
    def MakeBuyOrder(self,order_block):
         
        buy_order = order_block
        buyprice = '%.8f' % buy_order.buy_price

        buy_order.quantity_units = self.agent_weight / float(buyprice) ## converting it to units based on the agent weight & poition pricing
        buy_order.quantity_units = buy_order.quantity_units - (buy_order.quantity_units % self.pair_stepSize)
        
        print("Making Buy order for ",buy_order.quantity_units,self.currency,"at ",buyprice,self.base)  
        try:
            data = self.account.order_limit_buy(symbol=self.symbol,quantity=buy_order.quantity_units,price=buyprice) ##now placing buy order
            print("Buy Order in place !!!!!")
            print("")
            ## Just to make sure its all in sync with binance...
            buy_order.buy_uid = str(data['orderId'])
            buy_order.buy_price = float(data['price'])
            buy_order.quantity_units = float(data['origQty'])
            buy_order.quantity_base = buy_order.quantity_units * buy_order.buy_price
            
            ##Then backlog it 
            self.update_last_backlog(buy_order)
            self.log_activities(str(buy_order.buy_price),"")
            return 1
                    
        except BinanceAPIException as e:
            print("ERROR: ")
            print (e.status_code)
            print (e.message)
            print("")
            return 0
    
    
    #make sell order at specified position 
    def MakeSellOrder(self,order_block):
        
        OrderAmount = order_block.quantity_units 
       
        OrderAmount = OrderAmount - (OrderAmount % self.pair_stepSize)
        OrderBase = OrderAmount * order_block.sell_price
        sellprice = '%.8f' % order_block.sell_price
        
        print("")
        print("Making Sell order for ", OrderAmount,self.currency, ".....", OrderBase,self.base," at ",sellprice)
        
        try:
            data = self.account.order_limit_sell(symbol=self.symbol,quantity=OrderAmount,price=sellprice) ##now placing sell order
            ## Just to make sure its all in sync with binance...
            self.back_orders[-1].sell_uid = str(data['orderId']) 
            self.back_orders[-1].sell_price = float(data['price']) 
            print("Sell Order in place !!!! ID: ", self.back_orders[-1].sell_uid)            
            print("")
            self.log_activities("",str(self.back_orders[-1].sell_price))
            return 1
        
        except BinanceAPIException as e:
            print("ERROR: ")
            print (e.status_code)
            print (e.message)
            print("")
                
            if e.status_code == 400: ##means we don't have the balance to sell, so force adjust  balance    
                if len(self.back_orders) == 1:
                    self.get_balance()
                    self.back_orders[-1].quantity_units = self.balance_unit
                    self.back_orders[-1].quantity_base = self.balance_base
            else:
                return 0
           
                    
    
      
        
  
   
        
    """   
        
        {
    "symbol": "LTCBTC",
    "orderId": 1,
    "clientOrderId": "myOrder1",
    "price": "0.1",
    "origQty": "1.0",
    "executedQty": "0.0",
    "status": "NEW",
    "timeInForce": "GTC",
    "type": "LIMIT",
    "side": "BUY",
    "stopPrice": "0.0",
    "icebergQty": "0.0",
    "time": 1499827319559
}
        """
        
        
    def get_orderbook(self):
        
        
        ##clear out current orderbook
        self.bid *= 0
        self.ask *= 0 
        
        bid = []
        ask = []
        

        while True:
            data = self.account.get_order_book(symbol=self.symbol)
            if data != 0:
                ask = data['asks'] ##sell orders
                bid = data['bids'] ##buy orders
                break
            
        b_sum = 0
        b_pos = 0 
        for b in bid:
            quantity_price  = float(b[0])
            quantity_unit = float(b[1])
            quantity_base = quantity_unit * quantity_price
            b_sum+=quantity_base
            self.bid.append(Block(0,0,quantity_price,0,quantity_unit,quantity_base,b_pos,b_sum))
            b_pos+=1
            
        a_sum = 0
        a_pos = 0 
        for a in ask:
            
            quantity_price = float(a[0])
            quantity_unit = float(a[1])
            quantity_base = quantity_unit * quantity_price
            a_sum += quantity_base
            
            self.ask.append(Block(0,0,0,quantity_price,quantity_unit,quantity_base,a_pos,a_sum))
            a_pos+=1 
            
        self.book_spread = (self.ask[1].sell_price / self.ask[0].sell_price) - 1
        print("Order Book Spread: ",self.book_spread)
        
        
    

            
            
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
                        sl = self.bid[x].buy_price / self.close[-1] 
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

        ## just to make sure price did not go up again then we won't need to support it
        
        if self.support_needed:            
            self.get_ticker() 
            if self.ticker_close >= self.back_orders[-1].buy_price:
                self.support_needed = 0 
                return -1
            else:
                loss = self.back_orders[-1].quantity_base * ( 1 - (self.ticker_close / self.back_orders[-1].buy_price)) 
                print("Backorder Loss: ", loss)
        else:
            loss = 0
            
        p = rl - self.exchange_fee
        
        quantity_base = self.agent_weight + (loss / (1 + p)) ##calculate how many btc we need to recover previous loss
        quantity_units = quantity_base / entry_block.buy_price
        
        entry_block.quantity_units = quantity_units
        entry_block.quantity_base = quantity_base
        
        print("Making Entry at Block: ", entry_block.position, "..... Rate: ", entry_block.buy_price, ".... Base: ",entry_block.quantity_base, "... Units: ",entry_block.quantity_units)
        print("")
        
        self.support_needed = 0 
        return entry_block
        
        
        
        
    def GetExitPosition(self):
        
        self.get_orderbook()
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
                self.log_activities("",str(exit_order.sell_price))
                return exit_order
            else:
                print("SUPPORT NEEDED ^^^^^^^^^^^^^^")
                self.support_needed = 1 
                return -1
        else:
            print("No Exit found")
            self.log_activities("","")
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
                    
                    if str(status['status']) == "NEW" or str(status['status']) == "PARTIALLY_FILLED":  ##we look to update sell order     
                        
                        self.back_orders[-1].quantity_units = remaining_qty ##updated quantiy in back order
                        self.back_orders[-1].quantity_base = self.back_orders[-1].quantity_units * self.back_orders[-1].sell_price      
                        
                        sell_pos = self.GetExitPosition()                             ##get updated Exit position
                        if isinstance(sell_pos, Block) and sell_pos.sell_price != self.back_orders[-1].sell_price: ##we get a different exit position
                            order_state = self.CancelOrder(self.back_orders[-1].sell_uid) ##cancel the current order
                            self.MakeSellOrder(sell_pos)                                  ##execute order      
                        elif isinstance(sell_pos, Block) and sell_pos.sell_price == self.back_orders[-1].sell_price: ##we get a different exit position
                            self.log_activities("",str(sell_pos.sell_price))
                            print("SELL ORDER IS GOOD ***********")
                            print("")
                        elif sell_pos < 0:                                 ##we need a support buy block
                            buy_pos = self.market_study()                  ##find a buy position
                            if isinstance(buy_pos, Block):
                                self.add_to_backlog(buy_pos)                         ##back log it
                                if self.MakeBuyOrder(buy_pos) == 0:                 ##execute order  
                                    self.remove_last_backlog()                      ##remove the last block since its been cancelled  
                                                 
                    elif str(status['status'])== "FILLED":
                        print("SELL ORDER FILLED ****************")
                        print("")
                        self.remove_last_backlog() ##remove the last block since its filled
                        
                    elif str(status['status']) == "CANCELED":
                        print("SELL ORDER CANCELED ****************")
                        print("")
                        ##update the block quantity
                        self.back_orders[-1].quantity_units = remaining_qty ##updated quantiy in back order
                        self.back_orders[-1].quantity_base = self.back_orders[-1].quantity_units * self.back_orders[-1].sell_price  
                        
                        if (self.base == "USDT" and self.back_orders[-1].quantity_base > self.base_usd_min) or (self.base == "BTC" and self.back_orders[-1].quantity_base > self.base_btc_min):
                            print("remaining balance of cancelled order still needs to be cleared out")
                            sell_pos = self.GetExitPosition()                             ##get updated Exit position
                            if isinstance(sell_pos, Block) and sell_pos.sell_price != self.back_orders[-1].sell_price: ##we get a different exit position
                                order_state = self.CancelOrder(self.back_orders[-1].sell_uid) ##cancel the current order
                                self.MakeSellOrder(sell_pos)                   ##execute order       
                            elif sell_pos < 0:                                 ##we need a support buy block
                                buy_pos = self.market_study()                  ##find a buy position
                                if isinstance(buy_pos, Block):
                                    self.add_to_backlog(buy_pos)               ##back log it
                                    if self.MakeBuyOrder(buy_pos) == 0:                 ##execute order  
                                        self.remove_last_backlog()                        ##remove the last block since its been cancelled 
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
                    
                    if str(status['status']) == "NEW":          
                        buy_pos = self.market_study()                                                            ##get updated Buy position
                        if isinstance(buy_pos, Block) and buy_pos.buy_price != self.back_orders[-1].buy_price:   ##we get a different exit position
                            order_state = self.CancelOrder(self.back_orders[-1].buy_uid)                         ##cancel the current order
                            if order_state == 1 or order_state == -1:                                            ##buy order is Canceled
                                self.MakeBuyOrder(buy_pos)                                                       ##execute order      
                        elif isinstance(buy_pos, Block) and buy_pos.buy_price == self.back_orders[-1].buy_price: ##we get a different exit position
                            self.log_activities(str(buy_pos.buy_price),"")
                            print("Buy ORDER IS GOOD ***********")
                            print("")
                        elif buy_pos < 0:                                                 ##we don't need a suppport block anymore
                            order_state = self.CancelOrder(self.back_orders[-1].buy_uid) ##cancel the current order
                            self.remove_last_backlog()                                  ##remove the last block since its not needed
                            
                    elif str(status['status']) == "PARTIALLY_FILLED" or str(status['status']) == "FILLED":       ## order has been touched 
                        print("BUY ORDER TOUCHED ****************")
                        print("")
                        self.back_orders[-1].quantity_units = executed_qty * 0.999 ##updated quantiy in back order
                        self.back_orders[-1].quantity_base = self.back_orders[-1].quantity_units * self.back_orders[-1].buy_price   
                                             
                        ##cancel buy order and find exit position
                        if str(status['status']) == "PARTIALLY_FILLED":
                            order_state = self.CancelOrder(self.back_orders[-1].buy_uid) ##cancel the current order
                            
                        sell_pos = self.GetExitPosition()                            ##get Exit position
                        if isinstance(sell_pos, Block): 
                            self.MakeSellOrder(sell_pos)                   ##execute order   
                        elif sell_pos < 0:                                 ##we need a support buy block
                            buy_pos = self.market_study()                  ##find a buy position
                            if isinstance(buy_pos, Block):
                                self.add_to_backlog(buy_pos)               ##back log it
                                if self.MakeBuyOrder(buy_pos) == 0:                 ##execute order  
                                    self.remove_last_backlog()                        ##remove the last block since its been cancelled    
                                
                    elif str(status['status']) == "CANCELED":
                        print("BUY ORDER CANCELED ****************")
                        print("")
                        if executed_qty != 0: ##it was cancelled but there was a partial fill before it was cancelled 
                            self.back_orders[-1].quantity_units = executed_qty ##updated quantiy in back order
                            self.back_orders[-1].quantity_base = self.back_orders[-1].quantity_units * self.back_orders[-1].buy_price  
                            sell_pos = self.GetExitPosition()                            ##get Exit position
                            if isinstance(sell_pos, Block) and sell_pos.sell_price != self.back_orders[-1].sell_price: ##we get a different exit position
                                order_state = self.CancelOrder(self.back_orders[-1].sell_uid) ##cancel the current order
                                if order_state == 1 or order_state == -1:             ##sell order is Canceled
                                    self.MakeSellOrder(sell_pos)                   ##execute order
                                elif order_state == -1:                               ##order has been filled
                                    self.remove_last_backlog()                        ##remove the last block since its filled       
                                elif isinstance(sell_pos, Block) and sell_pos.sell_price == self.back_orders[-1].sell_price: ##we get a different exit position
                                    self.log_activities("",str(sell_pos.sell_price))
                                    print("SELL ORDER IS GOOD ***********")
                                    print("")
                            elif sell_pos < 0:                                 ##we need a support buy block
                                buy_pos = self.market_study()                  ##find a buy position
                                if isinstance(buy_pos, Block):
                                    self.add_to_backlog(buy_pos)               ##back log it
                                    if self.MakeBuyOrder(buy_pos) == 0:                 ##execute order  
                                         self.remove_last_backlog()                        ##remove the last block since its been cancelled    
                        else:
                            self.remove_last_backlog()                        ##remove the last block since its been cancelled    
                            
            else:
                buy_pos = self.market_study() ##found buy position
                if isinstance(buy_pos, Block):                          
                    self.add_to_backlog(buy_pos) ##back log it
                    if self.MakeBuyOrder(buy_pos) == 0:                 ##execute order  
                        self.remove_last_backlog()                        ##remove the last block since its been cancelled  
                                
                        
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
          #  break
                    
                
                
            

def main():
     
    target_xrp = trading_account('BTC','USDT','o7F2kS6QGIzbMm73iTXmwXlDqbAV4bIHFJcKsPw6dMf447nk7okcRVyprbT8t2Fu','8bzSZklysXWhv4yxU9RKGlVbwmuZuzm0o1VaqjfIs4eZLKGmCeNY3XdSlAeHFj1k',270)    
    target_xrp.trade()
   # target_eos = trading_account('EOS','USDT','o7F2kS6QGIzbMm73iTXmwXlDqbAV4bIHFJcKsPw6dMf447nk7okcRVyprbT8t2Fu','8bzSZklysXWhv4yxU9RKGlVbwmuZuzm0o1VaqjfIs4eZLKGmCeNY3XdSlAeHFj1k',250)   
    
  # while True:
        
  #      target_eos.trade()
    #target.back_test()

    
        
    

if __name__ == '__main__':
    main()
