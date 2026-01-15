"""Teste simples para verificar extração do Guanabara"""
import requests
from bs4 import BeautifulSoup
import re

# Testar com requests primeiro (mais simples)
url = 'https://www.supermercadosguanabara.com.br/produtos/42'
print(f"Testando URL: {url}")

try:
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }
    response = requests.get(url, headers=headers, timeout=30)
    print(f"Status: {response.status_code}")
    print(f"HTML length: {len(response.text)}")
    
    # Buscar padrões de preço
    precos = re.findall(r'R\$\s*(\d+)[,.](\d{2})|(\d+)[,.](\d{2})', response.text)
    print(f"\nPadrões de preço encontrados: {len(precos)}")
    
    if precos:
        print("\nPrimeiros 10 preços:")
        for i, p in enumerate(precos[:10], 1):
            if p[0]:
                print(f"  {i}. R$ {p[0]},{p[1]}")
            else:
                print(f"  {i}. {p[2]},{p[3]}")
    
    # Buscar por BeautifulSoup
    soup = BeautifulSoup(response.text, 'html.parser')
    texto_completo = soup.get_text()
    
    # Buscar padrão: número seguido de texto (nome do produto)
    # Padrão Guanabara: "13,95 Arroz Branco..."
    padrao_produto = re.findall(r'(\d+[,.]\d{2})\s+([A-Z][^0-9]+?)(?=\d+[,.]\d{2}|$)', texto_completo)
    print(f"\nPadrões produto encontrados: {len(padrao_produto)}")
    
    if padrao_produto:
        print("\nPrimeiros 10 produtos:")
        for i, (preco, nome) in enumerate(padrao_produto[:10], 1):
            nome_limpo = nome.strip()[:50]
            print(f"  {i}. {nome_limpo} - {preco}")
    
except Exception as e:
    print(f"Erro: {e}")
    import traceback
    traceback.print_exc()
