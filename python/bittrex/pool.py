#from __future__ import division
import MySQLdb
import traceback
import datetime
from settings import *
from bittrex.bittrex import Bittrex, API_V2_0
from dateutil import relativedelta as rdelta
from decimal import *
from time import sleep
from warnings import filterwarnings

filterwarnings('ignore', category=MySQLdb.Warning)

getcontext().prec = 9

class DBHandler():
    def __init__(self):
        self.dbcon = None
        self._connect()
    
    def _connect(self):
        try:
            print "Connecting to database..."
            while(1):
                self.dbcon = MySQLdb.connect(DB_HOST, DB_USER, DB_PW, DB_NAME)
                if self.dbcon.open:
                    break
            print "Database connection established"
        except MySQLdb.OperationalError, e:
            print e
            
    def query(self, sql_query, param=[], single_fetch=False, exec_many=False):
        res = None
        dbcur = None
        
        try:
            if not self.dbcon.open:
                self._connect()
                
            dbcur = self.dbcon.cursor(MySQLdb.cursors.DictCursor)
            
            if not exec_many:
                dbcur.execute(sql_query, param)
            else:
                dbcur.executemany(sql_query, param)
            
            if not single_fetch:
                res = dbcur.fetchall()
            else:
                res = dbcur.fetchone()
            
            self.dbcon.commit()
            dbcur.close()
            
        except MySQLdb.OperationalError, e:
            self.dbcon.rollback()
            self.dbcon.close()
            print traceback.print_exc()
            print e
            
        except:
            print traceback.print_exc()
            
        finally:
            if dbcur:
                dbcur.close()
            return res
        

