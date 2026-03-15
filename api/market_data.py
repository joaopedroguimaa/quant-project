import yfinance as yf
import pandas as pd 
from database.connection import DataBase 

class DataFetcher:
    def __init__(self):
        self.lista_tickers = [
            "ITUB4.SA", "BBDC4.SA", "VALE3.SA", "PETR4.SA", "GGBR4.SA", 
            "BPAC11.SA", "B3SA3.SA", "PETR3.SA", "BBAS3.SA", "SANB11.SA", 
            "CSNA3.SA", "ABEV3.SA"

        ]
        self.period = "5y"
        self.interval = "1d"
        self.db = DataBase()

    def get_symbols(self):
        return self.lista_tickers
    
    def set_interval(self, period=None, interval=None):
        period = period or self.period
        interval = interval or self.interval

        print(f"Baixando dados para {self.lista_tickers}...")
        dados = yf.download(self.lista_tickers, period=period, interval=interval)
        return dados
    
    
    
    def get_data(self):
        dados = self.set_interval()
        if not dados.empty:
            print(dados.head())
            print("\nColunas:", dados.columns)
            print("\nTipo:", type(dados))
        else:
            print("\nNenhum dado recuperado (possível rate limit do Yahoo Finance).")
        return dados
    
    def data_to_rows(self, dados):
        if dados is None or dados.empty:
            return pd.DataFrame()

        linhas = []

        tickers = dados.columns.get_level_values('Ticker').unique() if 'Ticker' in dados.columns.names else dados.columns.get_level_values(1).unique()
        for data in dados.index:
            for ticker in tickers:
                try:
                    linha = {
                        'date' : data.strftime('%Y-%m-%d'),
                        'ticker': ticker.replace('.SA', ''),
                        'open': float(dados['Open'][ticker][data]),
                        'high': float(dados['High'][ticker][data]),
                        'low': float(dados['Low'][ticker][data]),
                        'close': float(dados['Close'][ticker][data]),
                        'volume': int(dados['Volume'][ticker][data])
                    }
                    linhas.append(linha)
                except (KeyError, ValueError, TypeError):
                    continue
        return pd.DataFrame(linhas)
    

    
    
    def save_data(self):
        dados_brutos = self.set_interval()
        if dados_brutos is None or dados_brutos.empty:
            print("Nenhum dado válido para salvar.")
            return 0
            
        dados_linha = self.data_to_rows(dados_brutos)
        if dados_linha.empty:
             return 0

        dados_novos = self.db.insert_dados(dados_linha)
        self.db.export_to_excel()
        return dados_novos

