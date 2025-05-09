class HistoricalRecord:
    def __init__(self, date, close, volume):
        self.date = date
        self.close = float(close)
        self.volume = int(volume)

def log_record(msg):
    print(f"📌 {msg}")

class Equity:
    def __init__(self, symbol, name, shares):
        self.symbol = symbol.upper()
        self.name = name
        self.shares = float(shares)
        self.records = []  # List of HistoricalRecord objects

    def update_shares(self, delta):
        self.shares += delta

    def add_record(self, data):
        self.records.append(data)
        log_record(f"{data.date}: Close = {data.close}, Vol = {data.volume}")
