"""Teste da função ler_google_sheets sem Flask"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Importar apenas o necessário
import requests
import pandas as pd
from io import StringIO
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def ler_google_sheets():
    """Lê dados da planilha do Google Sheets via API pública"""
    try:
        # ID da planilha do Google Sheets
        sheet_id = '1gWYvYjPrTNAvEXkeYTh5SjnyWMir371D_5vTmacWAO8'
        
        # URL para exportar como CSV (formato público)
        url = f'https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv&gid=0'
        
        print(f"Lendo Google Sheets: {url}")
        
        print("Fazendo requisição HTTP...")
        try:
            # Tentar primeiro sem SSL (mais comum em ambientes corporativos)
            response = requests.get(url, timeout=20, verify=False)
            print(f"Resposta recebida (sem SSL): Status {response.status_code}")
            print(f"Tamanho da resposta: {len(response.text)} caracteres")
        except Exception as req_error:
            print(f"Erro sem SSL: {req_error}")
            raise
        
        response.raise_for_status()
        
        # Ler CSV
        print("Lendo CSV...")
        df = pd.read_csv(StringIO(response.text))
        print(f"DataFrame criado: {len(df)} linhas, {len(df.columns)} colunas")
        
        # Normalizar nomes das colunas
        df.columns = df.columns.str.strip()
        print(f"Colunas normalizadas: {list(df.columns)}")
        
        # Verificar se as colunas existem
        colunas_necessarias = ['Segmento', 'Produto', 'Marca', 'Qtd', 'Menor Preço', 'Mercado', 'Link']
        colunas_faltantes = [col for col in colunas_necessarias if col not in df.columns]
        
        if colunas_faltantes:
            print(f"ERRO: Colunas faltantes no Google Sheets: {colunas_faltantes}")
            print(f"Colunas disponíveis: {list(df.columns)}")
            return []
        
        print("Todas as colunas necessárias estão presentes!")
        
        # Converter para formato da tabela
        print("Convertendo para formato da tabela...")
        tabela = []
        for idx, row in df.iterrows():
            # Pular linhas vazias
            if pd.isna(row['Produto']) or str(row['Produto']).strip() == '':
                continue
            
            tabela.append({
                'Segmento': str(row['Segmento']) if not pd.isna(row['Segmento']) else 'Outros',
                'Produto': str(row['Produto']),
                'Marca': str(row['Marca']) if not pd.isna(row['Marca']) else 'Genérico',
                'Qtd': str(row['Qtd']) if not pd.isna(row['Qtd']) else 'un',
                'Menor Preço': str(row['Menor Preço']) if not pd.isna(row['Menor Preço']) else 'R$ 0,00',
                'Mercado': str(row['Mercado']) if not pd.isna(row['Mercado']) else 'Desconhecido',
                'Link': str(row['Link']) if not pd.isna(row['Link']) else ''
            })
            
            # Log a cada 20 produtos
            if (idx + 1) % 20 == 0:
                print(f"  Processados {idx + 1} linhas...")
        
        print(f"SUCESSO! Lidos {len(tabela)} produtos do Google Sheets")
        return tabela
        
    except Exception as e:
        print(f"ERRO: {e}")
        import traceback
        traceback.print_exc()
        return []

if __name__ == '__main__':
    print("=" * 60)
    print("TESTE DIRETO DA FUNCAO ler_google_sheets()")
    print("=" * 60)
    resultado = ler_google_sheets()
    print("=" * 60)
    if resultado:
        print(f"RESULTADO: {len(resultado)} produtos retornados")
        print("\nPrimeiros 5 produtos:")
        for i, p in enumerate(resultado[:5], 1):
            print(f"  {i}. {p['Produto']} - {p['Marca']} - {p['Menor Preço']}")
    else:
        print("RESULTADO: Lista vazia retornada")
