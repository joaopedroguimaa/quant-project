import sqlite3
import pandas as pd
import os

class DataBase:

    def __init__(self, db_name="database/acoes.db"):
        os.makedirs(os.path.dirname(db_name), exist_ok=True)

        self.db_name = db_name
        self.create_table()

    def create_table(self):
        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.cursor()
            
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS precos_acoes (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    ticker VARCHAR(10) NOT NULL,
                    date DATE NOT NULL,
                    open FLOAT,
                    high FLOAT,
                    low FLOAT,
                    close FLOAT,
                    volume INTEGER,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(ticker, date)
                )
            """)

    def insert_dados(self, df):
        if df.empty:
            print("DataFrame vazio")
            return 0
        
        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.cursor()
            
            registros_novos = 0
            registros_existentes = 0
            erros = 0
            
            for _, row in df.iterrows():
                try:
                    cursor.execute("""
                        INSERT OR IGNORE INTO precos_acoes 
                        (ticker, date, open, high, low, close, volume)
                        VALUES (?, ?, ?, ?, ?, ?, ?)
                    """, (
                        row['ticker'],
                        row['date'],
                        row['open'],
                        row['high'],
                        row['low'],
                        row['close'],
                        row['volume']
                    ))
                    
                    if cursor.rowcount > 0:
                        registros_novos += 1
                    else:
                        registros_existentes += 1
                        
                except Exception as e:
                    erros += 1
                    print(" Erro ao inserir")
         
            return registros_novos

    def export_to_excel(self, excel_name="database/acoes.xlsx"):
        print(f"Exportando banco de dados para {excel_name}...")
        try:
            with sqlite3.connect(self.db_name) as conn:
                df = pd.read_sql_query("SELECT * FROM precos_acoes", conn)
                df.to_excel(excel_name, index=False)
                print(f"Exportação para {excel_name} concluída com sucesso!")
        except Exception as e:
            print(f"Erro ao exportar para Excel: {e}")