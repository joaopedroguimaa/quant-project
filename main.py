from api.market_data import DataFetcher
from factors.returns import executar_analise_completa

def main():

    fetcher = DataFetcher()
    fetcher.get_data()
    novos = fetcher.save_data()
    print(f"{novos} novos registros salvos!")


    ranking = executar_analise_completa()
    if ranking is not None:
        print("Análise Concluída")

if __name__ == "__main__":
    main()