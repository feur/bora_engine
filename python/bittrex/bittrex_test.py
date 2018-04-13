from bittrex.bittrex import *
import argparse
from statistics import mean



def GetPair():
    parser = argparse.ArgumentParser(description='Process TA for pair')
    parser.add_argument('-p', '--pair',
                    action='store',         # tell to store a value
                    dest='pair',        # use `paor` to access value
                    help='The Pair to be watched')
    parser.add_argument('-a', '--high1',
                    type=float,
                    action='store',   # tell to store a value
                    dest='a',        # use `a` to access value
                    help='fib zone 1')
    parser.add_argument('-b', '--low1',
                    type=float,
                    action='store',         # tell to store a value
                    dest='b',        # use `d` to access value
                    help='fib zone 1')
    parser.add_argument('-c', '--high2',
                    type=float,
                    action='store',         # tell to store a value
                    dest='c',        # use `b` to access value
                    help='fib zone 2')
    parser.add_argument('-d', '--low2',
                    type=float,
                    action='store',         # tell to store a value
                    dest='d',        # use `c` to access value
                    help='fib zone 2')                   
    parser.add_argument('-e', '--high3',
                    type=float,
                    action='store',         # tell to store a value
                    dest='e',        # use `e` to access value
                    help='fib zone 3')             
    parser.add_argument('-f', '--Low3',
                    type=float,
                    action='store',         # tell to store a value
                    dest='f',        # use `e` to access value
                    help='fib zone 3')    
    pair = parser.parse_args()
    return pair
    

def GetData(pair):
    """
    {u'C': 3.079e-05, u'H': 3.079e-05, u'L': 3.079e-05, u'O': 3.079e-05, u'BV': 0.04902765, u'T': u'2018-04-13T07:10:00', u'V': 1592.32422805}
    """
    
    account = Bittrex("f5d8f6b8b21c44548d2799044d3105f0", "b3845ea35176403bb530a31fd4481165", api_version=API_V2_0)
    data = account.get_candles(pair.pair,tick_interval=TICKINTERVAL_FIVEMIN)
    if(data['success'] == True):
            data = data['result']
    return data
    
    
def GetFramedData(data,window):
    data_window=[]    
    
    for i in range (len(data)-window,len(data)):
        data_window.append(data[i])
         
    return data_window
    
    
def GetFib(current, a, b, c, d, e,f):
    if current < e:
        high = e
        low = f
    elif current > e and current < c:
        high = c
        low = d
    elif current > c and current < a:
        high = a
        low = b
    else:
        fib = 1
        return fib
    
    fib = (current - low) / (high - low)
    return fib    
    
    
 
def GetTr(data):
    tr=[]

    for i in range(1,28):
        itemP = data[i-1]
        itemN = data[i]
        maximum = max(abs(itemN['H'] - itemN['L']), abs(itemN['H'] - itemN['C']), abs(itemN['L'] - itemP['C']))
        tr.append(maximum)
        
    print(tr)  
    return tr  
    
    
  
def GetTrMax(tr):
    trMax=[]
    
    dis = 14
    sum = 0
    
    for i in range (0, dis):
        sum += tr[i]
        
    trMax.append(sum)

    for i in range(1,dis):
        trMax.append(trMax[i-1] - (trMax[i-1]/14) + tr[i+dis])
        
        
    print(len(trMax))    
        
    return trMax  
       
    

def GetdmPos(data):
    dmPos=[]

    for i in range(1,28):
        itemP = data[i-1]
        itemN = data[i]
        
        if (itemN['H'] - itemP['H']) > (itemP['L'] - itemN['L']):
            dmPos.append(0)
        else:
            dmPos.append(max((itemN['H'] - itemP['H']), 0))
            
    print(dmPos)      
    return dmPos  
    
 
def GetdmNeg(data):
    dmNeg=[]

    for i in range(1,28):
        itemP = data[i-1]
        itemN = data[i]
        
        if (itemP['L'] - itemN['L']) > (itemN['H'] - itemN['H']):
            dmNeg.append(0)
        else:
            dmNeg.append(max((itemP['L'] - itemN['L']), 0))
            
    print(dmNeg)      
    return dmNeg
    

def GetdiPos(dmPos,dmNeg):
    """ +DI, positive directional moving index
        :param df: data
        :param windows: range
        :return:
        """
        
    trMax = sum(tr)
    diPos = 100 * (dmPos/trMax)        
        
    return diPos
 
 
def GetdiNeg(data):
    return diNeg
    
    
def GetDX(diPos, diNeg):
    diDiff = abs(diPos - diNeg)
    diSum  = diPos + diNeg 
    dx = 100 * (diDiff / diSum)
    return dx
    
    
def GetADX(dx):
    adx = mean(dx)
    return adx
    
def GetMomentum(data):
    
    current = data[-1]
    previous = data[-11]

    momentum = (current['C'] / previous['C'])  
    
    print momentum
    
    return momentum
    
    
    

def GetIchimokuAverage(data):
    
    #get list of high & low 
    high=[]
    low=[]
    
    for item in data:
        high.append(item['H'])
        low.append(item['L'])
    
    result = (mean(high) + mean(low)) / 2    
    return result   
    

def GetIchimokuSignal(data):
    
    tenkanSen = GetIchimokuAverage(GetFramedData(data,9))
    kijunSen = GetIchimokuAverage(GetFramedData(data,26))
    senkouA = (tenkanSen + kijunSen) / 2
    senkouB = GetIchimokuAverage(GetFramedData(data,52))
    
    print(tenkanSen)
    print(kijunSen)

    if tenkanSen == kijunSen :
        return 1
    else:
        return 0
        
    
    
    


def GetRating(fib,diPos,diNeg,dax,momentum):
    print("Di+ is %.9f" % diPos)
    print("Di- is %.9f" % diNeg)
    print("DAX is %.9f" % dax)
    print("Momentum is %.9f" % momentum)
    print("Fib is %.9f" % fib)
    rating = (1-fib) * (diPos + diNeg + (dax/40)) * momentum
    return rating


         

pair = GetPair()
data = GetData(pair)

current = data[-1]

#for item in data:
#    print(item["C"]);

#tr = GetTr(GetFramedData(data,28))
#dmPos = GetdmPos(GetFramedData(data,28))
#dmNeg = GetdmNeg(GetFramedData(data,28))
#trMax = GetTrMax(tr)

momentum = GetMomentum(data)
signal = GetIchimokuSignal(data)
print(signal)


fib = GetFib(current['C'], pair.a, pair.b, pair.c, pair.d, pair.e, pair.f)
print(GetRating(fib,31.2223,10.3730,50.8481,0.momentum)); 




 