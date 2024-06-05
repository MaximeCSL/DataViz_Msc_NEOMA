import yfinance as yf
from datetime import datetime
import Fetch_excel_ptf

class AssetDataFetcher:
    def __init__(self, data, start_date="1900-01-01", end_date=None):
        if end_date is None:
            end_date = datetime.today().strftime('%Y-%m-%d')
        
        self.start_date = start_date
        self.end_date = end_date
        self.data = data

    def fetch_data(self):
        self.data = yf.download(self.data, start=self.start_date, end=self.end_date)["Close"]
        self.data.fillna(method='ffill', inplace=True)
        return self.data