class BittrexPool(Bittrex):
    def __init__(self, api_key, api_secret, api_version=APIVER):
        Bittrex.__init__(self, api_key, api_secret, api_version=api_version)
        self.db = DBHandler()
        
    #@brief: calculate overall change in pool between two dates
    def getPoolTotalChange(self, start_date, end_date):
        try:
            total_growth = None
            sql_param = []
            if start_date == None and end_date == None:
            #get everything
                sql_query = "SELECT EXP(SUM(LOG(Growth + 1))) as total_growth "\
                            "FROM {table} where Type = 'Tick'"\
                            .format(table=DB_TBL_POOLGROWTH)
                sql_param = []
                
            elif start_date == None and end_date != None:
            #get from oldest record  to end_date
                sql_query = "SELECT EXP(SUM(LOG(Growth + 1))) as total_growth "\
                            "FROM {table} where "\
                            "DateTime <= %s AND Type = 'Tick'"\
                            .format(table=DB_TBL_POOLGROWTH)
                sql_param = (end_date,)
                
            elif start_date != None and end_date == None:
            #get from start_date to latest record
                sql_query = "SELECT EXP(SUM(LOG(Growth + 1))) as total_growth "\
                            "FROM {table} where "\
                            "DateTime > %s AND Type = 'Tick'"\
                            .format(table=DB_TBL_POOLGROWTH)
                            
                sql_param = (start_date,)
                
            else:
            #get from start_date to end_date
                sql_query = "SELECT EXP(SUM(LOG(Growth + 1))) as total_growth "\
                            "FROM {table} where DateTime > %s "\
                            "AND DateTime <= %s AND Type = 'Tick'"\
                            .format(table=DB_TBL_POOLGROWTH)
                sql_param = (start_date, end_date)
                
            total_growth = self.db.query(sql_query\
                , param=sql_param, single_fetch=True)
            
            total_growth = total_growth['total_growth']
            
            if total_growth == None:
                total_growth = Decimal('1')
            else:
                total_growth = Decimal(str(total_growth))
        except:
            print traceback.print_exc()
            
        finally:
            return total_growth
    
    def initializePool(self):
        try:            
            sql_query = "SELECT COUNT(ID) as tick_count from pool_growth "\
                        "WHERE Type = 'Tick' "
                        
            count = self.db.query(sql_query, single_fetch=True)
            count = count['tick_count']
            
            #database if fresh but bittrex is not, first time the app runs
            if count == 1:
                sql_query = "Update pool_growth set Growth = 0, Type = 'Init' "\
                            "WHERE ID = "\
                            "(SELECT ID from "\
                                "(SELECT MAX(ID) as ID from pool_growth) t)"
                count = self.db.query(sql_query)
                
        except:
            print traceback.print_exc()

            
    #@brief: update market_investment details of pool for all currency
    #@affected tables: market_investments, trade_history    
    def updateMarketProfits(self):
        print "########## Updating Profits #########"
        balance_list = self.getPoolBalances()
        balance_list = [balance for balance in balance_list \
                        if balance['Currency'] != 'BTC']

        for bal in balance_list:
            self._updateTickerProfit(bal)
        
        #track BTC changes based on pool balance only
        btcbalance = self.get_balance('BTC')
        if(btcbalance['success'] == True):
            btcbalance = btcbalance['result']
            market_investment = {}
            market_investment['Market'] = 'BTC'
            market_investment['PricePerUnit'] = 1
            market_investment['Profit'] = None
            market_investment['TotalUnits'] = btcbalance['Available']
            market_investment['Active'] = True
            market_investment['RemainingInvestment'] = None
            market_investment['LatestBalance'] = btcbalance['Available']
            self._saveMarketInvestments(market_investment)
        self.updatePoolGrowth(GROWTH_TYPE_TICK)
        
    #brief: save pool to database
    #@affected tables: pool_growth
    def updatePoolGrowth(self, growth_type, target_date=None\
        , offset=Decimal('0')):
        
        print "$Updating Pool Growth..."
        try:
            
            if(growth_type == GROWTH_TYPE_DEPOSIT\
               or growth_type == GROWTH_TYPE_WITHDRAW):
                #set growth to 0 if pool change is due to deposit/withdrawal
                latest_pool = {"Balance": self.getLatestPoolFromDB()} 
            else:
                latest_pool = {"Balance": self.getLatestPoolFromAPI()}
            
            sql_query = "SELECT * from {pool_growth} "\
                          "ORDER BY DateTime DESC LIMIT 1"\
                          .format(pool_growth=DB_TBL_POOLGROWTH)
            
            last_recorded_pool = self.db.query(sql_query, single_fetch=True)                    

            
            if (last_recorded_pool == None):
                last_recorded_pool = {}
                last_recorded_pool['Balance'] = Decimal('0')
                last_recorded_pool['Type'] = None

            if growth_type == 'Tick':
                if last_recorded_pool['Type'] != 'Tick'\
                and last_recorded_pool['Type'] != 'Init':
                    growth_type = 'Init'
                    last_recorded_pool['Balance'] = Decimal('0')
                    
                try:
                    latest_pool['Growth'] \
                        = (latest_pool['Balance'] - last_recorded_pool['Balance'])\
                          /(last_recorded_pool['Balance'] + offset)
                          
                except ZeroDivisionError:
                    latest_pool['Growth'] = Decimal('0')
                    
                except InvalidOperation:
                    latest_pool['Growth'] = Decimal('0')
                    
            else:                                  
                #set growth to 0 if pool change is due to deposit/withdrawal
                latest_pool['Growth'] = 0
                            
            latest_pool['Type'] = growth_type
            latest_pool['Offset'] = offset
            print"Saving pool_growth..."
            print "\tPrev: {0}".format(last_recorded_pool)
            print "\tNew: {0}".format(latest_pool)
            
            if target_date == None:
                self._saveToDB(DB_TBL_POOLGROWTH\
                          ,['Balance', 'Growth', 'Type', 'Offset']\
                          ,[latest_pool])
            else:
                latest_pool['DateTime'] = target_date
                self._saveToDB(DB_TBL_POOLGROWTH\
                          ,['Balance', 'Growth', 'Type', 'Offset', 'DateTime']\
                          ,[latest_pool])
                

        except:
            print traceback.print_exc()
        
        finally:
            print ""
            
    #@brief get the latest price per unit of a currency
    def getLatestPPU(self, market, price_type='Last'):
        try:
            while(1):
                ticker = self.get_ticker(market)
                
                if ticker['success'] == True:
                    if ticker['result'] is not None:
                        return Decimal(str(ticker['result'][price_type]))   

        except:
            print traceback.print_exc()
            print ticker
    
    def getLatestPoolFromAPI(self):
        balance_list = self.getPoolBalances(False)
        total_pool = Decimal('0')
        
        for balance in balance_list:
            balance['Balance'] = Decimal(str(balance['Balance']))
            if (balance['Currency'] == 'BTC'):
                total_pool += balance['Balance']
            else:
                if balance['Balance'] == Decimal('0'):
                    continue

                ppu = self.getLatestPPU('BTC' + '-' + balance['Currency'])
                total_pool += ppu*balance['Balance']               
                    
        return total_pool
    
    #@brief: get latest total pool size based on market_investments
    #    pool_size = sum of latest_balances (in BTC)
    def getLatestPoolFromDB(self, rectype='SUMMATION'):
        amount = {"pool_size": Decimal('0')}
        
        try:
            if rectype == 'SUMMATION':
                sql_query = "SELECT SUM(LatestBalance) as Balance from {table}"\
                    .format(table=DB_TBL_MARKET_INVESTMENTS)
            else:
                sql_query = "SELECT Balance from {table} ORDER BY DateTime DESC"\
                    .format(table=DB_TBL_POOLGROWTH)
            
            res = self.db.query(sql_query, single_fetch = True)
            
            amount['pool_size'] = res['Balance']
            if(amount['pool_size'] == None):
                amount['pool_size'] = Decimal('0')
            
        except:
            print traceback.print_exc()
            amount = None
        
        finally:
