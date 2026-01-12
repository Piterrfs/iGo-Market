from flask import Flask, jsonify, request, send_file
from flask_cors import CORS
import os
from datetime import datetime
from scraper import MercadoScraper
from ocr_processor import OCRProcessor
from comparador import ComparadorPrecos
from config import CSV_DIR, DATA_DIR
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

if __name__ == '__main__':
    print("Iniciando servidor Flask...")
    print("API disponível em http://localhost:5000")
    app.run(debug=True, host='0.0.0.0', port=5000)


