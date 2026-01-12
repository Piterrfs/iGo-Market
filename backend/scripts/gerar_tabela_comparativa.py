"""
Script para gerar tabela comparativa de preços dos mercados
Formato: Segmento | Produto | Marca | Qtd | Menor Preço | Mercado | Link
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scraper import MercadoScraper
from ocr_processor import OCRProcessor
from comparador import ComparadorPrecos
from config import MERCADOS, CSV_DIR
import pandas as pd
from datetime import datetime

def gerar_tabela_comparativa():
    """Gera tabela comparativa de preços"""
    print("Iniciando geracao da tabela comparativa...")
    print("=" * 80)
    
    # Inicializar componentes
    scraper = MercadoScraper()
    ocr = OCRProcessor()
    comparador = ComparadorPrecos()
    
    # Executar scraping
    print("\nFazendo scraping dos mercados...")
    resultados_scraping = scraper.scrape_all()
    
    # Processar imagens com OCR
    print("\nProcessando imagens com OCR...")
    todos_produtos = []
    for mercado_key, mercado_info in MERCADOS.items():
        print(f"  Processando {mercado_info['nome']}...")
        produtos = ocr.processar_imagens_mercado(mercado_info['nome'])
        for produto in produtos:
            produto['mercado'] = mercado_info['nome']
            produto['url_fonte'] = mercado_info['url']
            todos_produtos.append(produto)
    
    if not todos_produtos:
        print("Nenhum produto encontrado. Usando dados existentes...")
        comparador.carregar_dados()
        if comparador.df is None or comparador.df.empty:
            print("ERRO: Nenhum dado disponivel. Execute o scraping primeiro.")
            return None
        df = comparador.df
    else:
        # Criar DataFrame
        df = pd.DataFrame(todos_produtos)
        
        # Salvar CSV
        csv_path = os.path.join(CSV_DIR, f"produtos_{datetime.now().strftime('%Y%m%d')}.csv")
        df.to_csv(csv_path, index=False)
        print(f"\nDados salvos em: {csv_path}")
        
        # Carregar no comparador
        comparador.carregar_dados(csv_path)
    
    # Gerar tabela comparativa
    print("\nGerando tabela comparativa...")
    
    # Agrupar por produto, marca e quantidade para encontrar menor preço
    tabela_comparativa = []
    
    grupos = df.groupby(['segmento', 'produto', 'marca', 'quantidade'])
    
    for (segmento, produto, marca, qtd), grupo in grupos:
        # Ordenar por preço
        grupo_ordenado = grupo.sort_values('preco')
        menor_preco_item = grupo_ordenado.iloc[0]
        
        # Formatar preço
        preco_formatado = f"R$ {menor_preco_item['preco']:.2f}".replace('.', ',')
        
        # Obter URL do mercado
        url_mercado = menor_preco_item.get('url_fonte', MERCADOS.get(
            menor_preco_item['mercado'].lower(), {}
        ).get('url', 'N/A'))
        
        tabela_comparativa.append({
            'Segmento': segmento or 'Outros',
            'Produto': produto,
            'Marca': marca,
            'Qtd': qtd,
            'Menor Preço': preco_formatado,
            'Mercado': menor_preco_item['mercado'],
            'Link': url_mercado
        })
    
    # Criar DataFrame da tabela
    df_tabela = pd.DataFrame(tabela_comparativa)
    
    # Ordenar por segmento e produto
    df_tabela = df_tabela.sort_values(['Segmento', 'Produto', 'Marca'])
    
    # Exibir tabela
    print("\n" + "=" * 80)
    print("TABELA COMPARATIVA DE PRECOS")
    print("=" * 80)
    print(df_tabela.to_string(index=False))
    print("=" * 80)
    print(f"\nTotal de produtos: {len(df_tabela)}")
    
    # Salvar em CSV
    csv_tabela = os.path.join(CSV_DIR, f"tabela_comparativa_{datetime.now().strftime('%Y%m%d')}.csv")
    df_tabela.to_csv(csv_tabela, index=False, encoding='utf-8-sig')
    print(f"Tabela salva em: {csv_tabela}")
    
    # Salvar em Excel
    excel_path = os.path.join(CSV_DIR, f"tabela_comparativa_{datetime.now().strftime('%Y%m%d')}.xlsx")
    with pd.ExcelWriter(excel_path, engine='openpyxl') as writer:
        df_tabela.to_excel(writer, sheet_name='Comparacao de Precos', index=False)
    print(f"Tabela Excel salva em: {excel_path}")
    
    return df_tabela

if __name__ == '__main__':
    try:
        tabela = gerar_tabela_comparativa()
        if tabela is not None:
            print("\nSUCESSO: Tabela comparativa gerada com sucesso!")
        else:
            print("\nERRO: Erro ao gerar tabela comparativa.")
    except Exception as e:
        print(f"\nERRO: {e}")
        import traceback
        traceback.print_exc()
