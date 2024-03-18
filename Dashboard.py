import streamlit as st
from datetime import date,datetime
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import mpld3
from mpld3 import plugins
import streamlit.components.v1 as components
from nselib import capital_market

@st.cache_data 
def get_symbol():
    data=capital_market.equity_list()
    return data

def convert_to_float(value):
        if type(value) is str:
            return float(value.replace(',', ''))
        else:
            return value

@st.cache_data 
def fetch_data(symbol, start_date, end_date):
    data = capital_market.price_volume_and_deliverable_position_data(symbol=symbol, from_date=start_date, to_date=end_date)


    data['HighPrice'] = data['HighPrice'].apply(convert_to_float)
    data['LowPrice'] = data['LowPrice'].apply(convert_to_float)
    data['OpenPrice'] = data['OpenPrice'].apply(convert_to_float)
    data['ClosePrice'] = data['ClosePrice'].apply(convert_to_float)

    data = data.dropna()

    return data

@st.cache_data 
def calculate_percentage(symbol, start_date, end_date):

    curr_data=fetch_data(symbol,start_date,date.today().strftime("%d-%m-%Y"))
    curr_data.to_csv('data.csv')

    df = pd.read_csv('data.csv')

    df['Date'] = pd.to_datetime(df['Date'], format='%d-%b-%Y')

    filtered_data = df[(df['Date'] >= start_date) & (df['Date'] <= end_date)]
    print(filtered_data)
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

@st.cache_data 
def calculate_difference(symbol, start_date, end_date):
    df = pd.read_csv('data.csv')

    df['Date'] = pd.to_datetime(df['Date'], format='%d-%b-%Y')

    filtered_data = df[(df['Date'] >= start_date) & (df['Date'] <= end_date)]

    if len(filtered_data) == 0:
        st.warning("No data available for the selected date range.")
        return None

    difference = filtered_data['HighPrice'] - filtered_data['ClosePrice']

    return difference, filtered_data['Date'], filtered_data['ClosePrice']

def calculate_ema(close_data):
    # window=(datetime.strptime(end_date, '%d-%m-%Y')-datetime.strptime(start_date, '%d-%m-%Y')).days
    ema = close_data.ewm(span=20, adjust=False).mean()
    return ema
    

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


def plot_high_three(dates,highPrice,ema,pivot):
    dates = pd.to_datetime(dates)
    dates = dates.dt.strftime('%d-%m-%Y')

    dates = [datetime.strptime(date_str, "%d-%m-%Y") for date_str in dates]

    dates = mdates.date2num(dates)

    fig, ax = plt.subplots(figsize=(8, 6))
    scatter = ax.scatter(dates, ema,color='green', alpha=0.5, s=10)
    ax.plot(dates, ema, label='Exponential Moving Average', color='green')
    scatter = ax.scatter(dates, highPrice, color='red', alpha=0.5, s=10)
    ax.plot(dates, highPrice, label='High', color='red')
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

    symbol = st.sidebar.selectbox("Enter Symbol",get_symbol())
    start_date = st.sidebar.date_input("Select Start Date:",format='DD-MM-YYYY').strftime("%d-%m-%Y")
    end_date = st.sidebar.date_input("Select End Date:",format='DD-MM-YYYY').strftime("%d-%m-%Y")

    
    if st.button("Calculate"):
        
        
        percentage, avg, open_price, close_price, high_price, low_price, curr_price, highPrice = calculate_percentage(symbol, start_date, end_date)
        difference, dates, close_value = calculate_difference(symbol, start_date, end_date)
        ema=calculate_ema(close_value)
        
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
                plot_high_three(dates,highPrice,ema,avg)

            # with st.expander("Difference between High and Open"):
            #     plot_graph_difference(difference, dates)
            
            # with st.expander("EMA"):
            #     plot_graph_ema(ema, dates)


if __name__ == "__main__":
    main()
