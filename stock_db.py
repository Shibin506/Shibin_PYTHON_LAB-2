import sqlite3
from stock_models import Stock, DailyData

DB_NAME = "stock_data.db"

def save_to_db(portfolio):
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()

    # Create tables
    cur.execute("DROP TABLE IF EXISTS stocks")
    cur.execute("DROP TABLE IF EXISTS history")

    cur.execute("""
        CREATE TABLE stocks (
            symbol TEXT PRIMARY KEY,
            name TEXT,
            shares REAL
        )
    """)

    cur.execute("""
        CREATE TABLE history (
            symbol TEXT,
            date TEXT,
            close_price REAL,
            volume INTEGER,
            FOREIGN KEY(symbol) REFERENCES stocks(symbol)
        )
    """)

    # Insert stock data
    for stock in portfolio:
        cur.execute("INSERT INTO stocks VALUES (?, ?, ?)", (stock.symbol, stock.name, stock.shares))
        for d in stock.history:
            cur.execute("INSERT INTO history VALUES (?, ?, ?, ?)", (stock.symbol, d.date, d.close_price, d.volume))

    conn.commit()
    conn.close()

def load_from_db():
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()

    portfolio = []
    cur.execute("SELECT * FROM stocks")
    rows = cur.fetchall()
    for row in rows:
        symbol, name, shares = row
        stock = Stock(symbol, name, shares)

        cur.execute("SELECT date, close_price, volume FROM history WHERE symbol = ?", (symbol,))
        history_rows = cur.fetchall()
        for h in history_rows:
            date, close, volume = h
            stock.add_data(DailyData(date, close, volume))

        portfolio.append(stock)

    conn.close()
    return portfolio
