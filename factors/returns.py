# factors/returns.py
import pandas as pd
import numpy as np
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')


from factors.momentum import get_data_momentum, ranking_momentum
from factors.liquidity import get_data_liquidity, ranking_liquidity
from factors.volatility import get_data_volatility, ranking_volatility

class AnaliseConsolidada:
    """
    Classe que consolida as análises de Momentum, Liquidez e Volatilidade
    para gerar recomendações de investimento
    """
    
    def __init__(self, db_path="database/acoes.db"):
        self.db_path = db_path
        self.resultados = {}
        self.ranking_final = None
        
    def executar_todas_analises(self, tickers=None, data_corte=None):
        """
        Executa todas as análises com opção de data de corte
        """
        print(f"\nExecutando análises com data de corte: {data_corte}")
        
        # Momentum
        df_momentum = get_data_momentum(self.db_path, tickers, data_corte=data_corte)
        if not df_momentum.empty:
            self.resultados['momentum'] = ranking_momentum(df_momentum)
            print(f"    {len(self.resultados['momentum'])} ativos analisados (momentum)")
        else:
            print("    Sem dados para momentum")


        df_liquidity = get_data_liquidity(self.db_path, tickers, data_corte=data_corte)
        if not df_liquidity.empty:
            self.resultados['liquidez'] = ranking_liquidity(df_liquidity)
            print(f"    {len(self.resultados['liquidez'])} ativos analisados (liquidez)")
        else:
            print("    Sem dados para liquidez")
        

        df_volatility = get_data_volatility(self.db_path, tickers, data_corte=data_corte)
        if not df_volatility.empty:
            self.resultados['volatilidade'] = ranking_volatility(df_volatility)
            print(f"    {len(self.resultados['volatilidade'])} ativos analisados (volatilidade)")
        else:
            print("    Sem dados para volatilidade")
        
        return self.resultados
    
    def consolidar_resultados(self):
        """
        Combina os resultados das 3 análises em um único DataFrame
        """
        if len(self.resultados) < 3:
            print("Execute todas as análises primeiro!")
            return None
        

        consolidado = self.resultados['momentum'].copy()
        

        consolidado = consolidado.rename(columns={
            'retorno_12m': 'mom_retorno',
            'momentum_score': 'mom_score'
        })
        
        liq = self.resultados['liquidez'][['ticker', 'adtv_21', 'amihud_medio_21', 'liquidez_score']]
        consolidado = consolidado.merge(liq, on='ticker', how='inner')
        
        vol = self.resultados['volatilidade'][['ticker', 'vol_historica', 'vol_park_media', 'risco_score']]
        consolidado = consolidado.merge(vol, on='ticker', how='inner')
        
        # Momentum: quanto maior, melhor
        consolidado['mom_score_norm'] = consolidado['mom_score'].rank(pct=True) * 100
        
        # Liquidez: quanto maior, melhor
        consolidado['liq_score_norm'] = consolidado['liquidez_score']
        
        # Risco: quanto MENOR, melhor (inverter o score)
        consolidado['risco_score_norm'] = 100 - consolidado['risco_score']
        

        pesos = {
            'momentum': 0.40,
            'liquidez': 0.30,
            'risco': 0.30
        }
        
        consolidado['score_final'] = (
            consolidado['mom_score_norm'] * pesos['momentum'] +
            consolidado['liq_score_norm'] * pesos['liquidez'] +
            consolidado['risco_score_norm'] * pesos['risco']
        )
        
        # Classificação por perfil
        consolidado['classificacao'] = consolidado['score_final'].apply(
            self._classificar_ativo
        )
        

        self.ranking_final = consolidado.sort_values('score_final', ascending=False)
        
        return self.ranking_final
    
    def _classificar_ativo(self, score):
        """Classifica o ativo baseado no score final"""
        if score >= 80:
            return "COMPRA FORTE"
        elif score >= 60:
            return "COMPRA MODERADA"
        elif score >= 40:
            return "NEUTRO"
        elif score >= 20:
            return "EVITAR"
        else:
            return "VENDA FORTE"
    
    def gerar_recomendacoes(self, top_n=10):
        """
        Gera recomendações detalhadas baseadas na análise consolidada
        """
        if self.ranking_final is None:
            print(" Execute a consolidação primeiro!")
            return None
               
        top_ativos = self.ranking_final.head(top_n)
        
        print(f"\n  TOP {top_n} ATIVOS RECOMENDADOS:")
        print("-" * 70)
        
        for i, (idx, ativo) in enumerate(top_ativos.iterrows(), 1):
            print(f"\n{i}. {ativo['ticker']} - {ativo['classificacao']}")
            print(f"   Momentum: {ativo['mom_retorno']:.2%} | Score: {ativo['mom_score_norm']:.1f}")
            print(f"   Liquidez: R$ {ativo['adtv_21']/1e6:.1f}M | Score: {ativo['liq_score_norm']:.1f}")
            print(f"   Risco: {ativo['vol_historica']:.2%} | Score: {ativo['risco_score_norm']:.1f}")
            print(f"   Score Final: {ativo['score_final']:.1f}")
        
        return top_ativos
    
    def analisar_perfil_risco(self):
        """
        Análise detalhada do perfil de risco dos ativos
        """
        if self.ranking_final is None:
            return None
        
        print("\n" + "="*70)
        print("  ANÁLISE DE PERFIL DE RISCO")
        print("="*70)
        
        baixo_risco = self.ranking_final[self.ranking_final['vol_historica'] < 0.20]
        medio_risco = self.ranking_final[(self.ranking_final['vol_historica'] >= 0.20) & 
                                         (self.ranking_final['vol_historica'] < 0.35)]
        alto_risco = self.ranking_final[self.ranking_final['vol_historica'] >= 0.35]
        
        print(f"\n   Baixo Risco (<20%): {len(baixo_risco)} ativos")
        print(f"   Médio Risco (20-35%): {len(medio_risco)} ativos")
        print(f"   Alto Risco (>35%): {len(alto_risco)} ativos")

        if not baixo_risco.empty:
            top_baixo = baixo_risco.iloc[0]
            print(f"\n   Melhor ativo de Baixo Risco: {top_baixo['ticker']} (Score: {top_baixo['score_final']:.1f})")
        
        if not medio_risco.empty:
            top_medio = medio_risco.iloc[0]
            print(f"   Melhor ativo de Médio Risco: {top_medio['ticker']} (Score: {top_medio['score_final']:.1f})")
        
        if not alto_risco.empty:
            top_alto = alto_risco.iloc[0]
            print(f"   Melhor ativo de Alto Risco: {top_alto['ticker']} (Score: {top_alto['score_final']:.1f})")
    
    def gerar_relatorio_completo(self, filename="reports/relatorio_investimento.xlsx"):
        """
        Gera um relatório completo em Excel com todas as análises
        """
        if self.ranking_final is None:
            print("   Execute a consolidação primeiro!")
            return
        
        with pd.ExcelWriter(filename, engine='openpyxl') as writer:
            self.ranking_final.to_excel(writer, sheet_name='Recomendações', index=False)
            self.resultados['momentum'].to_excel(writer, sheet_name='Momentum', index=False)
            self.resultados['liquidez'].to_excel(writer, sheet_name='Liquidez', index=False)
            self.resultados['volatilidade'].to_excel(writer, sheet_name='Volatilidade', index=False)
            
            estatisticas_data = {
                'Média Momentum': [f"{self.ranking_final['mom_retorno'].mean():.2%}"],
                'Média Liquidez': [f"R$ {self.ranking_final['adtv_21'].mean()/1e6:.1f}M"],
                'Média Volatilidade': [f"{self.ranking_final['vol_historica'].mean():.2%}"],
                'Total Ativos': [len(self.ranking_final)],
                'Data Análise': [datetime.now().strftime('%Y-%m-%d %H:%M')]
            }
            estatisticas = pd.DataFrame(estatisticas_data)
            estatisticas.to_excel(writer, sheet_name='Estatísticas', index=False)
        
        print(f"\n  Relatório completo salvo em: {filename}")

def executar_analise_completa(tickers=None, perfil_risco='moderado', data_corte=None):
    """
    Função principal que executa toda a análise e gera recomendações
    """
    analise = AnaliseConsolidada()
    analise.executar_todas_analises(tickers, data_corte=data_corte)
    ranking = analise.consolidar_resultados()
    
    if ranking is not None:
        top_10 = analise.gerar_recomendacoes(top_n=10)
        analise.analisar_perfil_risco()
        analise.gerar_relatorio_completo()
        return ranking
    
    return None

if __name__ == "__main__":
    ranking_final = executar_analise_completa()