#             print amount
            return amount['pool_size']
    
    #@brief: get balances from all currency as a list
    def getPoolBalances(self, to_print=True):
        while 1:
            balances = self.get_balances()
            if balances['success'] == True:
                balances = [balance for balance in balances['result']]
                if to_print:
                    print "Balances:"
                    for bal in balances:
                        bal['Available'] = Decimal(str(bal['Available']))
                        bal['Balance'] = Decimal(str(bal['Balance']))
                        bal['Pending'] = Decimal(str(bal['Pending']))
                        if bal['Balance'] > Decimal('0'):
                            print bal
                break

                
        return balances
    
    #@brief: calculate total pool change for specific time
    def getPeriodicPoolChanges(self):
        #TODO: modify to allow calculation of total pool growth per time frame
        percent_change_per_interval = {}
        latest_pool =  self.getLatestPool()
        print "Latest Pool: {0}".format(latest_pool)
        try:

            sql_query = "select * from daily_pool ORDER BY "\
                "ABS(TIMESTAMPDIFF(hour, DateTime"\
                ", DATE_SUB(now(), INTERVAL %s {unit}) )) LIMIT 1"

            for key in INTERVAL_LIST:
                param = (INTERVAL_LIST[key]['amount'], )
                
                query = sql_query.format(unit=INTERVAL_LIST[key]['unit'])
                result = self.db.query(query, param=param, single_fetch=True)
                
                print "Pool {0}: {1}, {2}".format(key\
                    , result['Balance']\
                    , result['DateTime'].strftime("%Y-%m-%d %H:%M:%S"))
                percent_change_per_interval[key] \
                    = (latest_pool - result['Balance'])/result['Balance']
                #print result
            print "Pool Changes:"
            print percent_change_per_interval
            print ""
             
        except:
            traceback.print_exc()
    
    #@brief: save data to database
    def _saveToDB(self, table, column_list, data_dict_list):
        sql_query = "INSERT INTO {table} (".format(table=table)
        sql_query += ", ".join(column_list)
        sql_query += ") VALUES("
        param_placeholder = []
        
        for key in column_list:
            param_placeholder.append("%s")
    
        sql_query += ", ".join(param_placeholder) + ")"
        #print sql_query
        
        try:
            #print "Saving into {0}...".format(table)
            for data in data_dict_list:
                #print data
                values = []
                for col in column_list:
                    values.append(data[col])
                
                self.db.query(sql_query, param=values)
             
        except:
            traceback.print_exc()
            print values
            print sql_query
            
    #@brief: save/update market_investment details to database
    def _saveMarketInvestments(self, market_investment, to_print = True):
        if to_print:
            print "Saving market investment: ",
            print market_investment
        
        sql_query = "SET @temp_Market=%s, @temp_TotalUnits=%s, "\
                "@temp_RemainingInvestment=%s , @temp_LatestBalance=%s "\
                ", @temp_Profit=%s, @temp_Active=%s, @LastUpdate=%s "\
                ", @temp_PricePerUnit=%s "
        
        try:
            market_investment['LastUpdate'] = datetime.datetime.utcnow()
            values = [market_investment['Market'],\
                market_investment['TotalUnits'],\
                market_investment['RemainingInvestment'],\
                market_investment['LatestBalance'],\
                market_investment['Profit'],\
                market_investment['Active'],\
                market_investment['LastUpdate'],\
                market_investment['PricePerUnit']\
                ]
            
            self.db.query(sql_query, param=values)

            sql_query = "INSERT INTO {table_name} (Market, PricePerUnit "\
                    ", TotalUnits, RemainingInvestment "\
                    ", LatestBalance, Profit, Active, LastUpdate) "\
                    "VALUES (@temp_Market, @temp_PricePerunit, @temp_TotalUnits "\
                        ",@temp_RemainingInvestment, @temp_LatestBalance "\
                        ", @temp_Profit, @temp_Active, @temp_LastUpdate) "\
                    "ON DUPLICATE KEY UPDATE TotalUnits = @temp_TotalUnits "\
                        ", PricePerUnit = @temp_PricePerUnit "\
                        ", RemainingInvestment = @temp_RemainingInvestment "\
                        ", LatestBalance = @temp_LatestBalance "\
                        ", Profit = @temp_Profit, Active = @temp_Active "\
                        ", LastUpdate = @temp_LastUpdate"\
                    .format(table_name=DB_TBL_MARKET_INVESTMENTS)
            self.db.query(sql_query)
             
        except:
            print traceback.print_exc()
            
    #@brief: get market_investment detail for a specific market from database
    def _getMarketInvestment(self, market):        
        try:
            market_investment = None
            
            sql_query = "SELECT * from {0} where Active = True and market = %s"\
                .format(DB_TBL_MARKET_INVESTMENTS)
                
            market_investment = self.db.query(sql_query\
                , param=(market,), single_fetch=True)
            
            #if no active market_investments set all market_investments 
            #variables to be used later to 0
            if(market_investment == None):
                market_investment = {}
                market_investment['Market'] = market
                market_investment['PricePerUnit'] = Decimal('0')
                market_investment['TotalUnits'] = Decimal('0')
                market_investment['RemainingInvestment'] = Decimal('0')
                market_investment['LatestBalance'] = Decimal('0')
                market_investment['Profit'] = Decimal('0')
                market_investment['Active'] = False
                market_investment['LastUpdate'] = datetime.datetime.utcnow()
            
        except:
            traceback.print_exc()
            
        finally:
            return market_investment
    
    #@brief: calculate profit, remaining units, latest balance based on order details
    def _processOrder(self, order, market_investment):        
        market_investment['LatestPpu'] = order['PricePerUnit']
        order['ActualQuantity'] = Decimal(str(order['ActualQuantity']))
        #buy order
        print                                    
        if (order['OrderType'].find('BUY') >= 0):
            q_available = market_investment['TotalUnits']\
            + order['ActualQuantity']
            market_investment['RemainingInvestment']\
                 += order['Price']
            
        #sell order
        elif (order['OrderType'].find('SELL') >= 0):
            q_available = market_investment['TotalUnits']\
                 - order['ActualQuantity']
            try:
                #calculate remaining investment
                market_investment['RemainingInvestment']\
                    *= q_available\
                    /(market_investment['TotalUnits'])

            except ZeroDivisionError:
                market_investment['TotalUnits'] = Decimal('0')
            
        #get new total units remaining for the currency
        market_investment['TotalUnits'] = q_available
        
        #get latest balance in the currency based on order's ppu
        market_investment['LatestBalance'] \
            = market_investment['TotalUnits'] \
            * order['PricePerUnit']
        
        #calculate profit/loss
        if(market_investment['TotalUnits'] > Decimal('0')):
            market_investment['Profit'] =\
                (market_investment['LatestBalance']\
                 - market_investment['RemainingInvestment'])\
                /(market_investment['RemainingInvestment'])

            #update oder to indicate Profit from that specific order
            order['Profit'] = market_investment['Profit']
            market_investment['Active'] = True
        else:
            #all investments are sold
            market_investment['Profit'] = Decimal('0')
            market_investment['TotalUnits'] = Decimal('0')
            market_investment['Active'] = False
            market_investment['Remaininginvestmet'] = Decimal('0')
            market_investment['LatestBalance'] = Decimal('0')
            order['Active'] = False
        
        self.logAction(order['OrderType'], '_processOrder'\
            , "Pool Order: {0}"\
                    .format(market_investment['Market'])\
            , "BTCProceed: {1}, Latest Market Investment: {0}"\
                .format(order['Price']\
                    , market_investment['LatestBalance'])\
            , order['DateTime'])      
        return order, market_investment
    
    #@brief: get all order made on a specific currency
    def _getOrderListApi(self, market):
        order_list = self.get_order_history(market)
        if order_list['success'] == True:
            order_list = [order for order in order_list['result']]
            for i, order in enumerate(order_list):
