#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jun 17 13:34:16 2024

@author: mclovin
"""

api_key = 'oy85tua1dxxc60en'
api_secret = 'cc704wqcx0a0a77w916lsp0kt3yy4yc6'

import pandas as pd
import streamlit as st
curve = pd.read_excel('jash.xlsx')
import warnings
import numpy as np
warnings.filterwarnings('ignore')
import altair as alt


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

pnl_df['Trade Date'] = pnl_df['Trade Date'].dt.date
pnl_df = pnl_df.drop(['Symbol', 'PNL','RealisedPNL','Cumulative PNL'], axis=1)

pnl_df['Trade Date'] = pd.to_datetime(pnl_df['Trade Date'])
pnl_df.set_index('Trade Date', inplace=True)

pnl_df = pnl_df.resample('D').last()
pnl_df.dropna(inplace=True)
pnl_df.reset_index(inplace=True)

# OPP ASSET 

close_values = [
    42700.949, 43017.199, 43318.25, 43619.398, 43737.898, 43658.648, 43683.602, 
    43820.102, 43996.65, 43891.25, 44201.699, 44161.551, 43583.949, 43584.949, 
    43689.148, 43449.602, 43577.5, 43769.102, 44566.449, 44481.75, 
    44814.199, 46431.398, 47012.25, 46834.551, 46841.398, 47262, 47314.25, 
    47097.551, 47092.25, 47732.301, 48143.551, 47867.699, 47870.898, 47445.301, 
    47840.148, 47491.852, 47724.852, 48282.199, 48508.551, 48292.25, 48234.301, 
    47761.648, 47704.949, 48195.852, 48159, 47450.25, 47242.648,  
    47438.352, 47709.801, 48158.301, 48125.102, 46064.449, 45713.551, 45701.148, 
    46058.2, 45015.051, 45082.398, 44866.148, 45442.352, 45367.75, 45996.801, 
    46188.648, 45970.949, 45825.551, 45818.5, 45012, 45634.551, 
    44882.25, 45502.398, 45908.301, 46218.898, 46384.852, 46535.5, 47094.199, 
    47019.699, 46919.801, 46811.75, 46576.5, 46588.051, 45963.148, 46120.898, 
    47286.898, 47286.898, 47456.102, 47581, 47835.801, 47327.852, 
    47282.398, 46981.301, 46789.949, 46594.102, 46575.898, 46384.801, 46310.898, 
    46684.898, 46863.75, 46600.199, 46785.949, 47124.602, 47578.25, 47545.449, 
    47624.25, 48060.801, 48493.051, 48581.699, 48730.551, 48986.602, 48564.551, 
    47773.25, 47484.801, 47069.449, 47574.148, 47924.898, 48189, 
    48494.949, 48201.051, 49424.051, 49396.75, 49231.051, 48923.551, 48895.301, 
    48285.352, 48021.102, 47487.898, 47421.102, 47754.102, 47859.449, 47687.449, 
    47977.051, 48115.648, 48199.5,  47781.949, 48768.602, 48971.648, 
    49281.801, 49142.148, 48501.352, 48682.352, 48983.949
]

# Creating a DataFrame from the given values
opp = pd.DataFrame({'close': close_values})

pnl_df.set_index(pnl_df['Trade Date'],inplace=True)
pnl_df.index = pd.to_datetime(pnl_df.index, format='%d-%m-%Y')

# # Dates to be removed
# dates_to_remove = pd.to_datetime(["02-11-2023", "03-11-2023", "06-11-2023", "08-12-2023", "05-01-2024", "06-02-2024", "02-04-2024", "05-04-2024"], format='%d-%m-%Y')

# # Removing the specified rows
# pnl_df = pnl_df.drop(dates_to_remove)

pnl_df.drop(columns=['Trade Date'],inplace=True)
pnl_df['close'] = opp['close'].values

pnl_df['Pos'] = 0
pnl_df['long'] = np.where(pnl_df['close']>0,1,pnl_df['Pos'])
pnl_df['Pos'] = np.where(pnl_df['long']==1,1,pnl_df['Pos'])
pnl_df['returns'] = pnl_df['close'].pct_change()*pnl_df['Pos'].shift(1)
pnl_df['Strategy1'] = (pnl_df['returns'].cumsum()) + 1
pnl_df['bnf'] = (pnl_df['Strategy1'] - 1) * 100

# pnl_df[['Equity Multiple','bnf']].plot()
# # Create the equity curve
# st.title("Equity Curve")

# # Simple line chart using Streamlit
# st.line_chart(pnl_df['Equity Multiple'])

# Set the title
# st.title("Orion vs BankNifty")
# zoom = alt.selection_interval(bind='scales')

# # Plot with Altair
# chart = alt.Chart(pnl_df).mark_line(color='purple').encode(
#     x=alt.X('Trade Date:T', title='Trade Date', axis=alt.Axis(format='%Y-%m-%d')),
#     y=alt.Y('Equity Multiple:Q', title='Equity Multiple')
# ).properties(
#     title='Equity Curve'
# ).add_selection(
#     zoom
# )

pnl_df.reset_index(inplace=True)

if not pnl_df.empty and 'Trade Date' in pnl_df.columns and 'Equity Multiple' in pnl_df.columns and 'bnf' in pnl_df.columns:
    st.markdown("<h1 style='color: purple;'>ORION <span style='color: white;'>vs BankNifty</span></h1>", unsafe_allow_html=True)
    
    zoom = alt.selection_interval(bind='scales')

    # Create the base chart
    base = alt.Chart(pnl_df).encode(
        x=alt.X('Trade Date:T', title='Track record', axis=alt.Axis(format='%Y-%m-%d')),
        y=alt.Y('Equity Multiple:Q', title='Returns (%)')
    )

    # Create the line for Equity Multiple
    equity_line = base.mark_line(color='purple').encode(
        y='Equity Multiple:Q'
    )

    # Create the line for BankNifty
    bnf_line = base.mark_line(color='white').encode(
        y='bnf:Q'
    )

    # Combine both lines in a layered chart
    chart = alt.layer(
        equity_line,
        bnf_line
    ).properties(
        title="ORION vs BankNifty"
    ).configure_axis(
        grid=False  # Remove grid lines
    ).add_selection(
        zoom
    )

    # Display the plot in Streamlit
    st.altair_chart(chart, use_container_width=True)
else:
    st.write("The DataFrame is empty or does not contain the required columns.")

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


