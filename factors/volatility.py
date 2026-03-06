import sqlite3
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

def get_data_volatility(db_path="database/acoes.db", tickers=None):
    """
    
    Args:
        db_path: caminho do arquivo .db
        tickers: lista de tickers (None = todos)
        dias_necessarios: mínimo de dias necessários para cálculo
    
    Returns:
        DataFrame com colunas: ticker, date, close, high, low
    """

    conn = sqlite3.connect(db_path)
    

    query = """
        SELECT ticker, date, close, high, low
        FROM precos_acoes
        WHERE 1=1
    """
    

    if tickers:
        placeholders = ','.join(['?'] * len(tickers))
        query += f" AND ticker IN ({placeholders})"
        params = tickers
    else:
        params = []
    

    query += " ORDER BY ticker, date"
    

    df = pd.read_sql_query(query, conn, params=params)
    conn.close()

    return df


def ranking_volatility(df):
    # 1. Calcular Log-Retornos
    df['log_ret'] = df.groupby('ticker')['close'].transform(lambda x: np.log(x / x.shift(1)))
    
    # 2. Volatilidade Histórica (Janela de 21 dias - 1 mês)
    # Calculamos o desvio padrão e anualizamos
    df['vol_historica'] = df.groupby('ticker')['log_ret'].transform(
        lambda x: x.rolling(window=21).std() * np.sqrt(252)
    )
    
    # 3. Volatilidade de Parkinson (Usa High e Low)
    # Captura o 'estresse' dentro do dia
    def parkinson(h, l):
        return np.sqrt(1 / (4 * np.log(2)) * (np.log(h / l)**2))
    
    df['vol_parkinson'] = parkinson(df['high'], df['low'])
    df['vol_park_media'] = df.groupby('ticker')['vol_parkinson'].transform(
        lambda x: x.rolling(window=21).mean() * np.sqrt(252)
    )

    # 4. Ranking (Última Data)
    ultima_data = df['date'].max()
    ranking = df[df['date'] == ultima_data].copy()
    
    # Score de Risco: 100 é o ativo MAIS VOLÁTIL (mais perigoso)
    ranking['risco_score'] = ranking['vol_historica'].rank(pct=True) * 100
    
    return ranking.sort_values(by='risco_score', ascending=True)[
        ['ticker', 'vol_historica', 'vol_park_media', 'risco_score']
    ]