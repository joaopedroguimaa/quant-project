# factors/volatility.py
import sqlite3
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

def get_data_volatility(db_path="database/acoes.db", tickers=None, data_corte=None):
    """
    Args:
        db_path: caminho do arquivo .db
        tickers: lista de tickers (None = todos)
        data_corte: data limite para buscar os dados (formato 'YYYY-MM-DD' ou datetime)
    
    Returns:
        DataFrame com colunas: ticker, date, close, high, low
    """

    conn = sqlite3.connect(db_path)
    
    query = """
        SELECT ticker, date, close, high, low
        FROM precos_acoes
        WHERE 1=1
    """
    
    params = []
    
    # Adicionar filtro de data_corte se fornecido
    if data_corte:
        # Converter para string se for datetime
        if hasattr(data_corte, 'strftime'):
            data_corte_str = data_corte.strftime('%Y-%m-%d')
        else:
            data_corte_str = str(data_corte)
        query += f" AND date <= ?"
        params.append(data_corte_str)
    
    # Adicionar filtro de tickers se fornecido
    if tickers:
        placeholders = ','.join(['?'] * len(tickers))
        query += f" AND ticker IN ({placeholders})"
        params.extend(tickers)
    
    query += " ORDER BY ticker, date"
    
    df = pd.read_sql_query(query, conn, params=params)
    conn.close()

    return df

def ranking_volatility(df):
    # 1. Calcular Log-Retornos
    df['log_ret'] = df.groupby('ticker')['close'].transform(lambda x: np.log(x / x.shift(1)))
    
    # 2. Volatilidade Histórica
    df['vol_historica'] = df.groupby('ticker')['log_ret'].transform(
        lambda x: x.rolling(window=21).std() * np.sqrt(252)
    )
    
    # 3. Volatilidade de Parkinson
    def parkinson(h, l):
        return np.sqrt(1 / (4 * np.log(2)) * (np.log(h / l)**2))
    
    df['vol_parkinson'] = parkinson(df['high'], df['low'])
    df['vol_park_media'] = df.groupby('ticker')['vol_parkinson'].transform(
        lambda x: x.rolling(window=21).mean() * np.sqrt(252)
    )

    # 4. Ranking (Última Data)
    ultima_data = df['date'].max()
    ranking = df[df['date'] == ultima_data].copy()
    
    # Score de Risco: 100 é o ativo MAIS VOLÁTIL
    ranking['risco_score'] = ranking['vol_historica'].rank(pct=True) * 100
    
    return ranking.sort_values(by='risco_score', ascending=True)[
        ['ticker', 'vol_historica', 'vol_park_media', 'risco_score']
    ]