#                 if order['Exchange'] == 'BTC-LTC':
#                     print "!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!"
#                     raise KeyboardInterrupt
                try:
                    order_list[i]['DateTime'] \
                        = datetime.datetime\
                        .strptime(order['Closed'], "%Y-%m-%dT%H:%M:%S.%f")
                except ValueError:
                    order_list[i]['DateTime'] \
                        = datetime.datetime\
                        .strptime(order['Closed'], "%Y-%m-%dT%H:%M:%S")
            order_list = sorted(order_list, key=lambda k: k['Closed'])
        else:
            order_list = []
            
        return order_list
    
    def _getActiveOrders(self):
        sql_query = "SELECT * FROM pool_trade_history where Active = 1 "\
                    "ORDER BY DateTime ASC"
        orders = None
        try:
            orders = self.db.query(sql_query)
            
        except:
            print traceback.print_exc()
            
        finally:
            return orders
        
    def _getUnprocessedOrders(self):
        sql_query = "SELECT * FROM pool_trade_history where InPool = 0 "\
                    "ORDER BY DateTime ASC"
        orders = None
        try:
            orders = self.db.query(sql_query)
            
        except:
            print traceback.print_exc()
            
        finally:
            return orders
            
    #@brief: update marke_investment details based on latest currency value
    def _updateTickerProfit(self, balance):
        market = 'BTC' + '-' + balance['Currency']
        #get market details
        market_investment = self._getMarketInvestment(market)
        
        market_investment['TotalUnits'] = balance['Balance']

        if market_investment['TotalUnits'] == Decimal('0'):
                market_investment['Profit'] = Decimal('0')
                market_investment['Active'] = False
                market_investment['Remaininginvestmet'] = Decimal('0')
                market_investment['LatestBalance'] = Decimal('0')
                market_investment['PricePerUnit'] = Decimal('0')
                self._saveMarketInvestments(market_investment, to_print=False)
        else:
            print "Updating {0} Ticker Profit...".format(market)
            #get lastest currency tick
            ppu = self.getLatestPPU(market)
                  
            #get latest balance value based on current tick
            market_investment['LatestBalance'] \
                = ppu*market_investment['TotalUnits']
             
            try:   
                #calculate new profit value based on latest ticker
                market_investment['Profit'] =\
                    (market_investment['LatestBalance']\
                     - market_investment['RemainingInvestment'])\
                    /(market_investment['RemainingInvestment'])
            except ZeroDivisionError:
                market_investment['Profit']
