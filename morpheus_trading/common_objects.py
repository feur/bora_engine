

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
        
        
class Target(object):
    
    def __init__(self,symbol,pp,im,mm,mxo,mno):
        self.symbol = str(symbol)
        self.price_precision = pp
        self.initial_margin = im
        self.minimum_margin = mm
        self.maximum_order_size = mxo
        self.minimum_order_size = mno
        
        


class Balance(object):
    
    def __init__(self,balance_type,amount,currrency,available,timestamp):        
        self.type = str(balance_type)
        self.currency = str(currrency)
        self.amount = float(amount)
        self.available = float(available)
        self.last_updated = timestamp
        
class Pair(object):
    
    def __init__(self,pair_name,target_name,target_type,bid,bid_size,ask,ask_size,daily_change,dail_change_perc,last_price,volume,high,low,timestamp):        
        self.pair_name = str(pair_name)
        self.target_name = str(target_name)
        self.target_type = str(target_type)
        self.bid = float(bid)
        self.bid_size = float(bid_size)
        self.ask = float(ask)
        self.ask_size = float(ask_size)
        self.daily_change = float(daily_change)
        self.dail_change_perc = float(dail_change_perc)
        self.last_price = float(last_price)
        self.volume = float(volume)
        self.high = float(high)
        self.low = float(low)
        self.last_updated = timestamp
   
        
class Active_Order(object):
    
    def __init__(self,symbol,order_type,UID,price,original_amount,remaining_amount,timestamp):     
        self.symbol = str(symbol)
        self.order_type = str(order_type)
        self.price = float(price)
        self.original_amount = float(original_amount)
        self.remaining_amount = float(remaining_amount)
        self.timestamp = timestamp
        
        buy_uid = 0
        buy_price = 0
        sell_price = 0
        sell_uid = 0
    
        if order_type == "buy limit":
            buy_uid = UID
            buy_price = self.price
        elif order_type == "sell limit":
            sell_uid = UID
            sell_price = self.price
                   
        self.order_block = Block(buy_uid,sell_uid,buy_price,sell_price,self.remaining_amount,self.remaining_amount*self.price,0,0,"ADMIN",self.symbol)
        self.order_block.state = 1
       
      
        
        
class Active_Position(object):
    
    def __init__(self,symbol,status,amount,base_price,margin_funding,margin_funding_type,pl,pl_perc,price_liq,leverage,timestamp):    
        self.symbol = str(symbol)
        self.status = str(status)
        self.amount = float(amount)
        self.base_price = float(base_price)
        self.margin_funding = float(margin_funding)
        
       # if margin_funding_type == 0:
       #     self.margin_funding_type = "daily"
       # elif margin_funding_type == 1:
       #     self.margin_funding_type = "term"
       
        self.margin_funding_type = str(margin_funding_type)
            
        self.pl = float(pl)
        self.pl_perc = float(pl_perc)
        self.price_liq = float(price_liq)
        self.leverage = float(leverage)
    
        self.timestamp = timestamp

        
class Margin_Position(object):
    
    def __init__(self,margin_balance,tradable_balance,unrealized_pl,unrealized_swap,net_value,required_margin,leverage,margin_requirement,timestamp):
        self.margin_balance = float(margin_balance)
        self.tradable_balance = float(tradable_balance)
        self.unrealized_pl = float(unrealized_pl)
        self.unrealized_swap = float(unrealized_swap)
        self.net_value = float(net_value)
        self.required_margin = float(required_margin)
        self.leverage = float(leverage)
        self.margin_requirement = float(margin_requirement)
        self.timestamp = timestamp
        return 1
    
   
        
    
 
    

