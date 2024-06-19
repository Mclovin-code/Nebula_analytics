#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jun 17 13:34:16 2024

@author: mclovin
"""

api_key = 'oy85tua1dxxc60en'
api_secret = 'cc704wqcx0a0a77w916lsp0kt3yy4yc6'

import pandas as pd
import numpy as np
import streamlit as st
curve = pd.read_excel('jash.xlsx')
import warnings
warnings.filterwarnings('ignore')

pnl = []

for k in curve['Symbol'].unique():
    
    df = curve[curve['Symbol']==k]
    df['new_qty'] = np.where(df['Trade Type']=='sell',-df['Quantity'],df['Quantity'])
    df['qty_cumsum'] = df['new_qty'].cumsum()
    df['sign'] = 0
    df['sign'] = np.where((df['qty_cumsum']==0),1,df['sign'])
    empty_dfs = []
    
    a = 0
    for n in range(len(df)):
        if df['sign'].iloc[n]==1:
            empty_dfs.append(df.iloc[a:n+1])
            a = n+1        
        # print(a,n)
    
    for dfs in empty_dfs:
        
        sells_df = dfs[dfs['Trade Type'] == 'sell']
        buys_df = dfs[dfs['Trade Type'] == 'buy']
        
        sell_turnover = (sells_df['Price']*sells_df['Quantity']).sum()
        buy_turnover = (buys_df['Price']*buys_df['Quantity']).sum()

        exe_date = pd.to_datetime(buys_df['Order Execution Time'].iloc[-1])
        
        pnl.append([k,exe_date,(sell_turnover - buy_turnover)])
    
pnl_df = pd.DataFrame(pnl)
pnl_df.rename(columns={0: 'Symbol', 1: 'Trade Date',2:'PNL'}, inplace=True)
# pnl_df = pnl_df.set_index('Trade Date')

pnl_df['RealisedPNL'] = pnl_df['PNL'].sum()
pnl_df['Cumulative PNL'] = pnl_df['PNL'].cumsum()

initial_margin = 2374716.79
pnl_df['Daily Equity'] = initial_margin + pnl_df['Cumulative PNL']
pnl_df['Equity Multiple'] = pnl_df['Daily Equity'] / initial_margin
pnl_df['Strategy'] = pnl_df['Daily Equity'] / initial_margin
pnl_df['Equity Multiple'] = (pnl_df['Daily Equity'] / initial_margin - 1) * 100

# Create the equity curve
st.title("Equity Curve")

# Simple line chart using Streamlit
st.line_chart(pnl_df['Equity Multiple'])

# def max_drawdown(df):
#     """
#     Calculate the maximum drawdown of a trading strategy.
    
#     Parameters:
#     - df: DataFrame containing the trading strategy returns. Assumes there's a column named 'Strategy'
#           that represents the cumulative returns of the strategy.
    
#     Returns:
#     - The maximum drawdown, expressed as a percentage, rounded to two decimal places.
#     """
#     DF = df.copy()
    
#     # Assuming 'Strategy' column represents cumulative returns
#     DF["cum_return"] = DF['Equity Multiple']
#     DF["cum_roll_max"] = DF["cum_return"].cummax()  # Max value to date for each row
#     DF["drawdown"] = DF["cum_roll_max"] - DF["cum_return"]  # Current drawdown
#     DF["drawdown_pct"] = DF["drawdown"] / DF["cum_roll_max"]  # Drawdown percentage
#     max_dd = DF["drawdown_pct"].max()  # Max drawdown percentage
    
#     return round(max_dd * 100, 2) 

# max_drawdown(pnl_df)

# def volatility(df):
#     """
#     Function to calculate the annualized volatility of a trading strategy
#     based on daily returns of 'BNF Close' prices.
#     """
#     DF = df.copy()
    
#     # Calculate daily returns as the percentage change, then convert to log returns
#     DF['Daily Returns'] = DF['Equity Multiple'].pct_change().apply(lambda x: np.log(1+x))
    
#     # Calculate the standard deviation of daily returns
#     daily_volatility = DF['Daily Returns'].std()
    
#     # Annualize the volatility
#     # Using 252 as the typical number of trading days in a year
#     annualized_volatility = daily_volatility * np.sqrt(252)
    
#     return round(annualized_volatility * 100,2) 

# volatility(pnl_df)

# def calculate_CAGR(df):
#     """
#     Function to calculate the Cumulative Annual Growth Rate (CAGR) of a trading strategy.
    
#     Parameters:
#     - df: A pandas DataFrame containing the strategy's return data.
    
#     Returns:
#     - The CAGR of the strategy, expressed as a percentage.
#     """
#     # Ensure df is a DataFrame
#     if not isinstance(df, pd.DataFrame):
#         df = pd.DataFrame(df)
    
#     # Calculate cumulative product to simulate compounding returns
#     cumprod_returns = df['Equity Multiple']
    
#     # Calculate the number of years the strategy has been running
#     n_years = len(cumprod_returns) / 252
    
#     # Calculate CAGR
#     CAGR = (cumprod_returns.iloc[-1])**(1/n_years) - 1
    
#     return round(CAGR * 100,2)

# calculate_CAGR(pnl_df)

# def sharpe_ratio(df, rf=0.02):
#     """
#     Calculate the Sharpe Ratio for a trading strategy.
    
#     Parameters:
#     - df: DataFrame containing the trading strategy data.
#     - rf: The risk-free rate. Defaults to 0.02 (or 2%).
    
#     Returns:
#     - The Sharpe Ratio of the strategy.
#     """
#     # Calculate the annualized return (CAGR) of the strategy
#     annualized_return = calculate_CAGR(df) - rf
    
#     # Calculate the annualized volatility (standard deviation) of the strategy
#     annualized_volatility = volatility(df)
    
#     # Calculate the Sharpe Ratio
#     sharpe_ratio = annualized_return / annualized_volatility
    
#     return round(sharpe_ratio,2)

# sharpe_ratio(pnl_df)

# pnl_df['Equity Multiple'] = (pnl_df['Daily Equity'] / initial_margin - 1) * 100


