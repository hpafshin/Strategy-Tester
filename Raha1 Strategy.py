# Importing required libraries
import pandas as pd
import numpy as np
import pathlib

# Reading every file in a folder with at least 21 records
path = pathlib.Path('e:/TSE Data/LatinSymbol')
final_list =[]
for file in path.iterdir():
    df = pd.read_csv (file)
    if len(df)<21:
        pass
    else:
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
        df = williams_aligator (13, 8, 5)
        df = macd (12,26,9)
# Generating Strategy with buy and sell signals
        df['MACDsig'] = np.where ((np.logical_and(df['MACD']>0, df['MACD']>df['Signal'])), True, False)
        df['Gatorsig'] = np.where ((np.logical_and(df['lip']>df['teeth'], df['teeth']>df['jaw'])), True, False)
        df['Buy'] = np.where ((np.logical_and(df['MACDsig']==True, df['Gatorsig']==True)),'buy','-')
        df['Sell 1/2'] = np.where ((np.logical_and(df['MACD']<df['Signal'], df['Gatorsig']==False)),'sell 1/2','-')
        df['Sell All'] = np.where ((df['MACD']<0),'sell all', '-')

# Back testing the strategy
        deposit_state = 0
        number_of_transactions = 0
        money = 10000000
        shares = 0
        for i in range (len(df)-1):
            if df.loc [i,'Buy'] == 'buy' and deposit_state == 0:
                deposit_state = 1
                number_of_transactions += 1
                shares = int(money/df.loc[i+1,'Open'])
                money -= shares *df.loc[i+1,'Open']
            elif df.loc [i,'Sell All'] == 'sell all' and deposit_state != 0:
                deposit_state = 0
                money += shares * df.loc[i+1,'Open']
                shares = 0            
        money += shares * df.loc[i+1,'Open']
        strategy_efficiency = money/10000000
        temp_list = [df.loc[1,'Symbol'], strategy_efficiency, number_of_transactions]
        final_list.append (temp_list)
# Exporting result to a .csv file
data_frame = pd.DataFrame (final_list)
data_frame.to_csv ('Raha1_Sanat.csv', index=False)