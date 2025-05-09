import tkinter as tk
from tkinter import messagebox, filedialog, simpledialog, Menu, ttk
import threading
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from datetime import datetime
import stock_data
from stock_class import Equity
import pandas as pd


class StockTrackerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Stock Analysis Assistant")
        self.stocks = []

        self.setup_menu()
        self.setup_tabs()
        self.setup_main_tab()
        self.setup_history_tab()

    def setup_menu(self):
        menubar = Menu(self.root)
        self.root.config(menu=menubar)

        file_menu = Menu(menubar, tearoff=0)
        file_menu.add_command(label="Exit", command=self.root.quit)
        menubar.add_cascade(label="File", menu=file_menu)

        web_menu = Menu(menubar, tearoff=0)
        web_menu.add_command(label="Fetch Data", command=self.request_data)
        menubar.add_cascade(label="Web", menu=web_menu)

    def setup_tabs(self):
        self.tab_control = ttk.Notebook(self.root)
        self.tab_main = tk.Frame(self.tab_control)
        self.tab_history = tk.Frame(self.tab_control)
        self.tab_graph = tk.Frame(self.tab_control)

        self.tab_control.add(self.tab_main, text="Portfolio")
        self.tab_control.add(self.tab_history, text="History")
        self.tab_control.add(self.tab_graph, text="Visualization")
        self.tab_control.pack(expand=1, fill="both")

    def setup_main_tab(self):
        tk.Label(self.tab_main, text="Ticker Symbol:").grid(row=0, column=0)
        tk.Label(self.tab_main, text="Company Name:").grid(row=1, column=0)
        tk.Label(self.tab_main, text="Shares:").grid(row=2, column=0)

        self.entry_symbol = tk.Entry(self.tab_main)
        self.entry_name = tk.Entry(self.tab_main)
        self.entry_shares = tk.Entry(self.tab_main)

        self.entry_symbol.grid(row=0, column=1)
        self.entry_name.grid(row=1, column=1)
        self.entry_shares.grid(row=2, column=1)

        tk.Button(self.tab_main, text="Add to Portfolio", command=self.add_stock, bg="green", fg="white").grid(row=3, column=1)
        self.stock_listbox = tk.Listbox(self.tab_main, width=50)
        self.stock_listbox.grid(row=0, column=2, rowspan=5)

    def setup_history_tab(self):
        self.text_history = tk.Text(self.tab_history)
        self.text_history.pack(expand=True, fill='both')

    def add_stock(self):
        symbol = self.entry_symbol.get()
        name = self.entry_name.get()
        try:
            shares = float(self.entry_shares.get())
            new_stock = Equity(symbol, name, shares)
            self.stocks.append(new_stock)
            self.refresh_portfolio()
        except:
            messagebox.showerror("Invalid Input", "Please enter valid data.")

    def refresh_portfolio(self):
        self.stock_listbox.delete(0, tk.END)
        for s in self.stocks:
            self.stock_listbox.insert(tk.END, f"{s.symbol} | {s.name} | {s.shares} shares")

    def request_data(self):
        start = simpledialog.askstring("Start Date", "MM/DD/YY")
        end = simpledialog.askstring("End Date", "MM/DD/YY")
        if not start or not end:
            return
        threading.Thread(target=self.fetch_data, args=(start, end)).start()

    def fetch_data(self, start, end):
        try:
            count = stock_data.retrieve_stock_web(start, end, self.stocks)
            self.root.after(0, lambda: self.handle_fetch_complete(count))
        except Exception as e:
            messagebox.showerror("Fetch Error", str(e))

    def handle_fetch_complete(self, count):
        if count == 0:
            messagebox.showinfo("Completed", "No records fetched.")
        else:
            messagebox.showinfo("Completed", f"Fetched {count} entries.")
            for stock in self.stocks:
                if hasattr(stock, 'records') and stock.records:
                    self.show_graph(stock)
                    self.show_history(stock)
                    self.tab_control.select(self.tab_graph)
                    break

    def show_graph(self, stock):
        for widget in self.tab_graph.winfo_children():
            widget.destroy()

        sorted_data = sorted(stock.records, key=lambda x: datetime.strptime(x.date, "%b %d, %Y"))
        dates = [datetime.strptime(d.date, "%b %d, %Y") for d in sorted_data]
        prices = [d.close for d in sorted_data]

        fig, ax = plt.subplots(figsize=(7, 4))
        ax.plot(dates, prices, marker='x', linestyle='-', color='purple')
        ax.set_title(f"{stock.symbol.upper()} Trend")
        ax.set_xlabel("Date")
        ax.set_ylabel("Close Price")
        ax.grid(True)

        chart = FigureCanvasTkAgg(fig, master=self.tab_graph)
        chart.draw()
        chart.get_tk_widget().pack(fill='both', expand=True)

    def show_history(self, stock):
        self.text_history.delete("1.0", tk.END)
        self.text_history.insert(tk.END, f"Data for {stock.symbol} ({stock.name})\n\n")
        for rec in stock.records:
            self.text_history.insert(tk.END, f"{rec.date} | Close: ${rec.close:.2f} | Vol: {rec.volume}\n")


if __name__ == "__main__":
    root = tk.Tk()
    app = StockTrackerApp(root)
    root.mainloop()
