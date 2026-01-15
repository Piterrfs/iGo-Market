"""Script para gerar produtos do Guanabara baseado no HTML fornecido"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pandas as pd
from datetime import datetime
from config import CSV_DIR, EXCEL_DIR, MERCADOS
import re

def gerar_produtos_guanabara():
    """Gera produtos do Guanabara baseado no HTML fornecido"""
    
    # Produtos extraídos do HTML fornecido
    produtos_texto = """
    13,95 Arroz Branco Ouro Nobre 5Kg
    18,95 Arroz Combrasil 5kg
    13,95 Arroz Rei do Sul 5kg
    19,95 Arroz Máximo 5Kg
    18,95 Arroz Carreteiro 5kg
    27,95 Arroz Branco Tio João 5kg
    2,99 Farinha de Trigo Globo Kg
    4,99 Feijão Preto Combrasil Kg
    3,99 Feijão Preto Copa Kg
    4,99 Feijão Preto Kicaldo 1kg
    2,99 Feijão Preto Macio Kg
    4,99 Feijão Preto Máximo Kg
    3,99 Feijão Preto Panela de Barro 1kg
    2,99 Feijão Preto Sanes Kg
    4,62 Pipoca Microondas Yoki 90g/100g
    """
    
    produtos = []
    
    # Processar cada linha
    for linha in produtos_texto.strip().split('\n'):
        linha = linha.strip()
        if not linha:
            continue
        
        # Extrair preço e nome
        match = re.match(r'(\d+[,.]\d{2})\s+(.+)', linha)
        if match:
            preco_str = match.group(1).replace(',', '.')
            preco = float(preco_str)
            nome_completo = match.group(2).strip()
            
            # Extrair quantidade
            qtd_match = re.search(r'(\d+(?:[,.]\d+)?)\s*(kg|g|L|l|ml)', nome_completo, re.IGNORECASE)
            quantidade = qtd_match.group(0) if qtd_match else 'un'
            
            # Identificar marca e produto
            nome_lower = nome_completo.lower()
            marca = 'Genérico'
            
            # Identificar marca conhecida
            marcas = {
                'tio joao': 'Tio João',
                't. joao': 'Tio João',
                'ouro nobre': 'Ouro Nobre',
                'combrasil': 'Combrasil',
                'rei do sul': 'Rei do Sul',
                'maximo': 'Máximo',
                'carreteiro': 'Carreteiro',
                'globo': 'Globo',
                'copa': 'Copa',
                'kicaldo': 'Kicaldo',
                'panela de barro': 'Panela de Barro',
                'sanes': 'Sanes',
                'yoki': 'Yoki'
            }
            
            for marca_key, marca_nome in marcas.items():
                if marca_key in nome_lower:
                    marca = marca_nome
                    break
            
            # Identificar produto base
            produto_base = nome_completo
            if marca != 'Genérico':
                # Remover marca do nome
                for marca_key in marcas.keys():
                    produto_base = re.sub(marca_key, '', produto_base, flags=re.IGNORECASE)
                produto_base = re.sub(r'\s+', ' ', produto_base).strip()
            
            # Identificar segmento
            if 'arroz' in nome_lower:
                segmento = 'Mercearia'
                produto = 'Arroz Branco'
            elif 'feijao' in nome_lower or 'feijão' in nome_lower:
                segmento = 'Mercearia'
                produto = 'Feijão Preto'
            elif 'farinha' in nome_lower:
                segmento = 'Mercearia'
                produto = 'Farinha de Trigo'
            elif 'pipoca' in nome_lower:
                segmento = 'Mercearia'
                produto = 'Pipoca Microondas'
            else:
                segmento = 'Mercearia'
                produto = produto_base.split()[0] if produto_base.split() else 'Produto'
            
            produtos.append({
                'segmento': segmento,
                'produto': produto,
                'marca': marca,
                'quantidade': quantidade,
                'preco': preco,
                'preco_oferta': preco,
                'mercado': 'Guanabara',
                'url_fonte': 'https://www.supermercadosguanabara.com.br/produtos',
                'data_extracao': datetime.now().strftime('%Y-%m-%d')
            })
    
    # Criar DataFrame
    df = pd.DataFrame(produtos)
    
    # Salvar CSV
    csv_path = os.path.join(CSV_DIR, f"produtos_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv")
    df.to_csv(csv_path, index=False, encoding='utf-8-sig')
    print(f"CSV salvo: {csv_path}")
    print(f"  Total de produtos: {len(df)}")
    
    # Salvar Excel
    excel_path = os.path.join(EXCEL_DIR, f"produtos_guanabara_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx")
    os.makedirs(EXCEL_DIR, exist_ok=True)
    with pd.ExcelWriter(excel_path, engine='openpyxl') as writer:
        df.to_excel(writer, sheet_name='Produtos', index=False)
    print(f"Excel salvo: {excel_path}")
    
    # Mostrar produtos
    print("\nProdutos gerados:")
    for i, p in enumerate(produtos[:10], 1):
        print(f"{i}. {p['produto']} - {p['marca']} - {p['quantidade']} - R$ {p['preco']:.2f}")
    
    return csv_path

if __name__ == '__main__':
    gerar_produtos_guanabara()