#                     print (market_investment['Profit'])
#                     print (market_investment['LatestBalance'])
#                     print (market_investment['RemainingInvestment'])
                
            market_investment['PricePerUnit'] = ppu

            print "\t",
            self._saveMarketInvestments(market_investment)

    def fetchPoolOrders(self):
        print "########## Updating Pool Orders ##########"
        #get latest investment details

        try:
            #market_investment = self._getMarketInvestment(market)
            
            #get orderhistory from bittrexapi
            order_list = self._getOrderListApi(None)
            
            sql_query = "SELECT count(*) as rec_found from {0} "\
                " where OrderUuid = %s".format(DB_TBL_TRADEHISTORY)
                
            for order in order_list:    #For each ORDER (starting from oldest)
                result = self.db.query(sql_query\
                    , param=(order['OrderUuid'],), single_fetch=True)
                
                if (result['rec_found'] != 0):
                    #if order is already there then skip the rest of the process and proceed to next
                    #print "OrderUuid \"{0}\" already processed, skip..."\
                    #   .format(order['OrderUuid'])
                    continue
                else:
                    print "Saving {0} Order..."\
                        .format(order['Exchange']\
                                ,order['OrderUuid'])
                print order
                order['PPULimit'] = order['Limit']
                order['ActualQuantity']\
                    = order['Quantity'] - order['QuantityRemaining']
                    
                self._saveToDB(DB_TBL_TRADEHISTORY\
                    , ['OrderUuid', 'Exchange', 'Price', 'Quantity'\
                       ,'ActualQuantity', 'QuantityRemaining', 'PricePerUnit'\
                       ,'OrderType', 'DateTime', 'Commission', 'PPULimit']\
                    , [order])
            
        except:
            traceback.print_exc()
            
        finally:
            print "\n"
    
    #@brief: update market_investment details based on changes caused by an order
    def processPoolOrders(self):
        print "########## Processing Pool Orders ##########"
        #get latest investment details
        try:            
            #get orderhistory from db
            order_list = self._getUnprocessedOrders()
                
            for order in order_list:    #For each ORDER (starting from oldest)
                market_investment = self._getMarketInvestment(order['Exchange'])
                order, market_investment \
                    = self._processOrder(order, market_investment)
                #print order
                sql_query = "UPDATE {table} "\
                            "SET InPool = 1 "\
                            "WHERE OrderUuid = %s "\
                            .format(table=DB_TBL_TRADEHISTORY)

                self.db.query(sql_query, param=(order['OrderUuid'], ))
                
                if order['Active'] == 0:
                    sql_query = "UPDATE {table} "\
                                "SET Active = 0 "\
                                "WHERE Exchange = %s "\
                                "AND DateTime <= %s"\
                                .format(table=DB_TBL_TRADEHISTORY)

                    self.db.query(sql_query\
                        , param=(order['Exchange'], order['DateTime']))
                                    
                self._saveMarketInvestments(market_investment)
            
        except:
            traceback.print_exc()
            
        finally:
            print "\n"
            
    def processPoolTransactions(self):
        print "########## Processing POOL Withdraws/Deposits ##########"        
        try:    
            status = False
            #get deposits from api
            while (1):
                transaction_list = self.get_deposit_history()
                if(transaction_list['success'] == True):
                    break
            #set deposit as type
            transaction_list = [t for t in transaction_list['result']]
            for transact in transaction_list:
                transact['Type'] = 'Deposit'
                transact['DateTime'] = transact['LastUpdated']
                transact['Amount'] = Decimal(str(transact['Amount']))
    
            #get withdrawals from api
            withdraw_list = self.get_withdrawal_history()
            if(withdraw_list['success'] == True):
                withdraw_list = [t for t in withdraw_list['result']]
                for transact in withdraw_list:
                    transact['Type'] = 'Withdrawal'
                    transact['DateTime'] = transact['Opened']
                    transaction_list.append(transact)
            else:
                withdraw_list = None
            
            #sort by date time ascending   
            transaction_list = sorted(transaction_list\
                                      , key=lambda k: k['DateTime'])
            #process
            self._processTransactionList(transaction_list)

        except:
            print traceback.print_exc()
            
        finally:
            print "\n"
            return status
    
    def _processTransactionList(self, transaction_list):
        sql_query = "SELECT count(*) as rec_found from {table} "\
            " where TxId = %s"\
            .format(table=DB_TBL_POOL_TRANSACTION)
        status = True
        try:    
            for transaction in transaction_list:
                
                txtype = transaction['Type']
                res = self.db.query(sql_query\
                    , param=(transaction['TxId'],)\
                    , single_fetch=True)
                if(res['rec_found'] != 0):
                    #transaction already processed
