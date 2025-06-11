import tkinter as tk
from tkinter import ttk, messagebox
from stock_api import get_historical_data
import config
import matplotlib
matplotlib.use('TkAgg')
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import mplfinance as mpf
import pandas_ta as ta

def plot_chart(df, symbol, chart_frame, indicators):
    for widget in chart_frame.winfo_children():
        widget.destroy()

    mpf_args = {'type':'candle', 'volume':True, 'style':'yahoo', 'title':f'{symbol} Analysis'}

    if indicators['SMA']:
        df['SMA20'] = ta.sma(df['Close'], length=20)
        mpf_args['mav'] = (20,)
    if indicators['EMA']:
        df['EMA20'] = ta.ema(df['Close'], length=20)
        apds = [mpf.make_addplot(df['EMA20'], color='red')]
        mpf_args['addplot'] = apds
    if indicators['RSI']:
        df['RSI'] = ta.rsi(df['Close'])
        apds = mpf_args.get('addplot', [])
        apds.append(mpf.make_addplot(df['RSI'], panel=2, color='blue', ylabel='RSI'))
        mpf_args['addplot'] = apds
        mpf_args['figscale'] = 1.2

    fig, _ = mpf.plot(df, returnfig=True, **mpf_args)

    canvas = FigureCanvasTkAgg(fig, master=chart_frame)
    canvas.draw()
    canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

def fetch_and_update(symbol_entry, interval_var, outputsize_var, chart_frame, indicator_vars):
    symbol = symbol_entry.get().upper()
    interval = interval_var.get()
    outputsize = outputsize_var.get()

    try:
        df = get_historical_data(symbol, interval=interval, outputsize=outputsize)
        df.columns = ['Open', 'High', 'Low', 'Close', 'Volume']
        df.index.name = 'Date'

        indicators = {name: var.get() for name, var in indicator_vars.items()}
        plot_chart(df, symbol, chart_frame, indicators)

    except Exception as e:
        messagebox.showerror("Error", f"Could not fetch data: {e}")

def create_main_window():
    window = tk.Tk()
    window.title("Advanced Stock Analytics with Intervals")
    window.geometry('1300x850')

    controls_frame = ttk.Frame(window)
    controls_frame.pack(pady=10)

    ttk.Label(controls_frame, text="Stock Symbol:", font=("Arial", 12)).pack(side=tk.LEFT, padx=5)
    symbol_entry = ttk.Entry(controls_frame, font=("Arial", 12), width=8)
    symbol_entry.pack(side=tk.LEFT, padx=5)
    symbol_entry.insert(0, config.DEFAULT_SYMBOL)

    ttk.Label(controls_frame, text="Interval:", font=("Arial", 12)).pack(side=tk.LEFT, padx=5)
    interval_var = ttk.Combobox(controls_frame, values=['1min', '5min', '15min', '30min', '60min'], width=7)
    interval_var.pack(side=tk.LEFT, padx=5)
    interval_var.set('15min')

    ttk.Label(controls_frame, text="Data Size:", font=("Arial", 12)).pack(side=tk.LEFT, padx=5)
    outputsize_var = ttk.Combobox(controls_frame, values=['compact', 'full'], width=8)
    outputsize_var.pack(side=tk.LEFT, padx=5)
    outputsize_var.set('compact')

    indicator_vars = {
        'SMA': tk.BooleanVar(value=True),
        'EMA': tk.BooleanVar(value=False),
        'RSI': tk.BooleanVar(value=False),
    }

    ttk.Checkbutton(controls_frame, text='SMA (20)', variable=indicator_vars['SMA']).pack(side=tk.LEFT, padx=5)
    ttk.Checkbutton(controls_frame, text='EMA (20)', variable=indicator_vars['EMA']).pack(side=tk.LEFT, padx=5)
    ttk.Checkbutton(controls_frame, text='RSI', variable=indicator_vars['RSI']).pack(side=tk.LEFT, padx=5)

    fetch_button = ttk.Button(
        controls_frame, 
        text="Fetch & Analyze", 
        command=lambda: fetch_and_update(
            symbol_entry, interval_var, outputsize_var, chart_frame, indicator_vars
        )
    )
    fetch_button.pack(side=tk.LEFT, padx=5)

    chart_frame = ttk.Frame(window)
    chart_frame.pack(pady=10, fill=tk.BOTH, expand=True)

    fetch_and_update(symbol_entry, interval_var, outputsize_var, chart_frame, indicator_vars)

    window.mainloop()

if __name__ == "__main__":
    create_main_window()
