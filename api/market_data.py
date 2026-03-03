#https://lucidarium.com.br/como-coletar-dados-de-acoes-e-cripto-com-yfinance-passo-a-passo/

import yfinance as yf
import pandas as pd 

lista_tickers = ["AAPL", "GOOGL", "MSFT"]


dados_multiplos = yf.download(lista_tickers, period="5d", interval="1d")

print(dados_multiplos['Close'].head())
