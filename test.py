import streamlit as st
import threading
import time
from datetime import date,datetime
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import mpld3
import streamlit.components.v1 as components
from nselib import capital_market


def calculate_ema(close_data):
    # window=(datetime.strptime(end_date, '%d-%m-%Y')-datetime.strptime(start_date, '%d-%m-%Y')).days
    ema = close_data.ewm(span=20, adjust=False).mean()
    return ema
 
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

def calculate_percentage(symbol, start_date, end_date):

    curr_data=fetch_data(symbol,start_date,date.today().strftime("%d-%m-%Y"))
    curr_data.to_csv('data.csv')

    df = pd.read_csv('data.csv')

    df['Date'] = pd.to_datetime(df['Date'], format='%d-%b-%Y')

    filtered_data = df[(df['Date'] >= start_date) & (df['Date'] <= end_date)]
    curr_price=curr_data['LastPrice'].iloc[-1]
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
    return percentage, avg, open_data, close_data, high_data, low_data, curr_price, filtered_data['HighPrice']


def calculate_difference(symbol, start_date, end_date):
    df = pd.read_csv('data.csv')

    df['Date'] = pd.to_datetime(df['Date'], format='%d-%b-%Y')

    filtered_data = df[(df['Date'] >= start_date) & (df['Date'] <= end_date)]

    if len(filtered_data) == 0:
        st.warning("No data available for the selected date range.")
        return None

    difference = filtered_data['HighPrice'] - filtered_data['ClosePrice']

    return difference, filtered_data['Date'], filtered_data['ClosePrice']
    

def plot_graph_difference(difference, dates):

    dates=pd.to_datetime(dates)
    dates=dates.dt.strftime('%d-%m-%Y')

    dates = [datetime.strptime(date_str, "%d-%m-%Y") for date_str in dates]

    dates=mdates.date2num(dates)
    
    # print(type(dates))
    fig, ax = plt.subplots(figsize=(8, 6))
    scatter = ax.scatter(dates, difference, label='Difference', color='blue', alpha=0.5, s=10)
    ax.plot(dates, difference, label='Difference (High - Open)')
    ax.tick_params(labelrotation=45)
    ax.set_xlabel('Date')
    ax.set_ylabel('Difference')
    ax.set_title('Difference between High and Open')
    ax.legend()

    ax.xaxis_date()
    ax.xaxis.set_major_locator(mdates.YearLocator())

    dates = [mdates.num2date(date) for date in dates]
    labels = ['Date: {0}\nDifference: {1:.2f}'.format(date.strftime('%d-%m-%Y'), close) for date, close in zip(dates, difference)]
    tooltip = mpld3.plugins.PointLabelTooltip(scatter, labels=labels)
    mpld3.plugins.connect(fig, tooltip)

    fig_html = mpld3.fig_to_html(fig)
    components.html(fig_html, height=650)

def plot_graph_close(dates, close_value):

    dates=pd.to_datetime(dates)
    dates=dates.dt.strftime('%d-%m-%Y')

    dates = [datetime.strptime(date_str, "%d-%m-%Y") for date_str in dates]

    dates=mdates.date2num(dates)
    
    fig, ax = plt.subplots(figsize=(8, 6))
    scatter = ax.scatter(dates, close_value, label='Close value', color='red', alpha=0.5, s=10)
    ax.plot(dates, close_value, label='Close value', color='red')
    ax.tick_params(labelrotation=45)
    ax.set_xlabel('Date')
    ax.set_ylabel('Close Values')
    ax.set_title('Close Values')
    ax.legend()

    ax.xaxis_date()
    ax.xaxis.set_major_locator(mdates.YearLocator())

    dates = [mdates.num2date(date) for date in dates]
    labels = ['Date: {0}\nClose Value: {1:.2f}'.format(date.strftime('%d-%m-%Y'), close) for date, close in zip(dates, close_value)]
    tooltip = mpld3.plugins.PointLabelTooltip(scatter, labels=labels)
    mpld3.plugins.connect(fig, tooltip)

    fig_html = mpld3.fig_to_html(fig)
    components.html(fig_html, height=650)


