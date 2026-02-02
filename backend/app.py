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
import requests

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
        
        # Processar produtos HTML retornados pelo scraper
        todos_produtos = []
        
        print(f"\n=== PROCESSANDO RESULTADOS DO SCRAPER ===")
        print(f"Total de mercados processados: {len(resultados)}")
        
        # Converter produtos HTML para formato padrão
        for mercado_key, produtos_html in resultados.items():
            print(f"\nMercado: {mercado_key}")
            print(f"  Tipo do retorno: {type(produtos_html)}")
            print(f"  Produtos HTML retornados: {len(produtos_html) if produtos_html else 0}")
            
            if produtos_html and len(produtos_html) > 0:
                print(f"  Primeiro produto exemplo: {produtos_html[0] if produtos_html else 'N/A'}")
                for produto_html in produtos_html:
                    # Normalizar produto HTML para formato padrão
                    produto_normalizado = {
                        'segmento': produto_html.get('categoria', 'Outros'),
                        'produto': produto_html.get('nome', ''),
                        'marca': 'Genérico',  # Será identificado pelo OCR processor
                        'quantidade': produto_html.get('quantidade', 'un'),
                        'preco': produto_html.get('preco', 0),
                        'preco_oferta': produto_html.get('preco', 0),
                        'mercado': MERCADOS[mercado_key]['nome'],
                        'url_fonte': MERCADOS[mercado_key].get('url', ''),
                        'data_extracao': datetime.now().strftime('%Y-%m-%d')
                    }
                    
                    # Tentar identificar marca e segmento usando OCR processor
                    if produto_normalizado['produto']:
                        # Usar método de identificação de segmento
                        produto_normalizado['segmento'] = ocr.identificar_segmento(produto_normalizado['produto'])
                        
                        # Tentar identificar marca no nome do produto
                        nome_lower = produto_normalizado['produto'].lower()
                        marcas_comuns = ['tio joao', 't. joao', 'italac', 'omo', 'sadia', 'coca cola', 'nestle']
                        for marca_cand in marcas_comuns:
                            if marca_cand in nome_lower:
                                produto_normalizado['marca'] = marca_cand.title()
                                break
                    
                    if produto_normalizado['produto'] and produto_normalizado['preco'] > 0:
                        todos_produtos.append(produto_normalizado)
        
        # Processar imagens com OCR (encartes em PDF/imagem)
        for mercado in ['guanabara', 'mundial', 'supermarket', 'prezunic']:
            produtos_ocr = ocr.processar_imagens_mercado(mercado.title())
            todos_produtos.extend(produtos_ocr)
        
        # Salvar em CSV
        if todos_produtos:
            df = pd.DataFrame(todos_produtos)
            csv_path = os.path.join(CSV_DIR, f"produtos_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv")
            df.to_csv(csv_path, index=False, encoding='utf-8-sig')
            print(f"\n✓ CSV salvo: {csv_path}")
            print(f"  Total de produtos salvos: {len(df)}")
            
            # Salvar também em Excel
            try:
                excel_path = os.path.join(DATA_DIR, 'excel', f"produtos_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx")
                os.makedirs(os.path.dirname(excel_path), exist_ok=True)
                with pd.ExcelWriter(excel_path, engine='openpyxl') as writer:
                    df.to_excel(writer, sheet_name='Produtos', index=False)
                print(f"✓ Excel salvo: {excel_path}")
            except Exception as e:
                print(f"⚠ Erro ao salvar Excel: {e}")
            
            # Atualizar comparador
            comparador.carregar_dados(csv_path)
        else:
            print("\n⚠ NENHUM PRODUTO ENCONTRADO!")
            print("  Verifique os logs acima para identificar o problema.")
        
        return jsonify({
            'success': True,
            'message': f'Scraping concluído. {len(todos_produtos)} produtos encontrados.',
            'produtos': len(todos_produtos),
            'arquivo_csv': csv_path if todos_produtos else None
        })
    except Exception as e:
        import traceback
        traceback.print_exc()
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
    """Gera tabela comparativa de preços no formato solicitado
    Tenta primeiro ler do Google Sheets, depois dos CSVs locais"""
    try:
        # Tentar ler do Google Sheets primeiro
        print("=" * 60)
        print("Tentando ler do Google Sheets...")
        print("=" * 60)
        try:
            tabela_google = ler_google_sheets()
            print(f"Resultado do Google Sheets: {len(tabela_google) if tabela_google else 0} produtos")
            if tabela_google and len(tabela_google) > 0:
                print("=" * 60)
                print("SUCESSO! Retornando dados do Google Sheets")
                print(f"Total: {len(tabela_google)} produtos")
                print("=" * 60)
                return jsonify({
                    'success': True,
                    'tabela': tabela_google,
                    'fonte': 'Google Sheets',
                    'total': len(tabela_google)
                })
            else:
                print("=" * 60)
                print("AVISO: Google Sheets retornou vazio")
                print("Usando fallback para CSV local")
                print("=" * 60)
        except Exception as e:
            print("=" * 60)
            print(f"ERRO ao ler Google Sheets: {e}")
            print("=" * 60)
            import traceback
            traceback.print_exc()
            # Continuar para tentar CSVs locais
        
        # Fallback: ler dos CSVs locais
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
        
        # Gerar tabela comparativa: uma linha por (segmento, produto, marca, quantidade, mercado)
        # para que o frontend possa assimilar o mesmo produto de vários mercados em uma única linha.
        tabela = []
        try:
            grupos = df.groupby(['segmento', 'produto', 'marca', 'quantidade'], dropna=False)
            
            for (segmento, produto, marca, qtd), grupo in grupos:
                if grupo.empty:
                    continue
                produto_str = str(produto) if not pd.isna(produto) else 'Produto'
                marca_str = str(marca) if not pd.isna(marca) else 'Genérico'
                marca_final, tipo = normalizar_marca_e_tipo(marca_str, produto_str)
                # Uma linha por mercado onde o produto existe (permite comparação lado a lado no frontend)
                for _, row in grupo.iterrows():
                    preco_valor = row['preco']
                    if pd.isna(preco_valor) or (isinstance(preco_valor, (int, float)) and preco_valor <= 0):
                        continue
                    preco_formatado = f"R$ {float(preco_valor):.2f}".replace('.', ',')
                    mercado_nome = str(row['mercado']) if not pd.isna(row['mercado']) else 'Desconhecido'
                    url_mercado = str(row.get('url_fonte', '')) if not pd.isna(row.get('url_fonte', '')) else ''
                    if not url_mercado:
                        for key, mercado_info in MERCADOS.items():
                            if mercado_info['nome'].lower() == mercado_nome.lower():
                                url_mercado = mercado_info['url']
                                break
                    tabela.append({
                        'Segmento': str(segmento) if not pd.isna(segmento) else 'Outros',
                        'Produto': produto_str,
                        'Marca': marca_final,
                        'Tipo': tipo,
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
            'total': len(tabela_ordenada),
            'fonte': 'CSV Local'
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

def corrigir_encoding(texto):
    """Corrige erros de encoding comuns em textos"""
    try:
        # Verificar se é None, NaN ou vazio
        if texto is None:
            return texto
        if hasattr(pd, 'isna') and pd.isna(texto):
            return texto
        if not texto:
            return texto
        
        # Converter para string de forma segura
        if not isinstance(texto, str):
            texto_str = str(texto)
        else:
            texto_str = texto
        
        # Correções de encoding (ISO-8859-1 interpretado como UTF-8)
        correcoes = {
            'Ã¡': 'á', 'Ã©': 'é', 'Ã­': 'í', 'Ã³': 'ó', 'Ãº': 'ú',
            'Ã£': 'ã', 'Ã§': 'ç', 'Ã¢': 'â', 'Ãª': 'ê', 'Ã´': 'ô',
            'Ã ': 'à', 'Ã‰': 'É', 'Ã"': 'Á', 'Ã\'': 'Í', 'Ã"': 'Ó',
            'Ãš': 'Ú', 'Ãƒ': 'Ã', 'Ã‡': 'Ç', 'Ã‚': 'Â', 'ÃŠ': 'Ê',
            'Ã"': 'Ô', 'Ã€': 'À', 'Ã¼': 'ü', 'Ãœ': 'Ü', 'Ã±': 'ñ',
            'Ã\'': 'Ñ',
            # Correções específicas mencionadas
            'Ã¡gua': 'Água', 'LaticÃ­nios': 'Laticínios', 'FilÃ©': 'Filé',
            'atÃ£o': 'Latão', 'AÃ§ougue': 'Açougue', 'YpÃª': 'Ypê',
            'SABÃ': 'Sabão', 'TÃ´nica': 'Tônica', 'PiraquÃª': 'Piraquê',
            'Ã­quido': 'Líquido', 'BebÃª': 'Bebê', 'AÃ§Ãºcar': 'Açúcar',
            'Ã¡ctea': 'Láctea', 'CafÃ©': 'Café', 'CoraÃ§Ãµes': 'Corações',
            'UniÃ£o': 'União', 'FeijÃ£o': 'Feijão', 'FarinÃ¡ceos': 'Farináceos',
            'FÃ¡cil': 'Fácil', 'SanitÃ¡ria': 'Sanitária'
        }
        
        for erro, correto in correcoes.items():
            texto_str = texto_str.replace(erro, correto)
        
        return texto_str
    except Exception as e:
        # Se houver qualquer erro, retornar o texto original
        print(f"Aviso: Erro ao corrigir encoding: {e}")
        return texto if texto is not None else ''


# Produtos base para extrair "Tipo" (complemento). Ordenados do mais curto ao mais longo
# para que o primeiro match seja a base mínima e o resto seja o tipo (ex: "Queijo Minas" -> "Frescal").
PRODUTOS_BASE_TIPO = [
    'Queijo Minas', 'Creme Dental', 'Escova Dental', 'Churrasqueira a Carvão', 'Carvão Briquete',
    'Carvão', 'Colgate Total', 'Colgate', 'Creme Dental Colgate', 'Creme Dental Colgate Total',
    'Escova Dental Colgate', 'Queijo Minas Frescal', 'Queijo Minas Sol com Sal', 'Queijo Minas Frescal Sol',
]


def extrair_tipo(produto):
    """Extrai o complemento (Tipo) do nome do produto. Ex: 'Queijo Minas Frescal' -> 'Frescal'."""
    if not produto or not isinstance(produto, str):
        return ''
    p = produto.strip()
    # Ordenar por tamanho crescente para pegar a base mínima e o resto como tipo
    bases_ordenadas = sorted(PRODUTOS_BASE_TIPO, key=len)
    for base in bases_ordenadas:
        if p.lower().startswith(base.lower()):
            resto = p[len(base):].strip()
            if resto:
                return resto
            return ''
    return ''


# Simplificação de marcas longas para exibição (ex.: "Padrão Regina Inteiro" -> "Padrão Regina")
SIMPLIFICAR_MARCA = {
    'padrão regina inteiro': 'Padrão Regina',
    'padrao regina inteiro': 'Padrão Regina',
    'porto alegre pequeno': 'Porto Alegre',
    'bom pastor pequeno': 'Bom Pastor',
    'padrão regina': 'Padrão Regina',
    'padrao regina': 'Padrão Regina',
}


def simplificar_marca(marca):
    """Simplifica o nome da marca para exibição."""
    if not marca or not isinstance(marca, str):
        return marca or ''
    key = marca.strip().lower()
    return SIMPLIFICAR_MARCA.get(key, marca.strip())


# Marcas conhecidas para extrair do texto do produto quando Marca = Genérico (ordem: mais específica primeiro)
MARCAS_CONHECIDAS = [
    'colgate total', 'colgate', 'oral b', 'sensodyne', 'close up', 'crest', 'sorriso',
    'montana', 'ypê', 'ype', 'nestlé', 'nestle', 'danone', 'vigor', 'italac', 'parmalat',
    'tio joão', 't. joão', 'tio joao', 't. joao', 'dona elza', 'dona elsa', 'camil',
    'omo', 'ariel', 'sadia', 'perdigão', 'perdigao', 'seara', 'coca cola', 'coca-cola',
    'pepsi', 'guaraná', 'guarana', 'monteminas', 'brilhante', 'bom pastor', 'porto alegre',
    'padrão regina', 'padrao regina', 'fort', 'onar', 'mor', 'flúor', 'fluor',
]


def extrair_marca_do_produto(produto):
    """Se a marca for Genérico, tenta extrair a marca do nome do produto."""
    if not produto or not isinstance(produto, str):
        return None
    nome_lower = produto.lower()
    for marca in MARCAS_CONHECIDAS:
        if marca in nome_lower:
            # Normalizar exibição
            if marca in ('t. joão', 't. joao'):
                return 'Tio João'
            if marca in ('dona elsa',):
                return 'Dona Elza'
            if marca in ('nestle', 'nestlé'):
                return 'Nestlé'
            if marca in ('padrao regina', 'padrão regina'):
                return 'Padrão Regina'
            if marca in ('perdigao', 'perdigão'):
                return 'Perdigão'
            if marca in ('guarana', 'guaraná'):
                return 'Guaraná'
            if marca in ('ype', 'ypê'):
                return 'Ypê'
            if marca in ('fluor', 'flúor'):
                return 'Flúor'
            return marca.title()
    return None


def normalizar_marca_e_tipo(marca, produto):
    """Retorna (marca_final, tipo). Se marca for Genérico, tenta extrair marca do produto. Aplica simplificação."""
    marca_str = str(marca).strip() if marca and not pd.isna(marca) else 'Genérico'
    produto_str = str(produto).strip() if produto and not pd.isna(produto) else ''
    if not marca_str or marca_str.lower() == 'genérico' or marca_str.lower() == 'generico':
        extraida = extrair_marca_do_produto(produto_str)
        if extraida:
            marca_str = extraida
    marca_final = simplificar_marca(marca_str)
    tipo = extrair_tipo(produto_str)
    return marca_final, tipo


def ler_google_sheets():
    """Lê dados da planilha do Google Sheets via API pública"""
    try:
        # ID da planilha do Google Sheets
        sheet_id = '1gWYvYjPrTNAvEXkeYTh5SjnyWMir371D_5vTmacWAO8'
        
        # URL para exportar como CSV (formato público)
        url = f'https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv&gid=0'
        
        print(f"Lendo Google Sheets: {url}")
        
        # Fazer requisição (desabilitar verificação SSL se necessário para ambientes corporativos)
        # Em ambientes corporativos, geralmente precisa desabilitar SSL
        import urllib3
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
        
        print("Fazendo requisição HTTP...")
        try:
            # Tentar primeiro sem SSL (mais comum em ambientes corporativos)
            response = requests.get(url, timeout=20, verify=False)
            # Garantir encoding UTF-8
            response.encoding = 'utf-8'
            print(f"Resposta recebida (sem SSL): Status {response.status_code}")
            print(f"Tamanho da resposta: {len(response.text)} caracteres")
        except Exception as req_error:
            # Se falhar, tentar com SSL
            print(f"Erro sem SSL: {req_error}")
            print("Tentando com SSL...")
            try:
                response = requests.get(url, timeout=20, verify=True)
                # Garantir encoding UTF-8
                response.encoding = 'utf-8'
                print(f"Resposta recebida (com SSL): Status {response.status_code}")
                print(f"Tamanho da resposta: {len(response.text)} caracteres")
            except Exception as ssl_error:
                print(f"Erro com SSL: {ssl_error}")
                raise
        
        response.raise_for_status()
        
        # Ler CSV com encoding UTF-8
        print("Lendo CSV...")
        from io import StringIO
        # Garantir que o texto está em UTF-8
        texto_csv = response.text
        if isinstance(texto_csv, bytes):
            texto_csv = texto_csv.decode('utf-8', errors='replace')
        df = pd.read_csv(StringIO(texto_csv), encoding='utf-8')
        print(f"DataFrame criado: {len(df)} linhas, {len(df.columns)} colunas")
        
        # Normalizar nomes das colunas
        df.columns = df.columns.str.strip()
        print(f"Colunas normalizadas: {list(df.columns)}")
        print(f"Tipo das colunas: {[type(c).__name__ for c in df.columns]}")
        
        # Usar os nomes das colunas diretamente do DataFrame (mais simples e confiável)
        # Verificar se temos pelo menos as colunas principais
        colunas_df_lower = [c.lower() for c in df.columns]
        colunas_necessarias_lower = ['segmento', 'produto', 'marca', 'qtd', 'menor preço', 'mercado', 'link']
        
        colunas_faltantes = []
        for col_nec in colunas_necessarias_lower:
            encontrada = False
            for col_df_lower in colunas_df_lower:
                # Comparação normalizada (remove acentos e espaços)
                col_nec_norm = col_nec.lower().replace('ç', 'c').replace('ã', 'a').replace('á', 'a').replace('é', 'e').replace('í', 'i').replace('ó', 'o').replace('ú', 'u')
                col_df_norm = col_df_lower.lower().replace('ç', 'c').replace('ã', 'a').replace('á', 'a').replace('é', 'e').replace('í', 'i').replace('ó', 'o').replace('ú', 'u')
                if col_nec_norm == col_df_norm:
                    encontrada = True
                    break
            if not encontrada:
                colunas_faltantes.append(col_nec)
        
        if colunas_faltantes:
            print(f"AVISO: Algumas colunas podem ter nomes diferentes: {colunas_faltantes}")
            print(f"Mas vamos tentar usar as colunas disponíveis: {list(df.columns)}")
        
        # Criar mapeamento simples usando os nomes reais das colunas
        # Assumir ordem padrão: Segmento, Produto, Marca, Qtd, Menor Preço, Mercado, Link
        col_map = {}
        if len(df.columns) >= 7:
            # Tentar mapear por posição se os nomes não baterem
            possiveis_nomes = [
                ['segmento', 'produto', 'marca', 'qtd', 'menor preço', 'mercado', 'link'],
                ['Segmento', 'Produto', 'Marca', 'Qtd', 'Menor Preço', 'Mercado', 'Link']
            ]
            
            # Primeiro tentar por nome exato
            for i, col_df in enumerate(df.columns):
                col_df_lower = col_df.lower()
                if i < len(possiveis_nomes[0]):
                    col_map[possiveis_nomes[0][i]] = col_df
            
            print(f"Mapeamento criado: {col_map}")
        else:
            print(f"ERRO: DataFrame tem apenas {len(df.columns)} colunas, esperado 7")
            return []
        
        print("Todas as colunas mapeadas!")
        
        # Converter para formato da tabela usando mapeamento ou ordem
        print("Convertendo para formato da tabela...")
        tabela = []
        
        # Usar ordem das colunas se mapeamento não funcionar
        col_segmento = col_map.get('segmento', df.columns[0] if len(df.columns) > 0 else 'Segmento')
        col_produto = col_map.get('produto', df.columns[1] if len(df.columns) > 1 else 'Produto')
        col_marca = col_map.get('marca', df.columns[2] if len(df.columns) > 2 else 'Marca')
        col_qtd = col_map.get('qtd', df.columns[3] if len(df.columns) > 3 else 'Qtd')
        col_preco = col_map.get('menor preço', df.columns[4] if len(df.columns) > 4 else 'Menor Preço')
        col_mercado = col_map.get('mercado', df.columns[5] if len(df.columns) > 5 else 'Mercado')
        col_link = col_map.get('link', df.columns[6] if len(df.columns) > 6 else 'Link')
        
        print(f"Usando colunas: Segmento={col_segmento}, Produto={col_produto}, Preco={col_preco}")
        
        for idx, row in df.iterrows():
            # Verificar se produto está vazio
            try:
                produto_val = row[col_produto]
                if pd.isna(produto_val) or str(produto_val).strip() == '':
                    continue
            except:
                continue
            
            # Aplicar correção de encoding aos campos de texto
            segmento = corrigir_encoding(row[col_segmento]) if not pd.isna(row[col_segmento]) else 'Outros'
            produto = corrigir_encoding(row[col_produto])
            marca = corrigir_encoding(row[col_marca]) if not pd.isna(row[col_marca]) else 'Genérico'
            qtd = corrigir_encoding(row[col_qtd]) if not pd.isna(row[col_qtd]) else 'un'
            preco = str(row[col_preco]) if not pd.isna(row[col_preco]) else 'R$ 0,00'
            mercado = corrigir_encoding(row[col_mercado]) if not pd.isna(row[col_mercado]) else 'Desconhecido'
            link = str(row[col_link]) if not pd.isna(row[col_link]) else ''
            marca_final, tipo = normalizar_marca_e_tipo(marca, produto)
            tabela.append({
                'Segmento': str(segmento),
                'Produto': str(produto),
                'Marca': marca_final,
                'Tipo': tipo,
                'Qtd': str(qtd),
                'Menor Preço': preco,
                'Mercado': str(mercado),
                'Link': link
            })
            
            # Log a cada 20 produtos
            if (idx + 1) % 20 == 0:
                print(f"  Processados {idx + 1} linhas...")
        
        print(f"SUCESSO! Lidos {len(tabela)} produtos do Google Sheets")
        return tabela
        
    except Exception as e:
        print(f"Erro ao ler Google Sheets: {e}")
        import traceback
        traceback.print_exc()
        return []

if __name__ == '__main__':
    print("Iniciando servidor Flask...")
    print("API disponível em http://localhost:5000")
    app.run(debug=True, host='0.0.0.0', port=5000)


