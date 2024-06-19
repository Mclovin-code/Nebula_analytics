#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Nov  5 01:39:05 2022

@author: mclovin
"""

api_key = 'oy85tua1dxxc60en'
api_secret = 'cc704wqcx0a0a77w916lsp0kt3yy4yc6'

from kiteconnect import KiteConnect
from selenium import webdriver
import time
import pandas as pd
# import os
import onetimepass as otp
import datetime as dt
import threading 
import numpy as np
import warnings
import gspread
from oauth2client.service_account import ServiceAccountCredentials
warnings.filterwarnings('ignore')

class zerodha:
    
    global api_key,api_secret
    kite = KiteConnect(api_key=api_key)
    
    def __init__(self):
        print('zerodha class established')
        
        self.kite = KiteConnect(api_key=api_key)
    
    def autologin(self,user):
    
        # token_path = "api_key.txt"
        # key_secret = open(token_path,'r').read().split()
        kite = KiteConnect(api_key=api_key)
        service = webdriver.chrome.service.Service('./chromedriver')
        service.start()
        options = webdriver.ChromeOptions()
        # options.add_argument('--headless')
        options = options.to_capabilities()
        driver = webdriver.Remote(service.service_url, options)
        driver.get(kite.login_url())
        driver.implicitly_wait(5)
        username = driver.find_element('xpath','/html/body/div[1]/div/div[2]/div[1]/div/div/div[2]/form/div[1]/input')
        password = driver.find_element('xpath','/html/body/div[1]/div/div[2]/div[1]/div/div/div[2]/form/div[2]/input')
        if user == 1:
            username.send_keys('ZMX287')
            password.send_keys('Unifynd@123')
            otp_secret = 'AVKWQS46CBCUPM55TJCP4TCXQNIDG37W'
        if user == 2:
            username.send_keys('MR8369')
            password.send_keys('ZERODHAADMIN')
            otp_secret = 'XZISU7TMGIRMUL4ZBCVKDT5KIDXEVPDC'
        driver.find_element('xpath','/html/body/div[1]/div/div[2]/div[1]/div/div/div[2]/form/div[4]/button').click()
        pin = driver.find_element('xpath','/html/body/div[1]/div/div[2]/div[1]/div/div/div[2]/form/div[2]/input')
        
        while True:
            otp_number = otp.get_totp(otp_secret)
            if len(str(otp_number)) == 6:
                break
        
        pin.send_keys(otp_number)
        driver.find_element('xpath','/html/body/div[1]/div/div[2]/div[1]/div/div/div[2]/form/div[3]/button').click()
        time.sleep(5)
        
        request_token=driver.current_url.split('request_token=')[1][:32]
        driver.quit()
        kite = KiteConnect(api_key=api_key)
        data = kite.generate_session(request_token, api_secret=api_secret)
        access_token = data["access_token"]
        return access_token
    
    def save_file_autologin(self):
        
        request_token = open("request_token.txt",'r').read()
        # key_secret = open("api_key.txt",'r').read().split()
        kite = KiteConnect(api_key=api_key)
        data = kite.generate_session(request_token, api_secret=api_secret)

        with open('access_token.txt', 'w') as file:
                file.write(data["access_token"])

        access_token = open("access_token.txt",'r').read()
        kite.set_access_token(access_token)
        return kite

    def get_access(self,number):
            scope_app = ['https://spreadsheets.google.com/feeds','https://www.googleapis.com/auth/drive']
            #credentials to the account
            cred = ServiceAccountCredentials.from_json_keyfile_name(r'/home/ubuntu/nebula_dashboard/voltaic-plating-368011-199a54d3d82d.json',scope_app)
            # authorize the clientsheet
            client = gspread.authorize(cred)
            sh = client.open('access_token')
            worksheet = sh.sheet1
            if number ==  1:
                access_token = worksheet.cell(1,1).value
                self.kite.set_access_token(access_token)
                return access_token
            if number == 2: 
                access_token = worksheet.cell(2,1).value
                self.kite.set_access_token(access_token)
                return access_token
                
    def nse_dump(self,exchange):
        nse = self.kite.instruments(exchange) #replace 'NSE' with 'BSE' for BSE data
        nse_data = pd.DataFrame(nse)
        return nse_data
    
    def instrument_token(self,data, symbol):
        """
        This function will return the token number of the instrument from data
        """
        return data[data.tradingsymbol == symbol].instrument_token.values[0]
    
    # instrument_token(nse_data, 'NIFTY BANK')
    
    def historical_data(self, symbol, from_date, to_date, interval, exchange):
        '''
        Parameters
        ----------
        symbol :type any asset.
        from_date : MM-DD-YYYY.
        to_date : MM-DD-YYYY.
        interval : minute,3minute,5minute,10minute,15minute,30minute,60minute,day.
        exchange : NSE,BSE,MCX,NFO.
        
        Returns
        -------
        df : returns a dataframe.

        '''
        df = pd.DataFrame()   
        nse_data = self.nse_dump(exchange)
        int_token = self.instrument_token(nse_data, symbol)  #the function we defined above which will return token no. of instrument
        
        to_date   = pd.Timestamp(to_date)
        from_date = pd.Timestamp(from_date)
        
        if interval=='minute':
            timedelta = 60
        if interval == '3minute' or interval =='5minute' or interval == '10minute' or interval == '15minute'\
            or interval == '30minute':
                timedelta = 100
        if interval == '60minute' or interval == 'day':
            timedelta = 400
        
        while True:
            
            if from_date >= (to_date - dt.timedelta(timedelta)):                     
                df = df.append(pd.DataFrame(self.kite.historical_data(int_token, from_date, to_date, interval)))
                break
            
            else:                                                           
                to_date_new = from_date + dt.timedelta(timedelta)
                
                df = df.append(pd.DataFrame(self.kite.historical_data(int_token, from_date, to_date_new, interval)))
                
                #to_date = from_date.date() + dt.timedelta(60)
                from_date = to_date_new
        df.rename(columns={'date': 'index'},inplace=True)
        df.set_index("index",inplace=True)   
        df.index = df.index.tz_localize(None)
        # df = df.drop_duplicates()
        # df = df.apply(pd.to_numeric)
        return df
    
    
    def download(self,asset,interval,start,end,exchange):
        
        asset = [asset]
        time = [interval]
        data = {}    
        threads = []
        Data = data.copy()
        for s in time:
            Data[s] = {}
        
        def f(tf):
            
            for t in asset:
                Data[tf][t] = self.historical_data(t,start,end, tf, exchange)
                
        for i in time:
            t = threading.Thread(target=f,args=[i])
            t.start()
            threads.append(t)
        
        for m in threads:
            m.join()
        
        return Data
    
    def com(self,df1,amount): # mock of zerodha's brokerage calculator - Futures
        
        
        df1['diff'] = abs(df1['Pos'].diff())
        tradebook = df1[df1['diff'] > 0][['Pos','close']]
        tradebook['Amount'] =  0
        tradebook['returns'] = tradebook['close'].pct_change(1)
        tradebook['Exits']= ''
        tradebook['Exits'] = np.where((tradebook['Pos'].shift(1)==1)&(tradebook['Pos']==0),'Exit',tradebook['Exits'])
        tradebook['Exits'] = np.where((tradebook['Pos'].shift(1)==-1)&(tradebook['Pos']==0),'Exit',tradebook['Exits'])
        tradebook['Exits'] = np.where((tradebook['Pos'].shift(1)==-1)&(tradebook['Pos']==1),'Exit',tradebook['Exits'])
        tradebook['Exits'] = np.where((tradebook['Pos'].shift(1)==1)&(tradebook['Pos']==-1),'Exit',tradebook['Exits'])

        tradebook['returns'] = np.where((tradebook['Exits'] !='Exit'),0,tradebook['returns'])
        tradebook['returns'] = np.where((tradebook['Pos'].shift(1) == -1),-tradebook['returns'],tradebook['returns'])
        
        tradebook['Amount'] = 0
        tradebook['Amount'].iloc[0] = amount
        tradebook['comi'] = 0

        for i in range(len(tradebook)):
            last = len(tradebook) - 1
            
            if tradebook['Exits'].iloc[i]=='Exit':
                quantity = (tradebook['Amount'].iloc[i-1]/tradebook['close'].iloc[i-1])
                buy = tradebook['close'].iloc[i-1]
                sell = tradebook['close'].iloc[i]
                # turnover = (quantity*tradebook['close'].iloc[i]) + (quantity*tradebook['close'].iloc[i-1]) 
                turnover = (buy + sell) * quantity 
                # print(quantity)
                base_brok=20
                brok_1 =  base_brok * 2 
                # brok_1 = 0
                brok_2 =  turnover * 0.03/100
                # brok_2 = 0
                brokerage = min(brok_1,brok_2)
                txn_charges = turnover * 0.002/100
                gst = (brokerage + txn_charges) * 18/100
                sebi_charges = (turnover * 10) / 10000000
                stamp_1 = (buy * quantity * 300) / 10000000
                stamp_2 = (buy * quantity * 0.003) / 100
                stamp_duty = min(stamp_1,stamp_2)
                stt = (sell * quantity) * 0.0025/100
                charges = brokerage + stt + txn_charges + gst + sebi_charges + stamp_duty
                charges = round(charges, 2)
                pct_charges = charges/tradebook['Amount'].iloc[i-1]
                returns = tradebook['returns'].iloc[i] - pct_charges
                # print(pct_charges)
                
                tradebook['Amount'].iloc[i] = tradebook['Amount'].iloc[i-1] + (tradebook['Amount'].iloc[i-1] * returns)
                tradebook['comi'].iloc[i] = charges
                
                if i<last:
                    tradebook['Amount'].iloc[i+1] = tradebook['Amount'].iloc[i]
        
        return tradebook

    def brokerage_calculator(self, quantity,segment,buy_p=0, sell_p=0):
      
        if segment == 'intraday':
            
            turnover = (buy_p + sell_p) * quantity
            base_brok=20
            brok_1 =  base_brok * 2 
            brok_2 =  turnover * 0.03/100
            brokerage = min(brok_1,brok_2)
            stt = (sell_p * quantity) * (0.025 / 100)
            txn_charges = turnover * 0.00345/100
            gst = (brokerage + txn_charges) * 18/100
            sebi_charges = (turnover * 10) / 10000000
            stamp_1 = (buy_p * quantity * 300) / 10000000
            stamp_2 = (buy_p * quantity * 0.003) / 100
            stamp_duty = min(stamp_1,stamp_2)
            tot_charges = brokerage + stt + txn_charges + gst + sebi_charges + stamp_duty
            tot_charges = round(tot_charges, 2)
            return tot_charges
        
        if segment == 'cnc':
            
            turnover = (buy_p + sell_p) * quantity
            base_brok=0
            brok_1 =  base_brok * 2 
            brok_2 =  turnover * 0.03/100
            brokerage = min(brok_1,brok_2)
            stt = ((sell_p + buy_p) * quantity) * (0.1 / 100)
            txn_charges = turnover * 0.00345/100
            gst = (brokerage + txn_charges) * 18/100
            sebi_charges = (turnover * 10) / 10000000
            stamp_1 = (buy_p * quantity * 1500) / 10000000
            stamp_2 = (buy_p * quantity * 0.015) / 100
            stamp_duty = min(stamp_1,stamp_2)
            tot_charges = brokerage + stt + txn_charges + gst + sebi_charges + stamp_duty
            tot_charges = round(tot_charges, 2)
            return tot_charges
        
        if segment == 'futures':
            
            turnover = (buy_p + sell_p) * quantity
            base_brok=20
            brok_1 =  base_brok * 2 
            brok_2 =  turnover * 0.03/100
            brokerage = min(brok_1,brok_2)
            stt = (sell_p * quantity) * (0.01 / 100)
            txn_charges = turnover * 0.002/100
            gst = (brokerage + txn_charges) * 18/100
            sebi_charges = (turnover * 10) / 10000000
            stamp_1 = (buy_p * quantity * 200) / 10000000
            stamp_2 = (buy_p * quantity * 0.002) / 100
            stamp_duty = min(stamp_1,stamp_2)
            tot_charges = brokerage + stt + txn_charges + gst + sebi_charges + stamp_duty
            tot_charges = round(tot_charges, 2)
            return tot_charges
        
        if segment == 'options':
            
            turnover = (buy_p + sell_p) * quantity
            base_brok = 20
    
            # Determine brok_1 based on conditions
            if buy_p == 0 or sell_p == 0:
                brok_1 = base_brok
            else:
                brok_1 = base_brok * 2
    
            brokerage = brok_1
            stt = (sell_p * quantity) * (0.05 / 100)
            txn_charges = turnover * 0.053/100
            gst = (brokerage + txn_charges) * 18/100
            sebi_charges = (turnover * 10) / 10000000
            stamp_1 = (buy_p * quantity * 300) / 10000000
            stamp_2 = (buy_p * quantity * 0.003) / 100
            stamp_duty = min(stamp_1, stamp_2)
            tot_charges = brokerage + stt + txn_charges + gst + sebi_charges + stamp_duty
            tot_charges = round(tot_charges, 2)
            return tot_charges
        
        if segment == 'options':
            
            turnover = (buy_p + sell_p) * quantity
            base_brok=20
            brok_1 =  base_brok * 2 
            brokerage = brok_1
            stt = (sell_p * quantity) * (0.05 / 100)
            txn_charges = turnover * 0.053/100
            gst = (brokerage + txn_charges) * 18/100
            sebi_charges = (turnover * 10) / 10000000
            stamp_1 = (buy_p * quantity * 300) / 10000000
            stamp_2 = (buy_p * quantity * 0.003) / 100
            stamp_duty = min(stamp_1,stamp_2)
            tot_charges = brokerage + stt + txn_charges + gst + sebi_charges + stamp_duty
            tot_charges = round(tot_charges, 2)
            return tot_charges
       
    
# brokerage_calculator(40000, 40250, 25, 'cnc')
    
    
  
    
    
    
