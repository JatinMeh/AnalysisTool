import sys
import tkinter as tk
from tkinter import ttk,filedialog,messagebox
from tkcalendar import DateEntry
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg,NavigationToolbar2Tk
import mplcursors

#Calculate the Percentage between current value and the average
def calculate_percentage(file_path, start_date, end_date, curr_price):

    df = pd.read_csv(file_path)

    df['Date '] = pd.to_datetime(df['Date '], format='%d-%b-%Y')

    start_date = pd.to_datetime(start_date, format='%Y-%m-%d')
    end_date = pd.to_datetime(end_date, format='%Y-%m-%d')

    filtered_data = df[(df['Date '] >= start_date) & (df['Date '] <= end_date)]

    if len(filtered_data) == 0:
        messagebox.showwarning("No Data", "No data available for the selected date range.")
        return None

    high_sorted = filtered_data.sort_values(by='High ', ascending=False)
    low_sorted = filtered_data.sort_values(by='Low ', ascending=False)

    open_data = filtered_data['Open '].iloc[0]
    close_data = filtered_data['Close '].iloc[-1]
    high_data = high_sorted['High '].iloc[0]
    low_data = low_sorted['Low '].iloc[0]

    total = open_data + close_data + high_data + low_data
    avg = total / 4

    percentage = ((curr_price - avg) / avg) * 100
    return percentage,avg,open_data,close_data,high_data,low_data

#Calculating difference between high - close
def calculate_difference(file_path, start_date, end_date):
    df = pd.read_csv(file_path)

    df['Date '] = pd.to_datetime(df['Date '], format='%d-%b-%Y')

    start_date = pd.to_datetime(start_date, format='%Y-%m-%d')
    end_date = pd.to_datetime(end_date, format='%Y-%m-%d')

    filtered_data = df[(df['Date '] >= start_date) & (df['Date '] <= end_date)]

    if len(filtered_data) == 0:
        messagebox.showwarning("No Data", "No data available for the selected date range.")
        return None

    difference=filtered_data['High ']-filtered_data['Close ']

    return difference,filtered_data['Date '],filtered_data['Close ']


#default date range after selecting csv file
def set_default_date_range(file_path):
    try:
        df = pd.read_csv(file_path)
        df['Date '] = pd.to_datetime(df['Date '], format='%d-%b-%Y')
        most_recent_date = df['Date '].max()
        oldest_date = df['Date '].min()
        start_date_entry.set_date(oldest_date)
        end_date_entry.set_date(most_recent_date)
    except Exception as e:
        messagebox.showerror("Error", f"Error while setting default date range: {str(e)}")

#browse button
def browse_file():
    file_path = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv")])
    file_path_entry.delete(0, tk.END)
    file_path_entry.insert(0, file_path)
    set_default_date_range(file_path)

#Plotting graph
def plot_graph(difference,dates,close_value):

    graph_window = tk.Toplevel(window)
    graph_window.title("Difference Graph")

    fig, ax = plt.subplots(figsize=(8, 6))

    unique_dates = sorted(set(dates))

    ax.plot(unique_dates, difference, label='Difference (High - Open)')
    ax.plot(unique_dates, close_value, label='Close value', color='red')
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
    

    file_path = file_path_entry.get()
    start_date = start_date_entry.get()
    end_date = end_date_entry.get()
    curr_price = float(curr_price_entry.get())

    #print(calculate_difference(file_path,start_date,end_date))    

    percentage,avg,open,close,high,low = calculate_percentage(file_path, start_date, end_date, curr_price)
    difference, dates,close_value=calculate_difference(file_path,start_date,end_date)

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
tk.Label(window, text="*CSV File Path:").grid(row=0, column=0, padx=10, pady=10)
file_path_entry = tk.Entry(window)
file_path_entry.grid(row=0, column=1, padx=10, pady=10)

browse_button = tk.Button(window, text="Browse", command=browse_file)
browse_button.grid(row=0, column=2, padx=10, pady=10)

#Range selection
tk.Label(window, text="*Select Date Range:").grid(row=1, column=0, padx=10, pady=10)
start_date_entry = DateEntry(window, width=12, background='darkblue', foreground='white', date_pattern='yyyy-mm-dd')
start_date_entry.grid(row=1, column=1, padx=10, pady=10)
tk.Label(window, text="to").grid(row=1, column=2, padx=10, pady=10)
end_date_entry = DateEntry(window, width=12, background='darkblue', foreground='white', date_pattern='yyyy-mm-dd')
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
