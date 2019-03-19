import base64
import hashlib
import hmac
import json
import time
import requests
from common_objects import *

  

def get_symbol_details(currency,base):
    symbol = currency + base
    url = "https://api.bitfinex.com/v1/symbols_details"
    response = requests.get(url).json()
 
    for r in response:
        if r["pair"] == symbol.lower():
            return Target(symbol,r["price_precision"],r["initial_margin"],r["minimum_margin"],r["maximum_order_size"],r["minimum_order_size"])
    
    
def get_symbol_ticker_last(currency,base):

    url = "https://api.bitfinex.com/v1/pubticker/" + currency.lower() + base.lower()
    response = requests.get(url).json()
    
    if len(response) > 1: 
        return float(response["last_price"])
    else:
        print(response)
        #print(response['message'])
        return 0
    
    


def get_symbol_candles(currency,base):

    url = 'https://api.bitfinex.com/v2/candles/trade:12h:'+"t"+currency.upper()+base.upper()+'/hist?'+"limit=5000"
    response = requests.get(url).json()
    
    return response


def get_asset_balance(key,secret,asset):
    
    str_url = 'https://api.bitfinex.com/v1/balances'
    payloadObject = {
       'request' : '/v1/balances',
       'nonce':str(time.time() * 100000) #convert to string
       }
            

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
    for r in req: 
        if r["currency"] == asset.lower():
            return float(r["amount"])
    
    return 0


def run_order(key,secret,symbol,amount,price,side):
    
    
    BASE_URL = "https://api.bitfinex.com/"
    nonce = str(int(round(time.time() * 100000)))
    
    
    path = "v1/order/new"
    
    body = {
            "request": '/v1/order/new',
            'nonce': nonce ,
            "symbol": symbol.upper(),
            "amount": str(amount),
            "price": price,
            "exchange": 'bitfinex',
            "side": side,
            "type": 'limit'
        
            }
    rawBody = json.dumps(body)
    
    signature = "/api/" + path + nonce + rawBody
    h = hmac.new(secret, signature.encode('utf8'), hashlib.sha384)
    signature = h.hexdigest()
    
    
    
    payload_json = json.dumps(body)
    payload = base64.b64encode(bytes(payload_json, "utf-8"))
    m = hmac.new(secret, payload, hashlib.sha384)
    m = m.hexdigest()
    
    headers = {
            "bfx-nonce": nonce,
            'X-BFX-APIKEY' : key,
            'X-BFX-PAYLOAD' : base64.b64encode(bytes(payload_json, "utf-8")),
            'X-BFX-SIGNATURE': m,
            "content-type": "application/json"      
            }
    
    
    result = requests.post(BASE_URL + path, headers=headers, data=rawBody, verify=True).json()
    print(result)
    
    if len(result) > 1: 
        return result['order_id']
    else:
        print(result['message'])
        return 0
        #return str(result['message'])
    
    
 
     



def get_order_status(key,secret,UID):
    
       
    BASE_URL = "https://api.bitfinex.com/"
    nonce = str(int(round(time.time() * 100000)))
    
    order_status = {'status':"",'executedQty':"",'origQty':""}
    
    
    path = "/v1/order/status"
    
    body = {
            "request": '/v1/order/status',
            'nonce': nonce ,
            'order_id' : UID
        
            }
    rawBody = json.dumps(body)
    
    signature = "/api/" + path + nonce + rawBody
    h = hmac.new(secret, signature.encode('utf8'), hashlib.sha384)
    signature = h.hexdigest()  
    
    payload_json = json.dumps(body)
    payload = base64.b64encode(bytes(payload_json, "utf-8"))
    m = hmac.new(secret, payload, hashlib.sha384)
    m = m.hexdigest()
    
    headers = {
            "bfx-nonce": nonce,
            'X-BFX-APIKEY' : key,
            'X-BFX-PAYLOAD' : base64.b64encode(bytes(payload_json, "utf-8")),
            'X-BFX-SIGNATURE': m,
            "content-type": "application/json"      
            }
    
    
    result = requests.post(BASE_URL + path, headers=headers, data=rawBody, verify=True).json()
    
    if len(result) > 1: 
        if result['is_cancelled'] == True:
            order_status['status']= "CANCELED"
        elif float(result['executed_amount']) == float(result['original_amount']):
            order_status['status']= "FILLED"
        elif float(result['executed_amount']) == 0:
            order_status['status']= "NEW"
        elif float(result['executed_amount']) > 0 and float(result['executed_amount']) < float(result['original_amount']):
            order_status['status']= "PARTIALLY_FILLED"
            
        order_status['executedQty']= float(result['executed_amount'])
        order_status['origQty']=float(result['original_amount'])
        
        return order_status
        
    else:
        return str(result['message'])
      
    
    
