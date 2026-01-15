"""Script para testar a API de tabela comparativa"""
import requests
import json

try:
    print("Testando API /api/tabela-comparativa...")
    print("=" * 60)
    
    # Testar health check primeiro
    print("\n1. Testando health check...")
    response = requests.get('http://localhost:5000/api/health', timeout=5)
    print(f"   Status: {response.status_code}")
    print(f"   Resposta: {response.json()}")
    
    # Testar tabela comparativa
    print("\n2. Testando tabela comparativa...")
    response = requests.get('http://localhost:5000/api/tabela-comparativa', timeout=15)
    print(f"   Status: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"   Success: {data.get('success')}")
        print(f"   Fonte: {data.get('fonte', 'N/A')}")
        print(f"   Total de produtos: {len(data.get('tabela', []))}")
        
        if data.get('tabela'):
            print(f"\n   Primeiros 3 produtos:")
            for i, produto in enumerate(data['tabela'][:3], 1):
                print(f"   {i}. {produto.get('Produto')} - {produto.get('Marca')} - {produto.get('Menor Preço')}")
    else:
        print(f"   Erro: {response.text[:500]}")
        
except requests.exceptions.ConnectionError as e:
    print(f"\nERRO: Não foi possível conectar ao backend")
    print(f"   Verifique se o servidor está rodando em http://localhost:5000")
    print(f"   Erro: {e}")
except Exception as e:
    print(f"\nERRO: {e}")
    import traceback
    traceback.print_exc()
