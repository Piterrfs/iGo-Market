"""Script para testar leitura do Google Sheets"""
import requests
import pandas as pd
from io import StringIO

sheet_id = '1gWYvYjPrTNAvEXkeYTh5SjnyWMir371D_5vTmacWAO8'
url = f'https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv&gid=0'

print(f"Testando URL: {url}")
print("=" * 60)

try:
    # Tentar primeiro com verificação SSL
    try:
        response = requests.get(url, timeout=10, verify=True)
    except requests.exceptions.SSLError:
        # Se falhar, tentar sem verificação (para ambientes corporativos)
        print("Aviso: Tentando sem verificação SSL...")
        import urllib3
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
        response = requests.get(url, timeout=10, verify=False)
    
    print(f"Status HTTP: {response.status_code}")
    
    if response.status_code == 200:
        df = pd.read_csv(StringIO(response.text))
        print(f"\nLinhas lidas: {len(df)}")
        print(f"Colunas: {list(df.columns)}")
        print(f"\nPrimeiras 5 linhas:")
        print(df.head(5).to_string())
        print(f"\nÚltimas 3 linhas:")
        print(df.tail(3).to_string())
    else:
        print(f"Erro: {response.text[:500]}")
except Exception as e:
    print(f"Erro ao acessar: {e}")
    import traceback
    traceback.print_exc()
