# analise_momentum.py
import sqlite3
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

def get_data_momentum(db_path="database/acoes.db", tickers=None, min_days=273, data_corte=None):
    """
    Args:
        db_path: caminho do arquivo .db
        tickers: lista de tickers (None = todos)
        min_days: mínimo de dias necessários para cálculo
        data_corte: data limite para buscar os dados (formato 'YYYY-MM-DD' ou datetime)
    
    Returns:
        DataFrame com colunas: ticker, date, close
    """

    conn = sqlite3.connect(db_path)
    
    query = """
        SELECT ticker, date, close
        FROM precos_acoes
        WHERE 1=1
    """
    
    params = []
    
   
    if data_corte:
      
        if hasattr(data_corte, 'strftime'):
            data_corte_str = data_corte.strftime('%Y-%m-%d')
        else:
            data_corte_str = str(data_corte)
        query += f" AND date <= ?"
        params.append(data_corte_str)

    if tickers:
        placeholders = ','.join(['?'] * len(tickers))
        query += f" AND ticker IN ({placeholders})"
        params.extend(tickers)
    
    query += " ORDER BY ticker, date"
    

    df = pd.read_sql_query(query, conn, params=params)
    conn.close()
    

    tickers_validos = []
    for ticker in df['ticker'].unique():
        dados_ticker = df[df['ticker'] == ticker]
        if len(dados_ticker) >= min_days:
            tickers_validos.append(ticker)
        else:
            print(f"AVISO: {ticker}: apenas {len(dados_ticker)} dias (mínimo {min_days}) - será ignorado")
  
    if tickers_validos:
        df = df[df['ticker'].isin(tickers_validos)]
    else:
        return pd.DataFrame()
    
    return df

def ranking_momentum(df):
    """
    df deve conter as colunas: 'ticker', 'date', 'close'
    O ideal é que o df esteja ordenado por data.
    """
    

    df = df.copy()
    
    # Garantir que está ordenado
    df = df.sort_values(['ticker', 'date'])

    print("   • Calculando retorno de 12 meses...")
    df['retorno_12m'] = df.groupby('ticker')['close'].transform(
        lambda x: x.shift(21) / x.shift(252) - 1
    )
    

    print("   • Calculando volatilidade...")
    def calcular_vol(x):
        return x.pct_change().std() * np.sqrt(252)
    
    df['volatilidade_anual'] = df.groupby('ticker')['close'].transform(
        lambda x: x.rolling(window=252).apply(calcular_vol)
    )
    


    df['momentum_score'] = df['retorno_12m'] / df['volatilidade_anual']
    

    ultima_data = df['date'].max()
    print(f"   • Última data disponível: {ultima_data}")
    
    ranking = df[df['date'] == ultima_data].copy()
    

    ranking = ranking.dropna(subset=['momentum_score', 'retorno_12m'])

    ranking = ranking.sort_values(by='momentum_score', ascending=False)
    
    print(f"Ranking calculado com {len(ranking)} tickers")
    
    return ranking[['ticker', 'retorno_12m', 'momentum_score']]
