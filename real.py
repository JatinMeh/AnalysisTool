from nselib import capital_market
from datetime import date
import sys
import tkinter as tk
from tkinter import ttk,filedialog,messagebox
from tkcalendar import DateEntry
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg,NavigationToolbar2Tk
import mplcursors

def fetch_data(symbol,start_date,end_date):
    data=capital_market.price_volume_and_deliverable_position_data(symbol=symbol,from_date=start_date,to_date=end_date)

    def convert_to_float(value):
        
        if type(value) is str:
            return float(value.replace(',', ''))
        else:
            return value
            
    data['HighPrice'] = data['HighPrice'].apply(convert_to_float)
    data['LowPrice'] = data['LowPrice'].apply(convert_to_float)
    data['OpenPrice'] = data['OpenPrice'].apply(convert_to_float)
    data['ClosePrice'] = data['ClosePrice'].apply(convert_to_float)

    data=data.dropna()

    return data

def clean_currency(x):
    if isinstance(x, str):
        return(x.replace(',', ''))
    return(x)

#Calculate the Percentage between current value and the average
def calculate_percentage(symbol, start_date, end_date, curr_price):

    filtered_data = fetch_data(symbol,start_date,end_date)


    if len(filtered_data) == 0:
        messagebox.showwarning("No Data", "No data available for the selected date range.")
        return None

    high_sorted = filtered_data.sort_values(by='HighPrice', ascending=False)
    low_sorted = filtered_data.sort_values(by='LowPrice', ascending=False)

    open_data = filtered_data['OpenPrice'].iloc[0]
    close_data = filtered_data['ClosePrice'].iloc[-1]
    high_data = high_sorted['HighPrice'].iloc[0]
    low_data = low_sorted['LowPrice'].iloc[0]

    total = open_data + close_data + high_data + low_data
    avg = total / 4

    percentage = ((curr_price - avg) / avg) * 100
    return percentage,avg,open_data,close_data,high_data,low_data

#Calculating difference between high - close
def calculate_difference(symbol, start_date, end_date):
   
    filtered_data = fetch_data(symbol,start_date,end_date)

    if len(filtered_data) == 0:
        messagebox.showwarning("No Data", "No data available for the selected date range.")
        return None

    difference=filtered_data['HighPrice']-filtered_data['ClosePrice']

    return difference,filtered_data['Date'],filtered_data['ClosePrice']


#Plotting graph
def plot_graph(difference,dates,close_value):

    graph_window = tk.Toplevel(window)
    graph_window.title("Difference Graph")

    fig, ax = plt.subplots(figsize=(8, 6))

    # unique_dates = sorted(set(dates))

    ax.plot(dates, difference, label='Difference (High - Open)')
    ax.plot(dates, close_value, label='Close value', color='red')
    ax.tick_params(labelrotation=45)
    ax.set_xlabel('Date')
    ax.set_ylabel('Difference')
    ax.set_title('Difference between High and Open')
    ax.legend()

    # Embed the plot in the Tkinter window
    canvas = FigureCanvasTkAgg(fig, master=graph_window)
    canvas_widget = canvas.get_tk_widget()
    canvas_widget.pack(side=tk.TOP, fill=tk.BOTH, expand=1) 

    toolbar = NavigationToolbar2Tk(canvas, graph_window)
    toolbar.update()
    canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)

    mplcursors.cursor(hover=True).connect("add", lambda sel: sel.annotation.set_text(f"{sel.artist.get_label()}\nDifference: {sel.target[1]:.2f}"))

    graph_window.protocol("WM_DELETE_WINDOW", lambda: on_graph_window_close(graph_window))



def on_graph_window_close(graph_window):
    graph_window.destroy()

#Submit button
def on_submit():
    if curr_price_entry.get() == '' or curr_price_entry.get().isalpha():
        messagebox.showwarning("Error","Please check your current value and enter the number")
        return None
    

    symbol = symbol_value.get()
    start_date = start_date_entry.get()
    end_date = end_date_entry.get()
    curr_price = float(curr_price_entry.get())

    #print(calculate_difference(file_path,start_date,end_date))    

    percentage,avg,open,close,high,low = calculate_percentage(symbol, start_date, end_date, curr_price)
    difference, dates,close_value=calculate_difference(symbol,start_date,end_date)

    if percentage is not None:
        result_label.config(text=f"Percentage Change: {percentage:.2f}%")
        avg_label.config(text=f"Pivot for date range: {avg:.2f}")
        open_label.config(text=f"Open: {open:.2f}")
        close_label.config(text=f"Close: {close:.2f}")
        high_label.config(text=f"High: {high:.2f}")
        low_label.config(text=f"Low: {low:.2f}")
    
    if difference is not None:
        plot_graph(difference,dates,close_value)
    


window = tk.Tk()
window.title("Stock Analysis Tool")

#CSV file path
tk.Label(window, text="*Symbol: ").grid(row=0, column=0, padx=10, pady=10)
symbol_value= tk.Entry(window)
symbol_value.grid(row=0, column=1, padx=10, pady=10)

#Range selection
tk.Label(window, text="*Select Date Range:").grid(row=1, column=0, padx=10, pady=10)
start_date_entry = DateEntry(window, width=12, background='darkblue', foreground='white', date_pattern='dd-mm-yyyy')
start_date_entry.grid(row=1, column=1, padx=10, pady=10)
tk.Label(window, text="to").grid(row=1, column=2, padx=10, pady=10)
end_date_entry = DateEntry(window, width=12, background='darkblue', foreground='white', date_pattern='dd-mm-yyyy')
end_date_entry.grid(row=1, column=3, padx=10, pady=10)

#Current value
tk.Label(window, text="*Enter Current Value:").grid(row=2, column=0, padx=10, pady=10)
curr_price_entry = tk.Entry(window)
curr_price_entry.grid(row=2, column=1, padx=10, pady=10)

#calculate button
submit_button = tk.Button(window, text="Calculate", command=on_submit)
submit_button.grid(row=3, column=0, columnspan=2, pady=20)

#display other values
open_label = tk.Label(window, text="")
open_label.grid(row=4, column=0, padx=10, pady=10)
close_label = tk.Label(window, text="")
close_label.grid(row=4, column=1, padx=10, pady=10)
high_label = tk.Label(window, text="")
high_label.grid(row=4, column=2, padx=10, pady=10)
low_label = tk.Label(window, text="")
low_label.grid(row=4, column=3, padx=10, pady=10)

#Display pivot for date range
avg_label = tk.Label(window, text="")
avg_label.grid(row=5, column=0, padx=10, pady=10)

#Display Percentage
result_label = tk.Label(window, text="")
result_label.grid(row=5, column=1, columnspan=2, pady=10)

window.protocol("WM_DELETE_WINDOW", lambda:sys.exit())

window.mainloop()



