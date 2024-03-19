import streamlit as st
import threading
import time
from datetime import datetime
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import mpld3
import streamlit.components.v1 as components
from nselib import capital_market

#caluculating EMA(Exponential Moving Average)
def calculate_ema(close_data):
    ema = close_data.ewm(span=20, adjust=False).mean()
    return ema
 
#Getting symbols after filtering NIFTY 50
def get_symbol(symbol, result_list,start_date,end_date):
    data = capital_market.price_volume_and_deliverable_position_data(symbol=symbol, from_date=start_date, to_date=end_date)
    
    def convert_to_float(value):
        if isinstance(value, str):
            return float(value.replace(',', ''))
        else:
            return value

    data['ClosePrice'] = data['ClosePrice'].apply(convert_to_float)

    data = data.dropna()
        
    ema = calculate_ema(data['ClosePrice'])
    
    if ema.iloc[-1] > ema.iloc[-2] and ema.iloc[-1] < data['ClosePrice'].iloc[-1] and ema.iloc[-2] > data['ClosePrice'].iloc[-2]:
        result_list.append(symbol)

def get_options_after_ema(start_date,end_date):
    result_list = []
    idx = capital_market.nifty50_equity_list()
    symbols = idx['Symbol']
    
    threads = []
    
    for symbol in symbols:
        thread = threading.Thread(target=get_symbol, args=(symbol, result_list, start_date, end_date))
        thread.start()
        time.sleep(0.6)
        threads.append(thread)
    
    for thread in threads:
        thread.join()

    return result_list

def convert_to_float(value):
        if type(value) is str:
            return float(value.replace(',', ''))
        else:
            return value
        
def fetch_data(symbol, start_date, end_date):
    data = capital_market.price_volume_and_deliverable_position_data(symbol=symbol, from_date=start_date, to_date=end_date)


    data['HighPrice'] = data['HighPrice'].apply(convert_to_float)
    data['LowPrice'] = data['LowPrice'].apply(convert_to_float)
    data['OpenPrice'] = data['OpenPrice'].apply(convert_to_float)
    data['ClosePrice'] = data['ClosePrice'].apply(convert_to_float)

    data = data.dropna()

    return data

#Calculate Values
def calculate_percentage(symbol, start_date, end_date):

    curr_data=fetch_data(symbol,start_date,end_date)
    curr_data.to_csv('data.csv')

    df = pd.read_csv('data.csv')

    df['Date'] = pd.to_datetime(df['Date'], format='%d-%b-%Y')

    filtered_data = df
    curr_price=curr_data['ClosePrice'].iloc[-1]
    curr_price=convert_to_float(curr_price)

    if len(filtered_data) == 0:
        st.warning("No data available for the selected date range.")
        return None

    open_data = filtered_data['OpenPrice'].iloc[0]
    close_data = filtered_data['ClosePrice'].iloc[0]
    high_data = filtered_data['HighPrice'].iloc[0]
    low_data = filtered_data['LowPrice'].iloc[0]

    total = close_data + high_data + low_data
    avg = total / 3

    percentage = ((curr_price - avg) / avg) * 100
    return percentage, avg, curr_price


def calculate_difference():
    df = pd.read_csv('data.csv')

    df['Date'] = pd.to_datetime(df['Date'], format='%d-%b-%Y')

    filtered_data = df

    if len(filtered_data) == 0:
        st.warning("No data available for the selected date range.")
        return None

    difference = filtered_data['HighPrice'] - filtered_data['ClosePrice']

    return difference, filtered_data['Date'], filtered_data['ClosePrice']
    
#Graph Plotting
def plot_close_three(dates,ClosePrice,ema,pivot):
    dates = pd.to_datetime(dates)
    dates = dates.dt.strftime('%d-%m-%Y')

    dates = [datetime.strptime(date_str, "%d-%m-%Y") for date_str in dates]

    dates = mdates.date2num(dates)

    fig, ax = plt.subplots(figsize=(8, 6))
    scatter = ax.scatter(dates, ema,color='green', alpha=0.5, s=10)
    ax.plot(dates, ema, label='Exponential Moving Average', color='green')
    scatter2 = ax.scatter(dates, ClosePrice, color='red', alpha=0.5, s=10)
    ax.plot(dates, ClosePrice, label='Close', color='red')
    ax.plot(dates,[pivot] * len(dates), label='pivot', color='blue')

    ax.tick_params(labelrotation=45)
    ax.set_xlabel('Date')
    ax.set_ylabel('Price')
    ax.set_title('Graph')
    ax.legend()

    ax.xaxis_date()
    ax.xaxis.set_major_locator(mdates.YearLocator())

    dates = [mdates.num2date(date) for date in dates]
    labels = ['Date: {0}\nValue: {1:.2f}'.format(date.strftime('%d-%m-%Y'), close) for date, close in zip(dates, ema)]
    tooltip = mpld3.plugins.PointLabelTooltip(scatter, labels=labels)
    labels2 = ['Date: {0}\nValue: {1:.2f}'.format(date.strftime('%d-%m-%Y'), close) for date, close in zip(dates, ClosePrice)]
    tooltip2 = mpld3.plugins.PointLabelTooltip(scatter2, labels=labels2)
    mpld3.plugins.connect(fig, tooltip)
    mpld3.plugins.connect(fig, tooltip2)

    fig_html = mpld3.fig_to_html(fig)
    components.html(fig_html, height=650)