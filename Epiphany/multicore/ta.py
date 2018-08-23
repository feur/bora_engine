
def GetFib(current, a, b, c, d, e,f):
    
    ##find High first
    if current < a and current > c:
        high = a
    elif current < c and current > e: 
        high = c
    elif current < e: 
        high = e
    elif current > a:
        high = a
        
    if high == a:
        low = b
    elif high == c:
        low = d
    elif high == e:
        low = f
        
        
    print("Fib is between %0.9f and %0.9f" % (high,low))
    
    fib = (current - low) / (high - low)
    return fib
    


def GetDX(diPos, diNeg):
    diDiff = abs(diPos - diNeg)
    diSum  = diPos + diNeg
    dx = 100 * (diDiff / diSum)
    return dx
    
def GetADX(dx):
    adx = mean(dx)
    return adx
    
def GetEMA(data, n, prevEMA):
    
    x = 0
    K = 2 / (float(n) + 1)
    
    if (prevEMA == 0):
        for i in range (0,n-1):
            x += data[i]
        
        prev = float(x/n) ##prev is SMA of period n
    else:
        prev = prevEMA
            
    EMA = float(data[-1] * K + prev * (1-K))
    
    return EMA   
    

    
def GetMomentum(data):
    current = data[-1]
    previous = data[-11]
    momentum = (current['C'] / previous['C'] * 100)
    return momentum
    
def GetIchimokuAverage(data):
    #get list of high & low#
    high=[]
    low=[]
    for item in data:
        high.append(item['H'])
        low.append(item['L'])

    result = (mean(high) + mean(low)) / 2
    return result

def GetFramedData(data,window):
        data_window=[]

        for i in range (len(data)-window,len(data)):
            data_window.append(data[i])

        return data_window


@offload
def BackTest(close, low, high, CRMI, Floor, rl, IchtPeriod, lp, sl):
    
    result = [0,0,0,0] #Profit, Wins, Lossess
    
    state = 0
    order = 0
    hold = 0
    initial = 0
    bought = 0
    loss = 0
    wins = 0
    profit = 0
    
    fee = 0.0055 ##0.55% fee 
    
    
    for i in range (len(close)-1-lp,len(close)-2):
        
        if (CRMI[i] <= Floor):
            state = 1
        else: 
            state = 0
            order = 0
                            
        if (hold == 0 and state == 1 and (order == 0 or order == 1)):
            buyPrice = close[i]
            bought += 1   
            order = 1
                        
                            
        elif (hold == 1 and (order == 0 or order == 2)):
            absolutemin = float(initial * (1+fee))      ##absolute minimum is to cover the fee
            minimum = float(close[i] * (rl + fee))    ##minium is just slighlty above the fee
            maximum = float(initial * rl)          ## maximum return limit

            position = float((close[i]) / initial)
                        
            if (position < 1 and minimum > absolutemin):
                sellPrice = minimum
            elif (position >= 1): ##current closing price at initial or above
                sellPrice = maximum
            elif position <= sl: ##stop loss
                sellPrice = close[i] 
            else:
                sellPrice = absolutemin
                
            order = 2
                                         
         
        if order == 1 and buyPrice >= low[i+1]: ## to make sure order is completed 
            buy = buyPrice
            hold = 1    
            order = 0
            initial = buy ##initial position
                    
                        
        if order == 2 and sellPrice <= high[i+1]:
            sell = sellPrice
            hold = 0 
            order = 0
            r = float(float(float(sell)/float(buy) - 1.005)*100)
                        
            if (r < 0):
                loss += 1
            elif (r > 0):
                wins += 1
                            
            profit = float(profit)+float(r)
                        
                            
                            
    if (hold == 1): ##take care of unifnihsed business
        sell = close[i]                           
                                    
        r = float(float(float(sell)/float(buy) - 1.005)*100)
        
        if (r < 0):
            loss += 1
        elif (r > 0):
            wins += 1
                            
        profit = float(profit)+float(r)
        
    result[0] = profit
    result[1] = wins
    result[2] = loss   
    result[3] = Floor
    return result 
    








