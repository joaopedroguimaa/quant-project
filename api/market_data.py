import yfinance as yf
import pandas as pd 


class DataFetcher:
    def __init__(self):
        self.lista_tickers = [ "MSFT"]
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
    
fetcher = DataFetcher()

dados_brutos = fetcher.get_data()

dados_linha = fetcher.data_to_rows(dados_brutos)

print (dados_linha)