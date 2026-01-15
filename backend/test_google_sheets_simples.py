"""Teste simples da leitura do Google Sheets"""
import requests
import pandas as pd
from io import StringIO
import urllib3

# Desabilitar avisos SSL
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

sheet_id = '1gWYvYjPrTNAvEXkeYTh5SjnyWMir371D_5vTmacWAO8'
url = f'https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv&gid=0'

print("=" * 60)
print("TESTE DE LEITURA DO GOOGLE SHEETS")
print("=" * 60)
print(f"\nURL: {url}")

try:
    # Tentar sem SSL primeiro (ambiente corporativo)
    print("\n1. Tentando requisição (sem verificação SSL)...")
    response = requests.get(url, timeout=15, verify=False)
    print(f"   Status: {response.status_code}")
    
    if response.status_code == 200:
        print("\n2. Lendo CSV...")
        df = pd.read_csv(StringIO(response.text))
        print(f"   Linhas: {len(df)}")
        print(f"   Colunas: {list(df.columns)}")
        
        # Verificar colunas
        colunas_necessarias = ['Segmento', 'Produto', 'Marca', 'Qtd', 'Menor Preço', 'Mercado', 'Link']
        colunas_faltantes = [col for col in colunas_necessarias if col not in df.columns]
        
        if colunas_faltantes:
            print(f"\n   ✗ Colunas faltantes: {colunas_faltantes}")
        else:
            print(f"\n   ✓ Todas as colunas necessárias estão presentes")
        
        # Converter para formato da tabela
        print("\n3. Convertendo para formato da tabela...")
        tabela = []
        for _, row in df.iterrows():
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
        
        print(f"   ✓ Total de produtos convertidos: {len(tabela)}")
        print(f"\n4. Primeiros 5 produtos:")
        for i, produto in enumerate(tabela[:5], 1):
            print(f"   {i}. {produto['Produto']} - {produto['Marca']} - {produto['Menor Preço']}")
        
        print(f"\n{'='*60}")
        print(f"✓ SUCESSO! {len(tabela)} produtos lidos do Google Sheets")
        print(f"{'='*60}")
    else:
        print(f"\n✗ ERRO: Status {response.status_code}")
        print(f"Resposta: {response.text[:500]}")
        
except Exception as e:
    print(f"\n✗ ERRO: {e}")
    import traceback
    traceback.print_exc()
