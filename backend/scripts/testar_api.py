"""
Script para testar a API localmente
"""
import requests
import json

BASE_URL = 'http://localhost:5000/api'

def testar_endpoints():
    """Testa todos os endpoints da API"""
    
    print("🧪 Testando API do iGo Market\n")
    
    # 1. Health Check
    print("1. Testando Health Check...")
    try:
        response = requests.get(f"{BASE_URL}/health")
        print(f"   ✅ Status: {response.status_code}")
        print(f"   📄 Resposta: {response.json()}\n")
    except Exception as e:
        print(f"   ❌ Erro: {e}\n")
    
    # 2. Estatísticas
    print("2. Testando Estatísticas...")
    try:
        response = requests.get(f"{BASE_URL}/estatisticas")
        print(f"   ✅ Status: {response.status_code}")
        print(f"   📄 Resposta: {json.dumps(response.json(), indent=2, ensure_ascii=False)}\n")
    except Exception as e:
        print(f"   ❌ Erro: {e}\n")
    
    # 3. Buscar Produto
    print("3. Testando Busca de Produto (arroz)...")
    try:
        response = requests.get(f"{BASE_URL}/buscar", params={'q': 'arroz'})
        print(f"   ✅ Status: {response.status_code}")
        data = response.json()
        print(f"   📄 Total de resultados: {data.get('total', 0)}\n")
    except Exception as e:
        print(f"   ❌ Erro: {e}\n")
    
    # 4. Comparar Preços
    print("4. Testando Comparação de Preços (leite)...")
    try:
        response = requests.get(f"{BASE_URL}/comparar", params={'produto': 'leite'})
        print(f"   ✅ Status: {response.status_code}")
        data = response.json()
        print(f"   📄 Total de resultados: {data.get('total', 0)}")
        if data.get('resultados'):
            primeiro = data['resultados'][0]
            print(f"   💰 Melhor oferta: {primeiro.get('produto')} - {primeiro.get('menor_preco')} em {primeiro.get('mercado_menor_preco')}\n")
    except Exception as e:
        print(f"   ❌ Erro: {e}\n")
    
    # 5. Gerar Planilha
    print("5. Testando Geração de Planilha...")
    try:
        response = requests.get(f"{BASE_URL}/planilha")
        if response.status_code == 200:
            print(f"   ✅ Status: {response.status_code}")
            print(f"   📊 Planilha gerada com sucesso!\n")
        else:
            print(f"   ⚠️ Status: {response.status_code}")
            print(f"   📄 Resposta: {response.json()}\n")
    except Exception as e:
        print(f"   ❌ Erro: {e}\n")

if __name__ == '__main__':
    print("⚠️ Certifique-se de que o servidor está rodando (python app.py)\n")
    testar_endpoints()