def plot_graph_ema(ema, dates):
    dates = pd.to_datetime(dates)
    dates = dates.dt.strftime('%d-%m-%Y')

    dates = [datetime.strptime(date_str, "%d-%m-%Y") for date_str in dates]

    dates = mdates.date2num(dates)

    fig, ax = plt.subplots(figsize=(8, 6))
    scatter = ax.scatter(dates, ema, label='EMA', color='green', alpha=0.5, s=10)
    ax.plot(dates, ema, label='Exponential Moving Average', color='green')
    ax.tick_params(labelrotation=45)
    ax.set_xlabel('Date')
    ax.set_ylabel('EMA')
    ax.set_title('Exponential Moving Average')
    ax.legend()

    ax.xaxis_date()
    ax.xaxis.set_major_locator(mdates.YearLocator())

    dates = [mdates.num2date(date) for date in dates]
    labels = ['Date: {0}\nEMA: {1:.2f}'.format(date.strftime('%d-%m-%Y'), close) for date, close in zip(dates, ema)]
    tooltip = mpld3.plugins.PointLabelTooltip(scatter, labels=labels)
    mpld3.plugins.connect(fig, tooltip)

    fig_html = mpld3.fig_to_html(fig)
    components.html(fig_html, height=650)

def plot_close_three(dates,ClosePrice,ema,pivot):
    dates = pd.to_datetime(dates)
    dates = dates.dt.strftime('%d-%m-%Y')

    dates = [datetime.strptime(date_str, "%d-%m-%Y") for date_str in dates]

    dates = mdates.date2num(dates)

    fig, ax = plt.subplots(figsize=(8, 6))
    scatter = ax.scatter(dates, ema,color='green', alpha=0.5, s=10)
    ax.plot(dates, ema, label='Exponential Moving Average', color='green')
    scatter = ax.scatter(dates, ClosePrice, color='red', alpha=0.5, s=10)
    ax.plot(dates, ClosePrice, label='Close', color='red')
    ax.plot(dates,[pivot] * len(dates), label='pivot', color='blue')

    ax.tick_params(labelrotation=45)
    ax.set_xlabel('Date')
    ax.set_ylabel('Price')
    ax.set_title('Exponential Moving Average')
    ax.legend()

    ax.xaxis_date()
    ax.xaxis.set_major_locator(mdates.YearLocator())

    dates = [mdates.num2date(date) for date in dates]
    labels = ['Date: {0}\nValue: {1:.2f}'.format(date.strftime('%d-%m-%Y'), close) for date, close in zip(dates, ema)]
    tooltip = mpld3.plugins.PointLabelTooltip(scatter, labels=labels)
    mpld3.plugins.connect(fig, tooltip)

    fig_html = mpld3.fig_to_html(fig)
    components.html(fig_html, height=650)

def main():
    st.title("Stock Analysis Tool")
    start_date = st.sidebar.date_input("Select Start Date:", format='DD-MM-YYYY').strftime("%d-%m-%Y")
    end_date = st.sidebar.date_input("Select End Date:", format='DD-MM-YYYY').strftime("%d-%m-%Y")

    if 'btn_clicked' not in st.session_state:
        st.session_state['btn_clicked'] = False


    def callback():
    # change state value
        st.session_state['btn_clicked'] = True


    if st.button('Get Symbol', on_click=callback) or st.session_state['btn_clicked']:
        
        if 'symbols' not in st.session_state:
            st.session_state.symbols = get_options_after_ema(start_date, end_date)
        st.session_state.symbol = st.sidebar.selectbox("Enter Symbol", st.session_state['symbols'])

    if st.button("Calculate"):
        percentage, avg, open_price, close_price, high_price, low_price, curr_price, highPrice = calculate_percentage(st.session_state.symbol, start_date, end_date)
        difference, dates, close_value = calculate_difference(st.session_state.symbol, start_date, end_date)
        ema = calculate_ema(close_value)

        if percentage is not None:
            st.sidebar.write(f"Current Price: {curr_price:.2f}")
            st.sidebar.write(f"Percentage Change: {percentage:.2f}%")
            st.sidebar.write(f"Pivot for date range: {avg:.2f}")
            st.sidebar.write(f"EMA: {ema.iloc[-1]:.2f}")
            st.sidebar.write(f"Open: {open_price:.2f}")
            st.sidebar.write(f"Close: {close_price:.2f}")
            st.sidebar.write(f"High: {high_price:.2f}")
            st.sidebar.write(f"Low: {low_price:.2f}")

        if difference is not None:
            # Add tabs
             with st.expander("Plot", expanded=True):
                plot_close_three(dates,close_value,ema,avg)

if __name__=="__main__":
    main()
