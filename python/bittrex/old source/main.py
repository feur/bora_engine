from settings import APIVER, API_KEY, API_SECRET
from pool import BittrexPool
from user_investment import UserInvestment
from apscheduler.schedulers.blocking import BlockingScheduler
from warnings import filterwarnings
import decimal
import MySQLdb

filterwarnings('ignore', category=MySQLdb.Warning)

decimal.getcontext().prec = 9

#poolTracker = BittrexPool(API_KEY, API_SECRET, api_version=APIVER) 
auradeTracker = UserInvestment(API_KEY, API_SECRET, api_version=APIVER)  

def hourlyTask():
    auradeTracker.processPoolTransactions()
    auradeTracker.fetchPoolOrders()
    auradeTracker.processPoolOrders()
    auradeTracker.updateMarketProfits()
    auradeTracker.updateAllUsersInvestments()
    auradeTracker.trackUserInvestments()
    
scheduler = BlockingScheduler()
scheduler.add_job(hourlyTask, 'interval', hours=1)
scheduler.start()

# order_list = poolTracker.get_order_history('BTC-LTC')
# order_list = [order for order in order_list['result']]
# for o in order_list:
#     if o['Exchange'] == 'BTC-LTC':
#         print o
#         print "!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!1"
# #         
# # a = poolTracker.get_deposit_history()
# # a = a['result']
# # 
# # for b in a:
# #     print b
# #     
# # a = poolTracker.get_withdrawal_history()
# # a = a['result']
# # for b in a:
# #     print b