#                     print "Transaction \"{0}\" already processed, skip..."\
#                         .format(transaction['TxId'])
#                     print "\t",
#                     print transaction
                    continue
                else:
                    print "D: {0}, A: {1}\n\t{2}".format(transaction['DateTime'], transaction['Amount'], transaction['TxId'])
                    print "Processing {0} Transaction: {1}...\n\t"\
                        .format(transaction['Currency']\
                                ,transaction),
                    #transaction['Currency'] = 'BTC'
                    if(transaction['Currency'] == 'BTC'):
                        market_investment = \
                            self._getMarketInvestment('BTC')
                        self._processBTCTransaction(txtype\
                                                ,transaction \
                                                ,market_investment)
                        print market_investment
                    else:
                        market_investment = \
                            self._getMarketInvestment(\
                                'BTC-' + transaction['Currency'])    
                        market_investment = \
                            self._processTransaction(txtype, transaction, market_investment)
                        
                        if(market_investment == None):
                            status = False
                    #Amount in transaction is actually quantity
                    print transaction
                    transaction['Quantity'] = transaction['Amount']
                    transaction['TxType'] = txtype
                    if txtype == 'Deposit':
                        transaction['PaymentUuid'] = None
                                            
                    self._saveToDB(DB_TBL_POOL_TRANSACTION\
                        , ['TxId', 'Currency', 'Quantity'\
                            , 'TxType', 'PaymentUuid','DateTime']\
                        , [transaction])
                    self.updatePoolGrowth(txtype\
                                          , target_date=transaction['DateTime'])
                    
        except:
            traceback.print_exc()
            
        finally:
            return status
    
    #@brief: exclusive for BTC only because other currency have different way of calculation
    def _processBTCTransaction(self, txtype, transaction, market_investment):
        transaction['Amount'] = Decimal(str(transaction['Amount']))
        if(txtype == 'Deposit'):
            market_investment['TotalUnits'] += transaction['Amount']
        elif(txtype == 'Withdrawal'):
            market_investment['TotalUnits'] -= transaction['Amount']
        else:
            raise TypeError
        
        market_investment['TotalUnits'] = market_investment['TotalUnits']
        market_investment['PricePerUnit'] = Decimal('1')
        market_investment['Profit'] = None
        market_investment['Active'] = True
        market_investment['RemainingInvestment'] = None
        market_investment['LatestBalance'] = market_investment['TotalUnits']
        self._saveMarketInvestments(market_investment)
        
        self.logAction(txtype, '_processBTCTransaction'\
            , "BTC Pool Transaction"\
            , "Amount: {0}, NewBalance: {1}"\
                .format(transaction['Amount'], market_investment['LatestBalance'])\
            , transaction['DateTime'])
     
    #brief: process transaction except BTC
    def _processTransaction(self, transact_type, transaction, market_investment):
        try:
            #incase the market is not yet in DB, this section will set the defaults
            market_investment['Active'] = True
            if(transaction['Currency'] == 'BTC'):
                market_investment['PricePerUnit'] = Decimal('1')
            else:
                #get priceperunit by the time the order was processed
                transaction_date =  datetime.datetime\
                            .strptime(transaction['LastUpdated']\
                                , "%Y-%m-%dT%H:%M:%S.%f")
                market_investment['PricePerUnit']\
                    = self._getPPUAtTime(market_investment['Market']\
                        , transaction_date)
            if(market_investment['PricePerUnit'] != None):
                #process the values depending on transaction 'type'
                order = {}
                order['DateTime'] = transaction_date
                order['Price'] \
                    = transaction['Amount'] * market_investment['PricePerUnit']
                order['PricePerUnit'] = market_investment['PricePerUnit']
                order['Quantity'] = order['ActualQuantity'] = transaction['Amount']
                
                if(transact_type == 'Withdrawal'):
                    #market_investment['TotalUnits'] -= transaction['Amount']
                    order['OrderType'] = 'SELL'
                elif (transact_type == 'Deposit'):
                    #market_investment['TotalUnits'] += transaction['Amount']
                    order['OrderType'] = 'BUY'
                else:
                    raise TypeError
                
                order, market_investment = self._processOrder(order, market_investment)
                self._saveMarketInvestments(market_investment)
            else:
                market_investment = None
                    
        except:
            print traceback.print_exc()
        
        finally:
            return market_investment
        
    def _getPPUAtTime(self, market, target_date):
        try:
            bittrex_v2 = BittrexPool(API_KEY, API_SECRET, api_version=API_V2_0)
            ticks = bittrex_v2.get_candles(market, 'hour')
            ticks = [tick for tick in ticks['result']]
            for i, tick in enumerate(ticks):
                ticks[i]['T'] \
                    = datetime.datetime\
                    .strptime(tick['T'], "%Y-%m-%dT%H:%M:%S")
                    
            closest_tick = min(ticks, key=lambda x: abs(x['T'] - target_date))
            print closest_tick 
            return Decimal(str(closest_tick['C']))
        except:
            return None
 
    def getMarketDistribution(self, include_btc=True):
        if include_btc == True:
            sql_query = "SELECT Market, ROUND(LatestBalance/"\
                "(SELECT SUM(LatestBalance) "\
                    "FROM pool_market_investments), 8) as Percent "\
                "FROM pool_market_investments WHERE LatestBalance>0"
        else:
            sql_query = "SELECT Market, ROUND(LatestBalance/"\
                    "(SELECT SUM(LatestBalance) "\
                    "FROM pool_market_investments "\
                    "WHERE Market != 'BTC'), 8) "\
                "as Percent "\
                "FROM pool_market_investments "\
                "WHERE LatestBalance>0 and Market != 'BTC'"
        
        try:
            market_list = list(self.db.query(sql_query))
                
            if include_btc == False:
                sql_query = "SELECT Market, LatestBalance "\
                    "FROM pool_market_investments "\
                    "WHERE Market='BTC'"
            
                res = self.db.query(sql_query, single_fetch=True)
                market_list.append(res)

        except:
            print traceback.print_exc()
            market_list = []
            
        finally:
            return market_list
        
    def logAction(self, logcode, function_name, log_desc, log_det
                  , log_date=datetime.datetime.utcnow(), user_id=None):
        sql_query = "INSERT INTO process_logs(UserID, LogCode, FunctionName \
            , Description, Details, DateTime) VALUES (%s, %s, %s, %s, %s, %s)"
        
        try:
            self.db.query(sql_query\
                , param=(user_id, logcode, function_name, log_desc, log_det, log_date))         
        
        except:
            print traceback.print_exc()
            
 
