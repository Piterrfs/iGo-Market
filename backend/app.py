from flask import Flask, jsonify, request, send_file
from flask_cors import CORS
import os
from datetime import datetime
from scraper import MercadoScraper
from ocr_processor import OCRProcessor
from comparador import ComparadorPrecos
from config import CSV_DIR, DATA_DIR, MERCADOS
import pandas as pd
import json

app = Flask(__name__)
CORS(app)

# Instâncias globais
scraper = MercadoScraper()
ocr = OCRProcessor()
comparador = ComparadorPrecos()

@app.route('/api/health', methods=['GET'])
def health():
    """Endpoint de health check"""
    return jsonify({'status': 'ok', 'message': 'API funcionando'})

@app.route('/api/scrape', methods=['POST'])
def executar_scraping():
    """Executa scraping de todos os mercados"""
    try:
        print("Iniciando scraping...")
        resultados = scraper.scrape_all()
        
        # Processar imagens com OCR
        todos_produtos = []
        for mercado in ['guanabara', 'mundial', 'supermarket', 'prezunic']:
            produtos = ocr.processar_imagens_mercado(mercado.title())
            todos_produtos.extend(produtos)
        
        # Salvar em CSV
        if todos_produtos:
            df = pd.DataFrame(todos_produtos)
            csv_path = os.path.join(CSV_DIR, f"produtos_{datetime.now().strftime('%Y%m%d')}.csv")
            df.to_csv(csv_path, index=False)
            
            # Atualizar comparador
            comparador.carregar_dados(csv_path)
        
        return jsonify({
            'success': True,
            'message': f'Scraping concluído. {len(todos_produtos)} produtos encontrados.',
            'produtos': len(todos_produtos)
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/buscar', methods=['GET'])
def buscar_produto():
    """Busca produtos por termo"""
    termo = request.args.get('q', '')
    
    if not termo:
        return jsonify({'error': 'Parâmetro "q" é obrigatório'}), 400
    
    comparador.carregar_dados()
    resultados = comparador.buscar_produto(termo)
    
    return jsonify({
        'success': True,
        'resultados': resultados,
        'total': len(resultados)
    })

@app.route('/api/comparar', methods=['GET'])
def comparar_precos():
    """Compara preços de produtos"""
    produto = request.args.get('produto', None)
    marca = request.args.get('marca', None)
    quantidade = request.args.get('quantidade', None)
    
    comparador.carregar_dados()
    resultados = comparador.comparar_produtos(produto, marca, quantidade)
    
    return jsonify({
        'success': True,
        'resultados': resultados,
        'total': len(resultados)
    })

@app.route('/api/planilha', methods=['GET'])
def gerar_planilha():
    """Gera e retorna planilha Excel"""
    try:
        comparador.carregar_dados()
        caminho_arquivo = comparador.exportar_planilha()
        
        if caminho_arquivo and os.path.exists(caminho_arquivo):
            return send_file(
                caminho_arquivo,
                mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                as_attachment=True,
                download_name=os.path.basename(caminho_arquivo)
            )
        else:
            return jsonify({'error': 'Nenhum dado disponível para exportar'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/estatisticas', methods=['GET'])
def estatisticas():
    """Retorna estatísticas dos dados"""
    comparador.carregar_dados()
    
    if comparador.df is None or comparador.df.empty:
        return jsonify({
            'total_produtos': 0,
            'total_mercados': 0,
            'data_atualizacao': None
        })
    
    df = comparador.df
    
    return jsonify({
        'total_produtos': len(df),
        'total_mercados': df['mercado'].nunique(),
        'mercados': df['mercado'].unique().tolist(),
        'preco_medio': float(df['preco'].mean()) if 'preco' in df.columns else 0,
        'preco_minimo': float(df['preco'].min()) if 'preco' in df.columns else 0,
        'preco_maximo': float(df['preco'].max()) if 'preco' in df.columns else 0,
        'data_atualizacao': df['data_extracao'].max() if 'data_extracao' in df.columns else None
    })

@app.route('/api/carrinho', methods=['POST'])
def calcular_carrinho():
    """Calcula o carrinho mais barato para uma lista de produtos"""
    try:
        data = request.get_json()
        produtos = data.get('produtos', [])
        
        if not produtos:
            return jsonify({'error': 'Lista de produtos é obrigatória'}), 400
        
        comparador.carregar_dados()
        resultado = comparador.calcular_carrinho_mais_barato(produtos)
        
        if resultado is None:
            return jsonify({'error': 'Nenhum dado disponível'}), 404
        
        return jsonify({
            'success': True,
            'resultado': resultado
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/tabela-comparativa', methods=['GET'])
def gerar_tabela_comparativa():
    """Gera tabela comparativa de preços no formato solicitado"""
    try:
        comparador.carregar_dados()
        
        if comparador.df is None or comparador.df.empty:
            return jsonify({'error': 'Nenhum dado disponível. Execute o scraping primeiro.'}), 404
        
        df = comparador.df.copy()
        
        # Normalizar nomes das colunas (case-insensitive) ANTES de verificar
        df.columns = df.columns.str.lower().str.strip()
        
        # Garantir que temos os campos necessários
        if 'segmento' not in df.columns:
            df['segmento'] = 'Outros'
        if 'url_fonte' not in df.columns:
            df['url_fonte'] = ''
        
        # Verificar se temos as colunas necessárias para agrupar
        
        # Mapear possíveis variações de nomes
        mapeamento_colunas = {
            'product': 'produto',
            'item': 'produto',
            'brand': 'marca',
            'quantity': 'quantidade',
            'qtd': 'quantidade',
            'price': 'preco',
            'preço': 'preco',
            'market': 'mercado',
            'store': 'mercado'
        }
        
        for col_antiga, col_nova in mapeamento_colunas.items():
            if col_antiga in df.columns and col_nova not in df.columns:
                df.rename(columns={col_antiga: col_nova}, inplace=True)
        
        colunas_necessarias = ['produto', 'marca', 'quantidade']
        colunas_faltantes = [col for col in colunas_necessarias if col not in df.columns]
        if colunas_faltantes:
            return jsonify({
                'error': f'Colunas faltantes no CSV: {", ".join(colunas_faltantes)}',
                'colunas_disponiveis': list(df.columns),
                'detalhes': 'Verifique se o CSV tem as colunas: produto, marca, quantidade, preco, mercado'
            }), 400
        
        # Preencher valores NaN antes de agrupar
        df['segmento'] = df['segmento'].fillna('Outros')
        df['produto'] = df['produto'].fillna('Produto')
        df['marca'] = df['marca'].fillna('Genérico')
        df['quantidade'] = df['quantidade'].fillna('un')
        
        # Gerar tabela comparativa
        tabela = []
        try:
            grupos = df.groupby(['segmento', 'produto', 'marca', 'quantidade'], dropna=False)
            
            for (segmento, produto, marca, qtd), grupo in grupos:
                if grupo.empty:
                    continue
                    
                grupo_ordenado = grupo.sort_values('preco')
                menor_preco_item = grupo_ordenado.iloc[0]
                
                # Verificar se tem preço válido
                preco_valor = menor_preco_item['preco']
                if pd.isna(preco_valor) or (isinstance(preco_valor, (int, float)) and preco_valor <= 0):
                    continue
                
                # Formatar preço
                preco_formatado = f"R$ {menor_preco_item['preco']:.2f}".replace('.', ',')
                
                # Obter URL do mercado
                mercado_nome = str(menor_preco_item['mercado']) if not pd.isna(menor_preco_item['mercado']) else 'Desconhecido'
                url_mercado = str(menor_preco_item.get('url_fonte', '')) if not pd.isna(menor_preco_item.get('url_fonte', '')) else ''
                if not url_mercado:
                    # Buscar URL do mercado na configuração
                    for key, mercado_info in MERCADOS.items():
                        if mercado_info['nome'].lower() == mercado_nome.lower():
                            url_mercado = mercado_info['url']
                            break
                
                tabela.append({
                    'Segmento': str(segmento) if not pd.isna(segmento) else 'Outros',
                    'Produto': str(produto) if not pd.isna(produto) else 'Produto',
                    'Marca': str(marca) if not pd.isna(marca) else 'Genérico',
                    'Qtd': str(qtd) if not pd.isna(qtd) else 'un',
                    'Menor Preço': preco_formatado,
                    'Mercado': mercado_nome,
                    'Link': url_mercado
                })
        except Exception as e:
            return jsonify({'error': f'Erro ao processar dados: {str(e)}'}), 500
        
        # Ordenar por segmento e produto
        tabela_ordenada = sorted(tabela, key=lambda x: (x['Segmento'], x['Produto'], x['Marca']))
        
        return jsonify({
            'success': True,
            'tabela': tabela_ordenada,
            'total': len(tabela_ordenada)
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    print("Iniciando servidor Flask...")
    print("API disponível em http://localhost:5000")
    app.run(debug=True, host='0.0.0.0', port=5000)


