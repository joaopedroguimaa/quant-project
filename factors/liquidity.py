import sqlite3
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

def get_data_liquidity(db_path="database/acoes.db", tickers=None):
    """
    
    Args:
        db_path: caminho do arquivo .db
        tickers: lista de tickers (None = todos)
        dias_necessarios: mínimo de dias necessários para cálculo
    
    Returns:
        DataFrame com colunas: ticker, date, close
    """

    conn = sqlite3.connect(db_path)
    

    query = """
        SELECT ticker, date, close, volume
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


def calc_exit_metrics(df):

    df = df.copy()

    df = df.sort_values(['ticker', 'date'])

    # 1. Volume Financeiro Diário (Cash Volume)

    df['cash_volume'] = df['volume'] * df['close']


    # 2. ADTV - Média de 21 dias (Volume Financeiro Médio)
    # Essencial para saber o "tamanho da porta"
    df['adtv_21'] = df['cash_volume'].rolling(window=21).mean()

    # 3. Volatilidade Relativa (Proxy de risco de execução)
    # Se a vol é alta, o custo de saída aumenta
    df['std_ret'] = df['close'].pct_change().rolling(21).std()

    # 5. Estimativa de Impacto (Slippage Estimator)
    # Baseado no modelo de raiz quadrada de impacto de mercado
    # Representa a sensibilidade do preço ao volume
    df['market_impact'] = (df['std_ret'] * np.sqrt(1 / df['adtv_21'])) * 1e3
    
    return df

def ranking_liquidity(df):
    """
    df deve conter: 'ticker', 'date', 'close', 'volume'
    """
    # 1. Volume Financeiro e Médias
    df['financeiro'] = df['volume'] * df['close']
    df['adtv_21'] = df.groupby('ticker')['financeiro'].transform(lambda x: x.rolling(21).mean())
    
    # 2. Medir o Impacto no Preço (Amihud)
    # Quanto o preço mexe para cada real negociado? (Menor é melhor)
    df['retorno_abs'] = df.groupby('ticker')['close'].transform(lambda x: x.pct_change().abs())
    df['amihud'] = df['retorno_abs'] / df['financeiro']
    df['amihud_medio_21'] = df.groupby('ticker')['amihud'].transform(lambda x: x.rolling(21).mean())

    # 3. Filtrar a última data disponível
    ultima_data = df['date'].max()
    ranking = df[df['date'] == ultima_data].copy()

    # 4. Normalização para o Ranking (Score de 0 a 100)
    # Queremos ADTV ALTO e Amihud BAIXO
    ranking['score_volume'] = ranking['adtv_21'].rank(pct=True) * 100
    ranking['score_impacto'] = (1 - ranking['amihud_medio_21'].rank(pct=True)) * 100

    # 5. Score Final de Liquidez (Média dos dois)
    ranking['liquidez_score'] = (ranking['score_volume'] + ranking['score_impacto']) / 2
    
    return ranking.sort_values(by='liquidez_score', ascending=False)[
        ['ticker', 'adtv_21', 'amihud_medio_21', 'liquidez_score']
    ]