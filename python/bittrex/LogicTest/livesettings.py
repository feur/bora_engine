from collections import OrderedDict
from decimal import Decimal, getcontext

getcontext().prec = 8

#LOCAL DB#
#DB_NAME = "aurade"
#DB_HOST = "localhost"
#3DB_PW = "Amm02o16!"
#DB_USER = "root"

#LIVE DB#
DB_NAME = "Bora"
DB_HOST = "localhost"
DB_PW = "Amm02o16!"
DB_USER = "root"

APIVER = 'v1.1'

DIR_GUNBOT = "~/autoscripts/gunbot"

#Andrew
# API_KEY = "d9cbabb7e37a4b05900fee6595d5be10"
# API_SECRET = "a9ee01b0fe784fdf9e089563515e720d"

#TARAS
API_KEY = "f5d8f6b8b21c44548d2799044d3105f0"
API_SECRET = "b3845ea35176403bb530a31fd4481165"

MIN_TRADE_LIMIT = Decimal('0.00050000')

DB_TBL_POOLGROWTH = "pool_growth"
DB_TBL_BALANCEPERCURRENCY = "pool_balances"
DB_TBL_TRADEHISTORY = "pool_trade_history"
DB_TBL_MARKET_INVESTMENTS = "pool_market_investments"
DB_TBL_POOL_TRANSACTION = "pool_transaction_history"
DB_TBL_WITHRAWALS = "withdraws"
DB_TBL_DEPOSITS = "deposits"
DB_TBL_USER_INVESTMENTS_C = "user_investments_current"
DB_TBL_USER_INVESTMENTS_U = "user_investments_updated"
DB_TBL_USER_INVESTMENTS_G = "user_investments_growth"

GROWTH_TYPE_TICK = 'Tick'
GROWTH_TYPE_TRANSACT = 'Transact'
GROWTH_TYPE_DEPOSIT = 'Deposit'
GROWTH_TYPE_WITHDRAW = 'Withdrawal'

BITTREX_SELL_FACTOR = Decimal('0.9975')
VERIFICATION_MINUTE_TO = 10

#from sql manual
AFFECTEDROWS_ONDUP_INSERT = 1
AFFECTEDROWS_ONDUP_UPDATE = 2

ORDERSTAT_COMPLETE = 'Complete'
ORDERSTAT_PARTIAL = 'Partial'
ORDERSTAT_OPEN = 'Open'
ORDERSTAT_ERROR = 'Error'

# INTERVAL_LIST = [{'id': '1 H', 'amount': 1, 'unit':'HOUR'}\
#                             ,{'id': '12 H', 'amount': 12, 'unit':'HOUR'}
#                             ,{'id': '1 D', 'amount': 1, 'unit':'DAY'}
#                             ,{'id': '1 W', 'amount': 1, 'unit':'WEEK'}
#                             ,{'id': '1 M', 'amount': 1, 'unit':'MONTH'}
#                             ,{'id': '1 Y', 'amount': 1, 'unit':'YEAR'}
#                             ]
INTERVAL_LIST = [('1H', {'amount': 1, 'unit':'HOUR'})\
                ,('12H',{'amount': 12, 'unit':'HOUR'})
                ,('1D', {'amount': 1, 'unit':'DAY'})
                ,('1W', {'amount': 1, 'unit':'WEEK'})
                ,('1M', {'amount': 1, 'unit':'MONTH'})
                ,('1Y', {'amount': 1, 'unit':'YEAR'})
                ]
INTERVAL_LIST = OrderedDict(INTERVAL_LIST)
