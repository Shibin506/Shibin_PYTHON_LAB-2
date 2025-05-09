from stock_models import Stock, DailyData
from stock_data import retrieve_stock_web, import_stock_web_csv
from stock_db import save_to_db, load_from_db
import matplotlib.pyplot as plt
from datetime import datetime
import os

# Global list of holdings
holdings = []

def launch_menu():
    while True:
        print("\n====== Welcome to Stock Pro ======")
        print("1. Manage Portfolio")
        print("2. Add Daily Trading Info")
        print("3. Display Stock Summary")
        print("4. Visualize Price Chart")
        print("5. Data Tools (Save, Load, Fetch, Import)")
        print("6. Quit")
        option = input("Enter your choice: ")

        if option == "1":
            portfolio_menu()
        elif option == "2":
            enter_trading_data()
        elif option == "3":
            print_summary()
        elif option == "4":
            draw_price_chart()
        elif option == "5":
            data_tools_menu()
        elif option == "6":
            print("Thank you for using Stock Pro!")
            break
        else:
            print("Invalid selection. Try again.")

def portfolio_menu():
    while True:
        print("\n-- Portfolio Management --")
        print("1. Add Stock")
        print("2. Modify Shares")
        print("3. Remove Stock")
        print("4. View All Holdings")
        print("0. Back to Main Menu")
        selection = input("Choose an option: ")

        if selection == "1":
            add_to_portfolio()
        elif selection == "2":
            change_shares()
        elif selection == "3":
            remove_stock()
        elif selection == "4":
            list_holdings()
        elif selection == "0":
            break
        else:
            print("Invalid input.")

def add_to_portfolio():
    ticker = input("Enter stock symbol: ").strip().upper()
    company = input("Enter company name: ").strip()
    try:
        qty = float(input("Enter shares held: ").strip())
        item = Stock(ticker, company, qty)
        holdings.append(item)
        print(f"{ticker} - {company} added.")
    except Exception as e:
        print(f"Error: {e}")

def change_shares():
    ticker = input("Enter stock symbol: ").strip().upper()
    item = locate_stock(ticker)
    if not item:
        print("Stock not found.")
        return
    action = input("Buy or Sell?: ").strip().lower()
    try:
        amount = float(input("Enter share quantity: "))
        if action == "buy":
            item.buy_shares(amount)
        elif action == "sell":
            item.sell_shares(amount)
        else:
            print("Invalid action.")
    except:
        print("Invalid input.")

def remove_stock():
    ticker = input("Symbol to delete: ").strip().upper()
    global holdings
    holdings = [s for s in holdings if s.symbol != ticker]
    print(f"{ticker} removed.")

def list_holdings():
    print(f"\n{'SYMBOL':<10} {'COMPANY':<25} {'SHARES':<10}")
    for stock in holdings:
        print(f"{stock.symbol:<10} {stock.name:<25} {stock.shares:<10}")
    input("Press Enter to return...")

def enter_trading_data():
    ticker = input("Which stock to update?: ").strip().upper()
    item = locate_stock(ticker)
    if not item:
        print("Stock not found.")
        return
    print("Input data (mm/dd/yy, closing price, volume). Leave blank to end.")
    while True:
        row = input("Enter record: ").strip()
        if not row:
            break
        try:
            date_str, price, volume = [x.strip() for x in row.split(",")]
            fmt_date = datetime.strptime(date_str, "%m/%d/%y").strftime("%b %d, %Y")
            item.add_data(DailyData(fmt_date, price, volume))
        except Exception as e:
            print(f"Invalid format: {e}")

def print_summary():
    for stock in holdings:
        print(f"\n{stock.symbol} - {stock.name} - {stock.shares} shares")
        if not stock.history:
            print("  No historical data.")
        for d in stock.history:
            print(f"  {d.date} | Close: ${d.close_price:.2f} | Volume: {d.volume}")
    input("\nPress Enter to continue...")

def draw_price_chart():
    for stock in holdings:
        if not stock.history:
            continue
        sorted_data = sorted(stock.history, key=lambda x: datetime.strptime(x.date, "%b %d, %Y"))
        dates = [datetime.strptime(d.date, "%b %d, %Y") for d in sorted_data]
        prices = [d.close_price for d in sorted_data]
        plt.plot(dates, prices, label=f"{stock.symbol} ({stock.name})")
    plt.title("Historical Stock Prices")
    plt.xlabel("Date")
    plt.ylabel("Close Price")
    plt.legend()
    plt.tight_layout()
    plt.gcf().autofmt_xdate()
    plt.show()

def data_tools_menu():
    global holdings
    while True:
        print("\n-- Data Utilities --")
        print("1. Save Portfolio")
        print("2. Load Portfolio")
        print("3. Fetch Online Prices")
        print("4. Import from CSV")
        print("0. Back to Main Menu")
        option = input("Choose option: ")

        if option == "1":
            save_to_db(holdings)
            print("Saved to database.")
        elif option == "2":
            holdings = load_from_db()
            print("Loaded from database.")
        elif option == "3":
            from_date = input("Start Date (m/d/yy): ")
            to_date = input("End Date (m/d/yy): ")
            retrieve_stock_web(from_date, to_date, holdings)
            print("Web data retrieved.")
        elif option == "4":
            ticker = input("Enter stock symbol: ").strip().upper()
            file_path = input("Full path to CSV: ")
            if os.path.exists(file_path):
                import_stock_web_csv(holdings, ticker, file_path)
                print("CSV successfully imported.")
            else:
                print("File not found.")
        elif option == "0":
            break
        else:
            print("Invalid choice.")

# Helper to locate stock object
def locate_stock(ticker):
    return next((s for s in holdings if s.symbol.upper() == ticker.upper()), None)

if __name__ == "__main__":
    launch_menu()
