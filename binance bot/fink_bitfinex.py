import base64
import hashlib
import hmac
import json
import time
import datetime

import requests



## Order book block
class Block(object):

    def __init__(self,price,quantity,base,position,booksum):

        self.price = price
        self.quantity_units = quantity
        self.quantity_base = base
        self.position = position
        self.weight = booksum
        
        
 ## Order Packet      
class Packet(object):

    def __init__(self,uid,packet_type,packet_price,packet_quantity):
        
        self.UID = uid
        self.packet_type = packet_type  ##LIMIT_BUY or LIMIT_SELL
        self.packet_price = packet_price
        self.packet_quantity = packet_quantity
        
        
        

        

class trading_account(object):
    
    def __init__(self, currency,base,key,secret):
        
        self.api_key = key
        self.api_secret = secret
        
        self.exchange_fee = 1.003
        
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
        
        self.ticker_close = []
        
        self.balance = 0
        self.budget = 500  ##USD
        self.back_orders = []
        
        
        
    def get_ticker(self):
        pair_name = "t" + self.currency + self.base##e..g tBTCUSD
    
        str_url = 'https://api.bitfinex.com/v2/tickers?symbols=' + pair_name
        payloadObject = {
                #'request' : '/v2/tickers?symbols=tBTCUSD,tLTCUSD,fUSD'
                #'request' : 'https://api.bitfinex.com/v2/tickers?symbols=tBTCUSD,tLTCUSD,fUSD'
                #'symbol' : 'BTCUSD',
            #'symbol' : 'XRPUSD',
            }

        payload_json = json.dumps(payloadObject)
        payload = base64.b64encode(bytes(payload_json, "utf-8"))

        m = hmac.new(self.api_secret, payload, hashlib.sha384)
        m = m.hexdigest()

        #headers
        headers = {
            'X-BFX-APIKEY' : self.api_key,
            'X-BFX-PAYLOAD' : base64.b64encode(bytes(payload_json, "utf-8")),
            'X-BFX-SIGNATURE' : m
            }

        # Get date and time in YYYYMMDD_HHMMSS format

        # Execute  API and retieve data, keep pinging api until data is retreived
        while True: 
            try:
                r = requests.get(str_url, data=payloadObject, headers=headers).json()[0]
                self.ticker_close.append(float(r[7]))
                return 1
            except:
                print("can't get data for pair")
                time.sleep(60)
        
        
    def get_historical_data(self):
        
        self.time *= 0
        self.open *= 0
        self.close *= 0
        self.high *= 0
        self.low *= 0
        self.vol *= 0
        
        
        #print("getting data........")
        
        str_url = 'https://api-pub.bitfinex.com/v2/candles/trade:12h:t'+self.symbol+'/hist?limit=1440'
        
    
    
        payloadObject = {
                # "request": '/v2/candles',
                #"limit"= 1000
            }

    
        payload_json = json.dumps(payloadObject)
        payload = base64.b64encode(bytes(payload_json, "utf-8"))

        m = hmac.new(self.api_secret, payload, hashlib.sha384)
        m = m.hexdigest()
        
        #headers
        headers = {
            'X-BFX-APIKEY' : self.api_key,
            'X-BFX-PAYLOAD' : base64.b64encode(bytes(payload_json, "utf-8")),
            'X-BFX-SIGNATURE' : m
            }
   
        # Execute  API and retieve data
        req = requests.get(str_url, data=payloadObject, headers=headers).json()
        #print(req)

    
        for i in range (len(req)):
            self.time.append(i)
            self.open.append(float(req[len(req)-i-1][1]))
            self.close.append(float(req[len(req)-i-1][2]))
            self.high.append(float(req[len(req)-i-1][3]))
            self.low.append(float(req[len(req)-i-1][4]))
            self.vol.append(float(req[len(req)-i-1][5]))
        
        
        
    def get_orderbook(self):
        
        
        ##clear out current orderbook
        self.bid *= 0
        self.ask *= 0 
        
        
        ##get orderbook 
        
        key = 'vmY34UGhFaTyFVz4R5nDjCHQP9oohKW6kxiVSH3GXFn'
        secret = b'z9gfn0JMTWQzIEcjlTiaLfdv6kBIHfKQiNe2QduZkml'
        
        #print("___________getting orderbook for ", self.symbol)
        str_url = 'https://api.bitfinex.com/v1/book/' + self.symbol + "?limit_bids=1000&&limit_asks=1000"
    
        payloadObject = {}

        payload_json = json.dumps(payloadObject)
        payload = base64.b64encode(bytes(payload_json, "utf-8"))

        m = hmac.new(secret, payload, hashlib.sha384)
        m = m.hexdigest()
        
        #headers
        headers = {
            'X-BFX-APIKEY' : key,
            'X-BFX-PAYLOAD' : base64.b64encode(bytes(payload_json, "utf-8")),
            'X-BFX-SIGNATURE' : m
            }
   
        # Execute  API and retieve data
        req = requests.get(str_url, data=payloadObject, headers=headers).json()
        ##{"bids":[{"price":"0.031458","amount":"4","timestamp":"1548640411.0"}],"asks":[{"price":"0.031461","amount":"17.39989262","timestamp":"1548640411.0"}]}
        
        b_sum = 0
        b_pos = 0 
        for b in req['bids']:
            
            quantity_price = float(b['price'])
            quantity_unit = float(b['amount'])
            quantity_base = quantity_unit * quantity_price
            b_sum += quantity_base
            
            self.bid.append(Block(quantity_price,quantity_unit,quantity_base,b_pos,b_sum))
            b_pos+=1 
            
            
        a_sum = 0
        a_pos = 0 
        for b in req['asks']:
            
            quantity_price = float(b['price'])
            quantity_unit = float(b['amount'])
            quantity_base = quantity_unit * quantity_price
            a_sum += quantity_base
            
            self.ask.append(Block(quantity_price,quantity_unit,quantity_base,a_pos,a_sum))
            a_pos+=1 
     
            

            
            
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
                        scenario += 1
                    else:
                        scenario += -1 
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
  
                    if x > 0 and y > 0 and self.bid[x].price >= min(self.close):
                        sl = self.bid[x].price / self.close[-1] 
                        rl  = self.ask[y].price / self.bid[x].price
                        if rl  > self.exchange_fee:
                            #print("")
                            #print("Bid: ", self.bid[x].price, "___", self.bid[x].weight)
                            #print("Ask: ", self.ask[y].price, "___", self.ask[y].weight)
                            #print("Rl: ", rl, " SL: ",sl)
                            #print("")
                            
                            w = self.Optimise(self.bid[x].price,rl,sl)
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
            print("Short at ", self.bid[short_pos].price, " then Long at ", self.ask[long_pos].price)
            #print("Return limit: ", self.ask[long_pos].price / self.bid[short_pos].price)
            self.agent_weight = 150 ##how much the agent is using for the order in base
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
        if len(self.back_orders) > 0:
            if self.ticker_close[-1] >= self.back_orders[-1].price:
                return -1
            else:
                loss = self.back_orders[-1].quantity_base * ( 1 - (self.ticker_close[-1] / self.back_orders[-1].price))         
        else:
            loss = 0
            
        p = rl - self.exchange_fee
        
        quantity_base = self.agent_weight + (loss / (1 + p)) ##calculate how many btc we need to recover previous loss
        quantity_units = quantity_base / entry_block.price
        
        entry_block.quantity_units = quantity_units
        entry_block.quantity_base = quantity_base
        
        if entry_block.quantity_base <= self.balance:
            print("Making Entry at Block: ", entry_block.position, "..... Rate: ", entry_block.price, ".... Base: ",entry_block.quantity_base, "... Units: ",entry_block.quantity_units)
            print("")
            return entry_block
        else:
            print("<<<<<<<<<<<<<<BALANCE NOT ENOUGH>>>>>>>>>>")
            return 0
        
        
        
    def GetExitPosition(self):
        
        self.get_orderbook()
        exit_order = 0
        
        entry = self.back_orders[-1] ##get last entry position
        print("updating exit position.... entry was at: %.9f") % (entry.price)
        
        if entry == 0:
            target_weight = self.agent_weight
        else:
            target_weight = entry.booksum
            
        
        ##find whether we need to shift up or down the price to match weight
        for i in self.ask:
            exit_order = i
            if (i.booksum > target_weight):
                break
                        
        if exit_order > 0:
            d = (exit_order.price / entry.price) - 1 
            if d > self.exchange_fee:
                
                exit_order.quantity_base = entry.quantity_units * (self.ticker_close[-1] / entry.price)
                exit_order.quantity_units = entry.quantity_units
                
                print("Exit at Block: %d ..... Rate: %.9f....Volume: %.9f....Units:%.9f") % (exit_order.position, exit_order.price, exit_order.quantity_base, exit_order.quantity_units)
                return exit_order
            else:
                print("Supporting with a new Entry")
                return -1
        else:
            print("No Exit found")
            return 0
        
        
        
    def back_test(self):
        import matplotlib.pyplot as plt
        
        print("Commencing Back testing")
        
        timeout = 1000 
        state = 0 
        self.balance = self.budget
        
        
        ##For plotting
        buy = []
        buy_time = []
        sell = []
        sell_time = []
        
        balance = []
        b_time = []
        
        r = [0]
        r_time = [0] 
        t = [0]
        i = 0
        
        holding = [0]
        h_time = [0]
        total_balance = [self.balance]
        t_time = [0]
        
        self.get_ticker()
        start_price = self.ticker_close[-1]
        
        self.profit = 0
        self.loss = 0
        
        velocity = 0
        
        #plt.ion()
        fig = plt.figure(1)
        fig.show()
        fig.canvas.draw()
        ax = fig.add_subplot(211)
        
        ax.set_title (self.symbol)
        
        ax.set_ylim(start_price * 0.9,start_price * 1.1)
        ax.set_xlim(0,10800)
        ax.grid()
        
        mng = plt.get_current_fig_manager()
        mng.resize(*mng.window.maxsize())
        
        
        cLine, = ax.plot(t, self.ticker_close, label='Close',color='black',linewidth=2)
        b = ax.plot(buy_time, buy, '_', markersize=5, color='blue', label = 'buy')
        s = ax.plot(sell_time, sell, '_', markersize=5, color='red', label = 'sell')
            
        bx = fig.add_subplot(212)
        bx.set_title ("Accumulated Trade Returns")
        bx.set_ylim(-10, 10)
        bx.set_xlim(0,36000)
        bx.grid()
        pl, = bx.plot(r_time, r, label='return',color='blue',linewidth=2)
        
        
        while i <= timeout:

            
            StartTime = datetime.datetime.now()
            self.get_ticker()
            print("Current Closing price: ", self.ticker_close[-1], self.base)
            
            
            ##4 states
            ## 0 state --> no orders no balance
            ## 1st state --> buy order no balance
            ## 2nd state --> no order balance
            ## 3rd state --> sell order balance
            
            if state == 0:
                buy_pos = self.market_study()
                if buy_pos != 0:
                    buy.append(buy_pos.price)
                    buy_time.append(i)
                    state = 1
                elif buy_pos < 0:
                    state = 2 ##go back to exit    
                    
            elif state == 1:
                if self.ticker_close[-1] <= buy_pos.price: ##assume buy order went through
                    
                    self.balance = self.balance - buy_pos.quantity_base
                    balance.append(self.balance)
                    b_time.append(i)

                    self.back_orders.append(buy_pos) ##put the entry order as a back order
                    state = 2 ## go next state
                    
                else:
                    state = 0 ## go previous state to re-do buy entry
                    
            elif state == 2:
                
                sell_pos = self.GetExitPosition() ##get Exit position
                
                if sell_pos > 0:
                    sell_time.append(i)
                    sell.append(sell_pos.price)
                    state = 3
                elif sell_pos < 0: ##it's gone below previous entry, make a new entry
                    state = 0 
                    
            elif state == 3:
                
                if self.ticker_close[-1]>= sell_pos.price: ##assuming that our sell order went through
  
                    print("***** SOLD *****")
                    
                    self.balance += sell_pos.quantity_base * ( 1 - (self.exchange_fee))
                    
                    balance.append(self.balance)
                    b_time.append(i)
                  
                    trade_return = ((sell_pos.price / self.back_orders[-1].price) - (1+self.exchange_fee)) * 100
                    if (trade_return > 0):
                        self.profit += 1
                    else:
                        self.loss += 1
                        
                    self.total_return = r[-1] + trade_return
                    r.append(r[-1] + trade_return)
                    r_time.append(i)            
                    state = 0   
                    
                    del self.back_orders[-1]
                    
                else:
                    state = 2 ## go previous state to re-do exit
                    
            i+=1
            t.append(i)
            
            
            print("")
            print("Back Orders: ", len(self.back_orders))
            total_quantity = 0 
            for x in self.back_orders:
                print("Back order at price ", x.price, " for Base ", x.quantity_base, " or Quantity ", x.quantity_units)
                total_quantity += x.quantity_units 
                
                
            holding.append(total_quantity *self.ticker_close[-1])
            h_time.append(i)
            

            EndTime = datetime.datetime.now()
            tdiff = EndTime - StartTime 
            timetaken = int(tdiff.total_seconds())
            
            if timetaken == 0:
                timetaken = 1
            
            
            total_balance.append(holding[-1] + self.balance)
            t_time.append(i)
            total_return = ((total_balance[-1] / self.budget) - 1) * 100
            
            if total_return != 0:
                velocity = (total_return * 60 * 60) / timetaken 
                
            
            print("")
            movement = (self.ticker_close[-1] / start_price) - 1
            print("Market Movement: ", movement * 100)
            print("Holding: ", holding[-1] ,"..... Balance ",self.balance , "....total_balance ", total_balance[-1] ) 
            print("State: ",state," Total Return: ",total_return," wins: ",self.profit," loss: ",self.loss, " .... time taken: ",timetaken," complete: ",(i*100)/timeout) 
            print("velocity: ", velocity)
            print("______________DONE___________________")
            print("")
                
             
            
        cLine, = ax.plot(t, self.ticker_close, label='Close',color='black',linewidth=2)
        b = ax.plot(buy_time, buy, '_', markersize=5, color='blue', label = 'buy')
        s = ax.plot(sell_time, sell, '_', markersize=5, color='red', label = 'sell')
        pl, = bx.plot(r_time, r, label='return',color='blue',linewidth=2)
        fig.canvas.draw()
            
                


def main():
     
    target = trading_account('BSV','USD','8DRfO5aIcF0ESv6PqntprFiBSnGsZWExTKd3SVQ8Jod',b'yoE8RqEooBzRRZCZaGxySV1obTyrznyLaXKvCntZoXs')    
    target.back_test()

    
        
    

if __name__ == '__main__':
    main()





