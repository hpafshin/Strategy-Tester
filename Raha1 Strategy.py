# Importing required libraries
import pandas as pd
import numpy as np
import pathlib
from statistics import mean

# Defining indicators functions    
def williams_aligator (jaw, teeth, lip):
    df ['mean'] = (df['High'] + df ['Low'])/2
    def SMMA (period):
        for i in range (len (df)):
            if i >= period:
                df [f'smma{period}'] = df.rolling (window= period) ['mean']. mean ()
        for i in range (period, len (df)):
            df.loc[i,f'smma{period}'] = (df.loc[i-1,f'smma{period}']*(period-1) + df.loc[i,'mean'])/period
        return df
    SMMA (jaw)
    SMMA (teeth)
    SMMA (lip)
    df ['jaw'] = df [f'smma{jaw}'] .shift (8)
    df ['teeth'] = df [f'smma{teeth}'] .shift (5)
    df ['lip'] = df [f'smma{lip}'] .shift (3)
    return df    
def macd (fast, slow, signal):
    exp1 = df.ewm (span= fast, adjust=False) ['Close'].mean ()
    exp2 = df.ewm (span= slow, adjust=False) ['Close'].mean ()
    macd = exp1 - exp2
    df ['MACD'] = macd
    sig = df.ewm (span= signal , adjust=False) ['MACD'].mean ()
    df ['Signal'] = sig
    histogram = macd - sig
    df ['Histogram'] = histogram
    return df
final_list =[]

# Reading every file in a folder with at least 30 records
path = pathlib.Path('e:/TSE Data/LatinSymbol')
for file in path.iterdir():
    deposit_state = 0
    number_of_transactions = 0
    money = 10000000
    shares = 0
    win = 0
    rewardtorisk = []
    df = pd.read_csv (file)
    if len(df)<30:
        pass
    else:    
        df = williams_aligator (13, 8, 5)
        df = macd (12,26,9)
    # Generating Strategy with buy and sell signals
        for i in range (20,len(df)-1):
            if df.loc [i,'MACD']>0 and df.loc [i,'MACD']>df.loc [i,'Signal'] and df.loc [i,'lip']>df.loc [i,'teeth'] and df.loc [i,'teeth']>df.loc [i,'jaw'] and deposit_state == 0:
                BuyPrice = df.loc[i,'Close']
                deposit_state = 1
                shares = int(money / BuyPrice)
                money -= shares * BuyPrice
            elif (df.loc [i,'MACD']<df.loc [i,'Signal'] and (df.loc [i,'lip']<df.loc [i,'teeth'] or df.loc [i,'teeth']<df.loc [i,'jaw'])) and deposit_state == 1:
                SellPrice = df.loc[i,'Close']
                number_of_transactions += 1
                deposit_state = 0
                money += shares * SellPrice
                shares = 0
                rewardtorisk.append (SellPrice/BuyPrice)
                if SellPrice > BuyPrice:
                    win += 1
        if number_of_transactions > 0:
            money += shares * df.loc[i,'Close']
            win_rate = win / number_of_transactions
            strategy_efficiency = money/10000000
            reward = list(filter (lambda x : x>1, rewardtorisk))
            risk = list(filter (lambda x : x<1, rewardtorisk))
            r2r = (1-mean(reward))/(mean(risk)-1) if len(reward) > 0 and len(risk) >0 else 0
            temp_list = [df.loc[1,'Symbol'], strategy_efficiency, number_of_transactions, win_rate, len(df), r2r]
            final_list.append (temp_list)
# Exporting result to an excel file
data_frame = pd.DataFrame (final_list, columns=['Symbol','Efficeincy','TransactionCount','winRate', 'DaysCount','Reward2Risk'])
data_frame.to_excel ('Raha1Backtest.xlsx',sheet_name='Parameters')
