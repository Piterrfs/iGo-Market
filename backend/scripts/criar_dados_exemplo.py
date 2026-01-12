"""
Script para criar dados de exemplo para testes
Baseado nos dados reais mencionados na documentação
"""
import pandas as pd
import os
import sys
from datetime import datetime

# Adicionar diretório pai ao path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import CSV_DIR

# Dados de exemplo baseados na documentação
dados_exemplo = [
    {
        'produto': 'Arroz Branco',
        'marca': 'Dona Elza',
        'quantidade': '5kg',
        'preco': 13.95,
        'mercado': 'Supermarket',
        'data_extracao': datetime.now().strftime('%Y-%m-%d'),
        'segmento': 'Mercearia'
    },
    {
        'produto': 'Arroz Branco',
        'marca': 'Tio João',
        'quantidade': '5kg',
        'preco': 27.95,
        'mercado': 'Guanabara',
        'data_extracao': datetime.now().strftime('%Y-%m-%d'),
        'segmento': 'Mercearia'
    },
    {
        'produto': 'Leite',
        'marca': 'Italac',
        'quantidade': '1L',
        'preco': 3.87,
        'mercado': 'Guanabara',
        'data_extracao': datetime.now().strftime('%Y-%m-%d'),
        'segmento': 'Laticínios'
    },
    {
        'produto': 'Leite',
        'marca': 'Italac',
        'quantidade': '1L',
        'preco': 3.87,
        'mercado': 'Supermarket',
        'data_extracao': datetime.now().strftime('%Y-%m-%d'),
        'segmento': 'Laticínios'
    },
    {
        'produto': 'Leite',
        'marca': 'Italac',
        'quantidade': '1L',
        'preco': 4.50,
        'mercado': 'Mundial',
        'data_extracao': datetime.now().strftime('%Y-%m-%d'),
        'segmento': 'Laticínios'
    },
    {
        'produto': 'Sabão em Pó',
        'marca': 'Omo',
        'quantidade': '1.6kg',
        'preco': 19.90,
        'mercado': 'Mundial',
        'data_extracao': datetime.now().strftime('%Y-%m-%d'),
        'segmento': 'Limpeza'
    },
    {
        'produto': 'Sabão em Pó',
        'marca': 'Omo',
        'quantidade': '1.6kg',
        'preco': 24.90,
        'mercado': 'Guanabara',
        'data_extracao': datetime.now().strftime('%Y-%m-%d'),
        'segmento': 'Limpeza'
    },
    {
        'produto': 'Alcatra',
        'marca': 'Genérico',
        'quantidade': '1kg',
        'preco': 34.90,
        'mercado': 'Guanabara',
        'data_extracao': datetime.now().strftime('%Y-%m-%d'),
        'segmento': 'Açougue'
    },
    {
        'produto': 'Alcatra',
        'marca': 'Genérico',
        'quantidade': '1kg',
        'preco': 38.90,
        'mercado': 'Mundial',
        'data_extracao': datetime.now().strftime('%Y-%m-%d'),
        'segmento': 'Açougue'
    },
    {
        'produto': 'Feijão Preto',
        'marca': 'Tio João',
        'quantidade': '1kg',
        'preco': 8.90,
        'mercado': 'Prezunic',
        'data_extracao': datetime.now().strftime('%Y-%m-%d'),
        'segmento': 'Mercearia'
    },
    {
        'produto': 'Feijão Preto',
        'marca': 'Tio João',
        'quantidade': '1kg',
        'preco': 9.50,
        'mercado': 'Guanabara',
        'data_extracao': datetime.now().strftime('%Y-%m-%d'),
        'segmento': 'Mercearia'
    },
]

def criar_arquivo_exemplo():
    """Cria arquivo CSV com dados de exemplo"""
    df = pd.DataFrame(dados_exemplo)
    arquivo = os.path.join(CSV_DIR, f"produtos_{datetime.now().strftime('%Y%m%d')}.csv")
    df.to_csv(arquivo, index=False)
    print(f"[OK] Arquivo de exemplo criado: {arquivo}")
    print(f"[INFO] Total de produtos: {len(df)}")
    print(f"[INFO] Mercados: {df['mercado'].unique().tolist()}")
    return arquivo

if __name__ == '__main__':
    criar_arquivo_exemplo()

