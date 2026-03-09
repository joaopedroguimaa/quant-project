# api/backtest.py
import sys
import os
import pandas as pd
import numpy as np
import sqlite3
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from factors.returns import AnaliseConsolidada

class SimuladorCarteira:
    def __init__(self, saldo_inicial=100000, db_path="database/acoes.db"):
        self.saldo_inicial = saldo_inicial
        self.saldo_disponivel = saldo_inicial
        self.db_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), db_path)
        self.carteira = {}
        self.historico_carteira = []
        self.historico_trades = []
        self.composicao_carteira = []
    
    def get_preco_ativo(self, ticker, data):
        """Busca o preço de fechamento de um ativo em uma data específica"""
        conn = sqlite3.connect(self.db_path)
        query = """
            SELECT close FROM precos_acoes 
            WHERE ticker = ? AND date <= ? 
            ORDER BY date DESC LIMIT 1
        """
        df = pd.read_sql_query(query, conn, params=[ticker, data.strftime('%Y-%m-%d')])
        conn.close()
        
        if df.empty:
            return None
        return df['close'].iloc[0]
    
    def get_precos_carteira(self, data):
        """Calcula o valor total da carteira em uma data específica"""
        valor_total = 0
        posicoes = []
        
        for ticker, info in self.carteira.items():
            preco_atual = self.get_preco_ativo(ticker, data)
            if preco_atual is not None:
                valor_posicao = info['quantidade'] * preco_atual
                valor_total += valor_posicao
                posicoes.append({
                    'ticker': ticker,
                    'quantidade': info['quantidade'],
                    'preco_medio': info['preco_medio'],
                    'preco_atual': preco_atual,
                    'valor': valor_posicao,
                    'retorno': (preco_atual / info['preco_medio'] - 1) * 100 if info['preco_medio'] > 0 else 0
                })
        
        return valor_total, posicoes
    
    def executar_rebalanceamento(self, data, recomendacoes, taxa_operacional=0.005):
        """Rebalanceia a carteira baseado nas novas recomendações"""
        print(f"\n{'='*60}")
        print(f"REBALANCEAMENTO - {data.strftime('%d/%m/%Y')}")
        print(f"{'='*60}")
        
        # Filtrar apenas recomendações com score >= 60
        ativos_recomendados = recomendacoes[recomendacoes['score_final'] >= 60].copy()
        
        if ativos_recomendados.empty:
            print("Nenhum ativo recomendado para compra neste período.")
            return
        
        # Normalizar scores para definir alocação
        ativos_recomendados['peso'] = ativos_recomendados['score_final'] / ativos_recomendados['score_final'].sum()
        
        print(f"Ativos recomendados ({len(ativos_recomendados)}):")
        for _, ativo in ativos_recomendados.iterrows():
            print(f"  {ativo['ticker']}: Score {ativo['score_final']:.1f} | Peso {ativo['peso']:.2%}")
        
        # Calcular valor atual da carteira
        valor_carteira_atual, posicoes_atuais = self.get_precos_carteira(data)
        saldo_total = self.saldo_disponivel + valor_carteira_atual
        
        print(f"\nSituação antes do rebalanceamento:")
        print(f"  Saldo disponível: R$ {self.saldo_disponivel:,.2f}")
        print(f"  Valor em ações: R$ {valor_carteira_atual:,.2f}")
        print(f"  Patrimônio total: R$ {saldo_total:,.2f}")
        
        # VENDER: ativos que não estão mais recomendados
        tickers_atuais = set(self.carteira.keys())
        tickers_recomendados = set(ativos_recomendados['ticker'])
        tickers_vender = tickers_atuais - tickers_recomendados
        
        for ticker in tickers_vender:
            info = self.carteira[ticker]
            preco_venda = self.get_preco_ativo(ticker, data)
            
            if preco_venda is not None:
                valor_venda = info['quantidade'] * preco_venda
                custo_venda = valor_venda * taxa_operacional
                self.saldo_disponivel += (valor_venda - custo_venda)
                
                self.historico_trades.append({
                    'data': data,
                    'ticker': ticker,
                    'operacao': 'VENDA',
                    'quantidade': info['quantidade'],
                    'preco': preco_venda,
                    'valor': valor_venda,
                    'taxas': custo_venda
                })
                
                print(f"  VENDA: {ticker} - {info['quantidade']} ações a R$ {preco_venda:.2f} = R$ {valor_venda:,.2f}")
        
        # Atualizar carteira (remover vendidos)
        self.carteira = {t: i for t, i in self.carteira.items() if t in tickers_recomendados}
        
        # COMPRAR: alocar saldo disponível entre os recomendados
        if self.saldo_disponivel > 0 and not ativos_recomendados.empty:
            ativos_recomendados['valor_investir'] = ativos_recomendados['peso'] * self.saldo_disponivel
            
            for _, ativo in ativos_recomendados.iterrows():
                ticker = ativo['ticker']
                valor_investir = ativo['valor_investir']
                preco_compra = self.get_preco_ativo(ticker, data)
                
                if preco_compra is not None and valor_investir > 0:
                    quantidade = int((valor_investir * (1 - taxa_operacional)) / preco_compra)
                    
                    if quantidade > 0:
                        valor_efetivo = quantidade * preco_compra
                        taxas = valor_efetivo * taxa_operacional
                        
                        self.saldo_disponivel -= (valor_efetivo + taxas)
                        
                        if ticker in self.carteira:
                            info = self.carteira[ticker]
                            novo_preco_medio = (info['quantidade'] * info['preco_medio'] + valor_efetivo) / (info['quantidade'] + quantidade)
                            info['quantidade'] += quantidade
                            info['preco_medio'] = novo_preco_medio
                        else:
                            self.carteira[ticker] = {
                                'quantidade': quantidade,
                                'preco_medio': preco_compra
                            }
                        
                        self.historico_trades.append({
                            'data': data,
                            'ticker': ticker,
                            'operacao': 'COMPRA',
                            'quantidade': quantidade,
                            'preco': preco_compra,
                            'valor': valor_efetivo,
                            'taxas': taxas
                        })
                        
                        print(f"  COMPRA: {ticker} - {quantidade} ações a R$ {preco_compra:.2f} = R$ {valor_efetivo:,.2f}")
        
        # Calcular nova posição
        novo_valor_carteira, novas_posicoes = self.get_precos_carteira(data)
        novo_patrimonio = self.saldo_disponivel + novo_valor_carteira
        
        print(f"\nSituação após rebalanceamento:")
        print(f"  Saldo disponível: R$ {self.saldo_disponivel:,.2f}")
        print(f"  Valor em ações: R$ {novo_valor_carteira:,.2f}")
        print(f"  Patrimônio total: R$ {novo_patrimonio:,.2f}")
        
        # Registrar histórico
        self.historico_carteira.append({
            'data': data,
            'saldo_disponivel': self.saldo_disponivel,
            'valor_acoes': novo_valor_carteira,
            'patrimonio_total': novo_patrimonio,
            'num_ativos': len(self.carteira),
            'retorno_acumulado': ((novo_patrimonio / self.saldo_inicial) - 1) * 100
        })
        
        # Registrar histórico da composição da carteira
        for ticker, info in self.carteira.items():
            preco_atual = self.get_preco_ativo(ticker, data)
            if preco_atual is not None:
                valor_posicao = info['quantidade'] * preco_atual
                peso = valor_posicao / novo_patrimonio * 100 if novo_patrimonio > 0 else 0
                
                self.composicao_carteira.append({
                    'data': data,
                    'ticker': ticker,
                    'quantidade': info['quantidade'],
                    'preco_medio': info['preco_medio'],
                    'preco_atual': preco_atual,
                    'valor_total': valor_posicao,
                    'peso_percentual': peso
                })
    
    def simular(self, data_inicio, data_fim, intervalo_dias=30):
        """Executa a simulação completa"""
        data_inicio = pd.to_datetime(data_inicio)
        data_fim = pd.to_datetime(data_fim)
        
        print(f"\n{'='*70}")
        print(f"INICIANDO SIMULAÇÃO DE CARTEIRA")
        print(f"{'='*70}")
        print(f"Saldo inicial: R$ {self.saldo_inicial:,.2f}")
        print(f"Período: {data_inicio.strftime('%d/%m/%Y')} a {data_fim.strftime('%d/%m/%Y')}")
        
        # Gerar datas de rebalanceamento
        datas_rebalanceamento = pd.date_range(start=data_inicio, end=data_fim, freq=f'{intervalo_dias}D')
        
        for i, data_reb in enumerate(datas_rebalanceamento):
            print(f"\n--- Processando rebalanceamento {i+1}/{len(datas_rebalanceamento)} ---")
            
            try:
                # Criar instância da análise
                analise = AnaliseConsolidada(self.db_path)
                
                # Executar análises com data de corte
                analise.executar_todas_analises(data_corte=data_reb)
                
                # Consolidar resultados
                ranking = analise.consolidar_resultados()
                
                if ranking is not None and not ranking.empty:
                    self.executar_rebalanceamento(data_reb, ranking)
                else:
                    print(f"Sem dados suficientes para {data_reb.strftime('%d/%m/%Y')}")
                    
            except Exception as e:
                print(f"Erro no rebalanceamento de {data_reb.strftime('%d/%m/%Y')}: {e}")
                continue
        
        # Gerar relatório final
        self.gerar_relatorio_final()
    
    def gerar_relatorio_final(self):
        """Gera relatório final"""
        if not self.historico_carteira:
            print("Nenhum dado histórico para gerar relatório")
            return
        
        df_historico = pd.DataFrame(self.historico_carteira)
        
        # Calcular evolução do Ibovespa para comparação
        try:
            import yfinance as yf
            print("\nBaixando histórico do Ibovespa para comparação...")
            data_ini = df_historico['data'].min() - timedelta(days=10)
            data_fim = df_historico['data'].max() + timedelta(days=5)
            
            df_ibov = yf.download("^BVSP", start=data_ini.strftime('%Y-%m-%d'), end=data_fim.strftime('%Y-%m-%d'), progress=False)
            
            if not df_ibov.empty:
                if df_ibov.index.tz is not None:
                    df_ibov.index = df_ibov.index.tz_localize(None)
                
                ibov_close = df_ibov['Close']
                if isinstance(ibov_close, pd.DataFrame):
                    ibov_close = ibov_close.iloc[:, 0]
                
                # Para cada data de rebalanceamento, buscar o preço anterior mais próximo
                ibov_precos = []
                for dt in df_historico['data']:
                    idx = ibov_close.index[ibov_close.index <= dt]
                    if len(idx) > 0:
                        ibov_precos.append(float(ibov_close.loc[idx[-1]]))
                    else:
                        ibov_precos.append(np.nan)
                
                df_historico['ibov_pontos'] = ibov_precos
                df_historico['ibov_pontos'] = df_historico['ibov_pontos'].ffill().bfill()
                
                ibov_inicial = df_historico['ibov_pontos'].iloc[0]
                df_historico['ibov_retorno_acumulado'] = ((df_historico['ibov_pontos'] / ibov_inicial) - 1) * 100
        except Exception as e:
            print(f"Não foi possível calcular o Ibovespa: {e}")
            
        print(f"\n{'='*70}")
        print(f"RELATÓRIO FINAL DA SIMULAÇÃO")
        print(f"{'='*70}")
        
        patrimonio_final = df_historico.iloc[-1]['patrimonio_total']
        retorno_total = df_historico.iloc[-1]['retorno_acumulado']
        
        print(f"\nMétricas Gerais:")
        print(f"  Patrimônio Inicial: R$ {self.saldo_inicial:,.2f}")
        print(f"  Patrimônio Final: R$ {patrimonio_final:,.2f}")
        print(f"  Retorno Total: {retorno_total:.2f}%")
        
        # Salvar relatório
        self.salvar_relatorio_excel(df_historico)
    
    def salvar_relatorio_excel(self, df_historico, filename="reports/backtest_resultado.xlsx"):
        """Salva resultados em Excel"""
        # Criar pasta reports se não existir
        reports_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "reports")
        os.makedirs(reports_dir, exist_ok=True)
        
        # Opcional: Adicionar timestamp ao nome do arquivo se desejar manter histórico de vários backtests
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename_with_ts = filename.replace('.xlsx', f'_{timestamp}.xlsx')
        filepath = os.path.join(reports_dir, os.path.basename(filename_with_ts))
        
        try:
            with pd.ExcelWriter(filepath, engine='openpyxl') as writer:
                # 1. Evolução do patrimônio
                df_historico.to_excel(writer, sheet_name='Evolução', index=False)
                
                # 2. Trades realizados
                if self.historico_trades:
                    df_trades = pd.DataFrame(self.historico_trades)
                    df_trades.to_excel(writer, sheet_name='Trades', index=False)
                
                # 3. Composição mensal da carteira
                if hasattr(self, 'composicao_carteira') and self.composicao_carteira:
                    df_composicao = pd.DataFrame(self.composicao_carteira)
                    df_composicao.to_excel(writer, sheet_name='Composicao_Mensal', index=False)
                
                # 4. Retornos mensais
                if len(df_historico) > 1:
                    df_historico_copy = df_historico.copy()
                    df_historico_copy['mes'] = df_historico_copy['data'].dt.strftime('%m/%Y')
                    df_historico_copy['retorno_mensal_perc'] = df_historico_copy['patrimonio_total'].pct_change() * 100
                    df_historico_copy['retorno_mensal_perc'] = df_historico_copy['retorno_mensal_perc'].fillna(0)
                    
                    cols_retornos = ['data', 'mes', 'patrimonio_total', 'retorno_mensal_perc', 'retorno_acumulado']
                    
                    if 'ibov_pontos' in df_historico_copy.columns:
                        df_historico_copy['ibov_retorno_mensal_perc'] = df_historico_copy['ibov_pontos'].pct_change() * 100
                        df_historico_copy['ibov_retorno_mensal_perc'] = df_historico_copy['ibov_retorno_mensal_perc'].fillna(0)
                        cols_retornos.extend(['ibov_pontos', 'ibov_retorno_mensal_perc', 'ibov_retorno_acumulado'])
                        
                    df_retornos = df_historico_copy[cols_retornos]
                    df_retornos.to_excel(writer, sheet_name='Retornos_Mensais', index=False)
                
                # 5. Resumo
                resumo_data = {
                    'Métrica': ['Saldo Inicial', 'Saldo Final', 'Retorno Total', 'Nº Rebalanceamentos'],
                    'Valor': [
                        f"R$ {self.saldo_inicial:,.2f}",
                        f"R$ {df_historico.iloc[-1]['patrimonio_total']:,.2f}" if not df_historico.empty else "R$ 0.00",
                        f"{df_historico.iloc[-1]['retorno_acumulado']:.2f}%" if not df_historico.empty else "0.00%",
                        len(df_historico)
                    ]
                }
                
                if 'ibov_retorno_acumulado' in df_historico.columns and not df_historico.empty:
                    resumo_data['Métrica'].extend([
                        'IBOV Inicial (pontos)',
                        'IBOV Final (pontos)',
                        'Retorno IBOV Total',
                        'Alpha (Carteira vs IBOV)'
                    ])
                    ibov_ini_pt = df_historico.iloc[0]['ibov_pontos']
                    ibov_fim_pt = df_historico.iloc[-1]['ibov_pontos']
                    ibov_ret = df_historico.iloc[-1]['ibov_retorno_acumulado']
                    alpha = df_historico.iloc[-1]['retorno_acumulado'] - ibov_ret
                    
                    resumo_data['Valor'].extend([
                        f"{ibov_ini_pt:,.0f}",
                        f"{ibov_fim_pt:,.0f}",
                        f"{ibov_ret:.2f}%",
                        f"{alpha:.2f} p.p."
                    ])
                    
                resumo = pd.DataFrame(resumo_data)
                resumo.to_excel(writer, sheet_name='Resumo', index=False)
            
            print(f"\nRelatório salvo com sucesso em: {filepath}")
        except Exception as e:
            print(f"Erro ao salvar relatório em Excel: {e}")

def executar_backtest(saldo_inicial=100000, data_inicio="2023-01-01", data_fim="2024-01-01"):
    """Função principal para executar o backtest"""
    simulador = SimuladorCarteira(saldo_inicial=saldo_inicial)
    simulador.simular(data_inicio=data_inicio, data_fim=data_fim)
    return simulador, simulador.historico_carteira

if __name__ == "__main__":
    print("SIMULADOR DE CARTEIRA COM REBALANCEAMENTO MENSAL")
    print("-" * 50)
    
    # Parâmetros da simulação
    SALDO_INICIAL = 100000
    DATA_INICIO = "2023-01-01"
    DATA_FIM = "2024-01-01"
    
    # Executar backtest
    simulador, historico = executar_backtest(
        saldo_inicial=SALDO_INICIAL,
        data_inicio=DATA_INICIO,
        data_fim=DATA_FIM
    )