def cancel_order(key,secret,UID):
    
  
    
    BASE_URL = "https://api.bitfinex.com/"
    nonce = str(int(round(time.time() * 100000)))
    
    
    path = "/v1/order/cancel"
    
    body = {
            "request": '/v1/order/cancel',
            'nonce': nonce ,
            'order_id' : UID
        
            }
    rawBody = json.dumps(body)
    
    signature = "/api/" + path + nonce + rawBody
    h = hmac.new(secret, signature.encode('utf8'), hashlib.sha384)
    signature = h.hexdigest()  
    
    payload_json = json.dumps(body)
    payload = base64.b64encode(bytes(payload_json, "utf-8"))
    m = hmac.new(secret, payload, hashlib.sha384)
    m = m.hexdigest()
    
    headers = {
            "bfx-nonce": nonce,
            'X-BFX-APIKEY' : key,
            'X-BFX-PAYLOAD' : base64.b64encode(bytes(payload_json, "utf-8")),
            'X-BFX-SIGNATURE': m,
            "content-type": "application/json"      
            }
    
    
    result = requests.post(BASE_URL + path, headers=headers, data=rawBody, verify=True).json()
    print(result)
    
    if len(result) > 1:     
        return 1
    else:
        print(result['message'])
        return 0
        #return str(result['message'])

    
    


def get_orderbooks(symbol):
    
    url = "https://api.bitfinex.com/v1/book/" + symbol.lower()
    req = requests.get(url).json()
    bid = []
    ask = []
    
    if len(req) == 1:
        print(req)
        time.sleep(70)
        return 0
        
    
    b_sum = 0
    b_pos = 0 
    for b in req['bids']:
            
        quantity_price = float(b['price'])
        quantity_unit = float(b['amount'])
        quantity_base = quantity_unit * quantity_price
        b_sum += quantity_base
        
        bid.append(Block(0,0,quantity_price,0,quantity_unit,quantity_base,b_pos,b_sum))
        b_pos+=1 
            
            
    a_sum = 0
    a_pos = 0 
    for b in req['asks']:
            
        quantity_price = float(b['price'])
        quantity_unit = float(b['amount'])
        quantity_base = quantity_unit * quantity_price
        a_sum += quantity_base
            
        ask.append(Block(0,0,0,quantity_price,quantity_unit,quantity_base,a_pos,a_sum))
        a_pos+=1 
        
    return bid, ask









def Get_Bitfinex_Pair(key,secret, base, currency):
        
    pair_name = "t" + currency + base##e..g tBTCUSD
    
    str_url = 'https://api.bitfinex.com/v2/tickers?symbols=' + pair_name
    payloadObject = {
        #'request' : '/v2/tickers?symbols=tBTCUSD,tLTCUSD,fUSD'
        #'request' : 'https://api.bitfinex.com/v2/tickers?symbols=tBTCUSD,tLTCUSD,fUSD'
        #'symbol' : 'BTCUSD',
        #'symbol' : 'XRPUSD',
    }

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

    # Get date and time in YYYYMMDD_HHMMSS format
    str_date_time= time.strftime('%Y%m%d'+'_'+'%H%M%S', time.localtime(time.time()))

    # Execute  API and retieve data, keep pinging api until data is retreived
    while True: 
        try:
            r = requests.get(str_url, data=payloadObject, headers=headers).json()[0]
            print(r)
            return Pair(pair_name,currency,base,r[1],r[2],r[3],r[4],r[5],r[6],r[7],r[8],r[9],r[10],str_date_time) 
        except:
            return 0
            print("can't get data for pair")
    
     
        