if __name__ == "__main__":
    poolTracker = BittrexPool(API_KEY, API_SECRET, api_version="v1.1")
    #poolTracker.processPoolTransactions()
    #poolTracker.processPoolOrders()
    #poolTracker.updateMarketProfits()
#     poolTracker._getMarketDistribution()
    poolTracker.updatePoolGrowth("Tick")
    
    #bittrex_v1.getPeriodicPoolChanges()
    #bittrex_v1.getPoolBalances()
    
    ################################TEST#######################################
    #balances =  my_bittrex.get_markets()
    #balances =  my_bittrex.get_deposit_history()
    #bittrex_v2 = BittrexPool(API_KEY, API_SECRET, api_version=API_V2_0)
    #balances = bittrex_v1.getPeriodicPoolChanges()
    #balances = bittrex_v1.getOrderPoolChange()
    #balances = bittrex_v1.get_market_history('BTC-LTC')
    #balances = poolTracker.get_order_history()
    #print len(balances['result'])
#     market_test = 'BTC-BCC'
#     ticks = bittrex_v2.get_candles(market_test, 'hour')
#     ticks = [tick for tick in ticks['result']]
#     for i, tick in enumerate(ticks):
#         ticks[i]['T'] \
#             = datetime.datetime\
#             .strptime(tick['T'], "%Y-%m-%dT%H:%M:%S")
#     
#     datetest = datetime.datetime.utcnow().replace(hour=1, day = 6, month = 10)
#     print "START"
#     #ticks = sorted(ticks, key=lambda k: rdelta.relativedelta(datetest, k['T']))
#     for tick in ticks:
#         print tick
#     #for x in balances['result']:
#     #    print x
#     print poolTracker.getLatestPPU(market_test)
#     print min(ticks, key=lambda x: abs(x['T'] - datetest))
#     #bittrex_v1.getLatestPool()
    
