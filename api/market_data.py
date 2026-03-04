import yfinance as yf
import pandas as pd 


class DataFetcher:
    def __init__(self):
        self.lista_tickers = ["AAPL", "GOOGL", "MSFT"]
        self.period = "5d"
        self.interval = "1d"

    def get_symbols(self):
        return self.lista_tickers
    
    def set_interval(self, period=None, interval=None):
        period = period or self.period
        interval = interval or self.interval

        dados = yf.download(self.lista_tickers, period=period, interval=interval)
        return dados
    
    def get_data(self):
        dados = self.set_interval()
        print(dados['Close'].head())
        return dados
    
fetcher = DataFetcher()
fetcher.get_data()