def Get_Bitfinex_Active_Positions(key,secret):
    
    '''
    [
     [
      SYMBOL, 
      STATUS, 
      AMOUNT, 
      BASE_PRICE, 
      MARGIN_FUNDING, 
      MARGIN_FUNDING_TYPE,
      PL,
      PL_PERC,
      PRICE_LIQ,
      LEVERAGE
      ...
      ], 
      ...
      ]
     '''
     
     
    positions = []
    
    BASE_URL = "https://api.bitfinex.com/"
    nonce = str(int(round(time.time() * 1000)))
    
    body = {}
    rawBody = json.dumps(body)
    path = "v2/auth/r/positions"
    
    signature = "/api/" + path + nonce + rawBody
    h = hmac.new(secret, signature.encode('utf8'), hashlib.sha384)
    signature = h.hexdigest()
    
    headers = {
            "bfx-nonce": nonce,
            "bfx-apikey": key,
            "bfx-signature": signature,
            "content-type": "application/json"      
            }
    
    
    result = requests.post(BASE_URL + path, headers=headers, data=rawBody, verify=True).json()
    
    
    str_date_time= time.strftime('%Y%m%d'+'_'+'%H%M%S', time.localtime(time.time()))
    
    for r in result:
        print(r)
        positions.append(Active_Position(r[0],r[1],r[2],r[3],r[4],r[5],r[6],r[7],r[8],r[9],str_date_time))
        
    return positions
        
    

def Get_Bitfinex_Active_Orders(key,secret):
    
        '''
        [{
                "id":448411365,
                "symbol":"btcusd",
                "exchange":"bitfinex",
                "price":"0.02",
                "avg_execution_price":"0.0",
                "side":"buy",
                "type":"exchange limit",
                "timestamp":"1444276597.0",
                "is_live":true,
                "is_cancelled":false,
                "is_hidden":false,
                "was_forced":false,
                "original_amount":"0.02",
                "remaining_amount":"0.02",
                "executed_amount":"0.0"
            }]
        '''
        
        orders = []
        
        str_url = 'https://api.bitfinex.com/v1/orders'
        payloadObject = {
            "request": "/v1/orders",
            'nonce':str(time.time() * 100000) 
        }

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
        
        str_date_time= time.strftime('%Y%m%d'+'_'+'%H%M%S', time.localtime(time.time()))

        
        for i in req:
            order_type = str(i['side']) + ' ' + str(i['type'])
            orders.append(Active_Order(i['symbol'],order_type,i['id'],i['price'],i['original_amount'],i['remaining_amount'],i['timestamp']))

        return orders
            
            
        
        
        
def Get_Bitfinex_Margin_Positions(key,secret):
        
    '''
    "margin_balance":"14.80039951",
    "tradable_balance":"-12.50620089",
    "unrealized_pl":"-0.18392",
    "unrealized_swap":"-0.00038653",
    "net_value":"14.61609298",
    "required_margin":"7.3569",
    "leverage":"2.5",
    "margin_requirement":"13.0",
    "margin_limits":[{
            "on_pair":"BTCUSD",
            "initial_margin":"30.0",
            "margin_requirement":"15.0",
            "tradable_balance":"-0.32924325966666666
    '''
        
    print("")
    print("____Getting margin positions")
    
    str_url = 'https://api.bitfinex.com/v1/margin_infos'
    payloadObject = {
        "request": "/v1/margin_infos",
        'nonce':str(time.time() * 100000) 
    }

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
        
    # Get date and time in YYYYMMDD_HHMMSS format
    str_date_time= time.strftime('%Y%m%d'+'_'+'%H%M%S', time.localtime(time.time()))
    #print('str_date_time: '+str_date_time)
        
    # Execute  API and retieve data
    req = requests.get(str_url, data=payloadObject, headers=headers).json()
    
    margin_position = Margin_Position(req[0]['margin_balance'],req[0]['tradable_balance'],req[0]['unrealized_pl'],req[0]['unrealized_swap'],req[0]['net_value'],req[0]['required_margin'],req[0]['leverage'],req[0]['margin_requirement'],str_date_time)
    
    return margin_position



def Cancel_All_Bitfinex_Orders(key,secret):
    
    print("")
    print("____Cancelling All Orders")
    
    str_url = 'https://api.bitfinex.com/v1/order/cancel/all'
    payloadObject = {
        "request": '/v1/order/cancel/all',
        'nonce':str(time.time() * 100000) 
    }

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
        
    # Get date and time in YYYYMMDD_HHMMSS format
    str_date_time= time.strftime('%Y%m%d'+'_'+'%H%M%S', time.localtime(time.time()))
        
    # Execute  API and retieve data
    req = requests.get(str_url, data=payloadObject, headers=headers).json()
    print(req)
    
    return 1
    
    





    
    

