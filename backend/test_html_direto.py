"""Teste direto com HTML fornecido pelo usuário"""
from bs4 import BeautifulSoup
import re

# HTML de exemplo baseado no que foi fornecido
html_exemplo = """
13,95 

Arroz Branco Ouro Nobre 5Kg

18,95 

Arroz Combrasil 5kg

13,95 

Arroz Rei do Sul 5kg

19,95 cada

Arroz Máximo 5Kg
"""

print("=== TESTE COM HTML EXEMPLO ===")
print(f"HTML: {html_exemplo[:200]}...")
print()

# Testar regex atual
padrao_atual = r'(\d+[,.]\d{2})\s+([A-ZÁÉÍÓÚÂÊÔÃÕÇ][^0-9<>]{5,100}?)(?=\s*\d+[,.]\d{2}|<|$)'
matches_atual = list(re.finditer(padrao_atual, html_exemplo, re.MULTILINE | re.IGNORECASE))
print(f"Regex atual encontrou: {len(matches_atual)} matches")

# Testar nova regex mais simples
padrao_novo = r'(\d+[,.]\d{2})\s+([A-Za-zÁÉÍÓÚÂÊÔÃÕÇáéíóúâêôãõç][A-Za-zÁÉÍÓÚÂÊÔÃÕÇáéíóúâêôãõç0-9\s]{3,60}?)(?=\s*\d+[,.]\d{2}|\s*cada|$)'
matches_novo = list(re.finditer(padrao_novo, html_exemplo, re.MULTILINE))
print(f"Regex nova encontrou: {len(matches_novo)} matches")

if matches_novo:
    print("\nProdutos encontrados:")
    for i, match in enumerate(matches_novo, 1):
        preco = match.group(1)
        nome = match.group(2).strip()
        print(f"{i}. {nome} - R$ {preco}")

# Testar com BeautifulSoup
soup = BeautifulSoup(html_exemplo, 'html.parser')
texto = soup.get_text()
print(f"\nTexto extraído: {texto[:200]}")

# Buscar padrão no texto
matches_texto = list(re.finditer(padrao_novo, texto, re.MULTILINE))
print(f"Matches no texto: {len(matches_texto)}")
