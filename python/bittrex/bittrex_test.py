from bittrex.bittrex import *

my_bittrex = Bittrex("f5d8f6b8b21c44548d2799044d3105f0", "b3845ea35176403bb530a31fd4481165", api_version=API_V2_0)

data = my_bittrex.get_candles('BTC-SALT',tick_interval=TICKINTERVAL_FIVEMIN)

if(data['success'] == True):
            data = data['result']
            for item in data:
                print(item["C"], item["T"]);
  
            
            
""""
print(my_bittrex.get_latest_candle('BTC-SALT',tick_interval=TICKINTERVAL_FIVEMIN))
print(my_bittrex.get_candles('BTC-SALT',tick_interval=TICKINTERVAL_FIVEMIN))
"""


 