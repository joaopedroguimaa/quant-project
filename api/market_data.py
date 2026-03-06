import yfinance as yf
import pandas as pd 
from database.connection import DataBase 

class DataFetcher:
    def __init__(self):
        self.lista_tickers = [ "MSFT"]
        self.period = "1y"
        self.interval = "1d"
        self.db = DataBase()

    def get_symbols(self):
        return self.lista_tickers
    
    def set_interval(self, period=None, interval=None):
        period = period or self.period
        interval = interval or self.interval

        dados = yf.download(self.lista_tickers, period=period, interval=interval)
        return dados
    
    def get_data(self):
        dados = self.set_interval()
        print(dados.head())
        print("\nColunas:", dados.columns)
        print("\nTipo:", type(dados))
        return dados
    
    def data_to_rows(self, dados):
        linhas = []

        tickers = dados.columns.get_level_values(1).unique()
        for data in dados.index:
            for ticker in tickers:
                linha = {
                    'date' : data.strftime('%Y-%m-%d'),
                    'ticker': ticker,
                    'open': float(dados['Open'][ticker][data]),
                    'high': float(dados['High'][ticker][data]),
                    'low': float(dados['Low'][ticker][data]),
                    'close': float(dados['Close'][ticker][data]),
                    'volume': int(dados['Volume'][ticker][data])
                }
                linhas.append(linha)
        return pd.DataFrame(linhas)
    
    def save_data(self):
        dados_brutos = self.set_interval()
        dados_linha =  self.data_to_rows(dados_brutos)
        dados_novos = self.db.insert_dados(dados_linha)
        return dados_novos

fetcher = DataFetcher()

dados_brutos = fetcher.get_data()

dados_linha = fetcher.data_to_rows(dados_brutos)

print (dados_linha)