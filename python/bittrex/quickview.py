import MySQLdb
from settings import *

def quickView():
    print "########### QuickView ###########"
    dbcon = MySQLdb.connect(DB_HOST, DB_USER, DB_PW, DB_NAME)
    dbcur = dbcon.cursor(MySQLdb.cursors.DictCursor)
    
    sql_query = "SELECT Balance from pool_growth ORDER BY DateTime DESC LIMIT 1"
    dbcur.execute(sql_query)
    balance = dbcur.fetchone()
    
    if balance:
        print "Latest Pool: {0}\n".format(balance['Balance'])
    
    sql_query = "SELECT uic.UserID, u.name "\
                "FROM (SELECT DISTINCT UserID FROM user_investments_current) uic "\
                    "INNER JOIN (SELECT id, name from users) u "\
                    "ON u.id = uic.UserID"
    dbcur.execute(sql_query)
    user_list = dbcur.fetchall()
    for user in user_list:
        sql_query = "SELECT * from user_investments_current WHERE UserID = %s"
        dbcur.execute(sql_query, (user['UserID'], ))
        user_investments = dbcur.fetchall()
        print "UserID: {0}\nName: {1}".format(user['UserID'], user['name'])
        total_investment_usd = 0
        total_investment_btc = 0
        for investment in user_investments:
            print "Investment {0}: {1} USD, {2} BTC"\
            .format(investment['InvestmentID'], investment['USD']\
                , investment['BTC'])
            total_investment_usd += investment['USD']
            total_investment_btc += investment['BTC']
        print "Total: {0} USD, {1} BTC"\
            .format(total_investment_usd, total_investment_btc)
        print ""
        
if __name__ == "__main__":
    quickView()
