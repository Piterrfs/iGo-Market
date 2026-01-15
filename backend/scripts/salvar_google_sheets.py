"""Script para salvar produtos no Google Sheets usando API"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pandas as pd
from datetime import datetime
from config import CSV_DIR
import json

# ID da planilha do Google Sheets
PLANILHA_ID = '1gWYvYjPrTNAvEXkeYTh5SjnyWMir371D_5vTmacWAO8'

def salvar_produtos_google_sheets():
    """Salva produtos no Google Sheets"""
    
    # Buscar CSV mais recente
    csv_files = [f for f in os.listdir(CSV_DIR) if f.startswith('produtos_') and f.endswith('.csv')]
    if not csv_files:
        print("❌ Nenhum CSV encontrado!")
        return
    
    latest_csv = max(csv_files, key=lambda f: os.path.getmtime(os.path.join(CSV_DIR, f)))
    csv_path = os.path.join(CSV_DIR, latest_csv)
    
    print(f"Lendo CSV: {latest_csv}")
    df = pd.read_csv(csv_path, encoding='utf-8-sig')
    
    print(f"Total de produtos no CSV: {len(df)}")
    
    # Preparar dados para Google Sheets
    # Formato: Segmento | Produto | Marca | Qtd | Menor Preço | Mercado | Link
    dados_planilha = []
    
    # Agrupar por produto, marca e quantidade
    grupos = df.groupby(['segmento', 'produto', 'marca', 'quantidade'], dropna=False)
    
    for (segmento, produto, marca, qtd), grupo in grupos:
        if grupo.empty:
            continue
        
        # Encontrar menor preço
        grupo_ordenado = grupo.sort_values('preco')
        menor_preco_item = grupo_ordenado.iloc[0]
        
        preco_valor = menor_preco_item.get('preco', menor_preco_item.get('preco_oferta', 0))
        if pd.isna(preco_valor) or preco_valor <= 0:
            continue
        
        preco_formatado = f"R$ {float(preco_valor):.2f}".replace('.', ',')
        mercado_nome = str(menor_preco_item.get('mercado', 'Desconhecido'))
        url_fonte = str(menor_preco_item.get('url_fonte', ''))
        
        dados_planilha.append({
            'Segmento': str(segmento) if not pd.isna(segmento) else 'Outros',
            'Produto': str(produto) if not pd.isna(produto) else 'Produto',
            'Marca': str(marca) if not pd.isna(marca) else 'Genérico',
            'Qtd': str(qtd) if not pd.isna(qtd) else 'un',
            'Menor Preço': preco_formatado,
            'Mercado': mercado_nome,
            'Link': url_fonte
        })
    
    # Ordenar por segmento e produto
    dados_planilha.sort(key=lambda x: (x['Segmento'], x['Produto'], x['Marca']))
    
    print(f"\nTotal de produtos unicos: {len(dados_planilha)}")
    print("\nPrimeiros 5 produtos:")
    for i, p in enumerate(dados_planilha[:5], 1):
        print(f"  {i}. {p['Segmento']} | {p['Produto']} | {p['Marca']} | {p['Qtd']} | {p['Menor Preço']} | {p['Mercado']}")
    
    # Salvar em JSON para facilitar integração com Google Apps Script
    json_path = os.path.join(CSV_DIR, 'produtos_para_google_sheets.json')
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(dados_planilha, f, ensure_ascii=False, indent=2)
    
    # Salvar também em Excel
    excel_path = os.path.join(CSV_DIR, '..', 'excel', 'produtos_completos.xlsx')
    os.makedirs(os.path.dirname(excel_path), exist_ok=True)
    df_planilha = pd.DataFrame(dados_planilha)
    with pd.ExcelWriter(excel_path, engine='openpyxl') as writer:
        df_planilha.to_excel(writer, sheet_name='Produtos', index=False)
    
    print(f"\nDados salvos em JSON: {json_path}")
    print(f"Dados salvos em Excel: {excel_path}")
    print(f"\nPara salvar no Google Sheets:")
    print(f"   1. Abra a planilha: https://docs.google.com/spreadsheets/d/{PLANILHA_ID}/edit")
    print(f"   2. Use o Google Apps Script (GOOGLE_APPS_SCRIPT_PARA_PRODUTOS.gs)")
    print(f"   3. Ou copie manualmente do arquivo Excel/JSON")
    
    return dados_planilha

if __name__ == '__main__':
    salvar_produtos_google_sheets()
