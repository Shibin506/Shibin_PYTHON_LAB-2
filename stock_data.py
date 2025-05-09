from stock_class import Equity, HistoricalRecord
import yfinance as yf
from datetime import datetime
import csv
import os


def retrieve_stock_web(date_from, date_to, portfolio):
    count = 0
    try:
        start_date = datetime.strptime(date_from, "%m/%d/%Y").strftime("%Y-%m-%d")
        end_date = datetime.strptime(date_to, "%m/%d/%Y").strftime("%Y-%m-%d")
    except:
        print("❌ Invalid date format. Use MM/DD/YYYY.")
        return 0

    for stock in portfolio:
        try:
            symbol = stock.symbol.strip().upper()
            print(f"📥 Downloading {symbol} from {start_date} to {end_date}")
            data = yf.download(symbol, start=start_date, end=end_date, progress=False)

            if data.empty:
                print(f"⚠️ No data for {symbol}")
                continue

            for idx, row in data.iterrows():
                try:
                    date = idx.strftime("%b %d, %Y")
                    close = round(row['Close'], 2)
                    volume = int(row['Volume'])
                    record = HistoricalRecord(date, close, volume)

                    if hasattr(stock, 'add_data'):
                        stock.add_data(record)
                    elif hasattr(stock, 'records'):
                        stock.records.append(record)
                    else:
                        print(f"⚠️ Stock object for {symbol} missing data method or list")

                    count += 1
                    print(f"✔️ {symbol} - {date}: Close = {close}, Volume = {volume}")
                except Exception as e:
                    print(f"⚠️ Failed parsing a row for {symbol}: {e}")
        except Exception as e:
            print(f"❌ Error retrieving {symbol}: {e}")
    return count


def import_stock_web_csv(portfolio, symbol, filename):
    stock = next((s for s in portfolio if s.symbol == symbol), None)
    if not stock:
        print(f"⚠️ Stock {symbol} not found in portfolio. Creating new entry.")
        stock = Equity(symbol, f"{symbol} (Imported)", 0)
        portfolio.append(stock)

    if not os.path.exists(filename):
        print("❌ File not found.")
        return

    with open(filename, newline='', encoding='utf-8-sig') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            try:
                date = row['Date'].strip()
                close = float(row['Close'])
                volume = int(row['Volume'])
                formatted_date = datetime.strptime(date, "%m/%d/%Y").strftime("%b %d, %Y")
                record = HistoricalRecord(formatted_date, close, volume)
                stock.records.append(record)
            except Exception as e:
                print(f"⚠️ Error parsing row: {e}")

    print("✅ CSV successfully imported.")
