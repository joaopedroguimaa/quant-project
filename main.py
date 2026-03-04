from api.market_data import DataFetcher

def main():

    fetcher = DataFetcher()
    

    dados_brutos = fetcher.get_data()
    dados_linha = fetcher.data_to_rows(dados_brutos)
    print(dados_linha)
    

    novos = fetcher.save_data()
    print(f"{novos} novos registros salvos!")

if __name__ == "__main__":
    main()