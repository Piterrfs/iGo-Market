import pytesseract
from PIL import Image
import re
import pandas as pd
from datetime import datetime
import os
from config import OCR_CONFIG, CSV_DIR, IMAGES_DIR
import cv2
import numpy as np

class OCRProcessor:
    def __init__(self):
        # Configurar caminho do Tesseract se necessário (Windows)
        # pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
        pass
    
    def preprocess_image(self, image_path):
        """Melhora a qualidade da imagem para OCR"""
        img = cv2.imread(image_path)
        
        # Converter para escala de cinza
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        
        # Aplicar threshold para melhorar contraste
        _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        
        # Redimensionar se muito pequeno
        height, width = thresh.shape
        if width < 800:
            scale = 800 / width
            new_width = int(width * scale)
            new_height = int(height * scale)
            thresh = cv2.resize(thresh, (new_width, new_height), interpolation=cv2.INTER_CUBIC)
        
        return thresh
    
    def extract_text(self, image_path):
        """Extrai texto de uma imagem usando OCR"""
        try:
            # Pré-processar imagem
            processed_img = self.preprocess_image(image_path)
            
            # OCR com configurações otimizadas
            custom_config = f'-l {OCR_CONFIG["lang"]} --psm {OCR_CONFIG["psm"]}'
            text = pytesseract.image_to_string(processed_img, config=custom_config)
            
            return text
        except Exception as e:
            print(f"Erro ao processar OCR em {image_path}: {e}")
            return ""
    
    def identificar_segmento(self, produto_nome):
        """Identifica o segmento do produto baseado no nome"""
        produto_lower = produto_nome.lower()
        
        segmentos = {
            'Mercearia': ['arroz', 'feijao', 'feijão', 'macarrao', 'macarrão', 'massa', 'oleo', 'óleo', 'acucar', 'açúcar', 'sal', 'farinha', 'biscoito', 'bolacha'],
            'Açougue': ['carne', 'frango', 'peixe', 'alcatra', 'patinho', 'contra file', 'contra-filé', 'picanha', 'linguiça', 'linguiça', 'salsicha', 'hamburguer', 'hambúrguer'],
            'Laticínios': ['leite', 'queijo', 'manteiga', 'requeijao', 'requeijão', 'iogurte', 'yogurte', 'creme de leite', 'nata'],
            'Hortifruti': ['banana', 'maça', 'maçã', 'laranja', 'tomate', 'cebola', 'batata', 'alface', 'couve', 'repolho', 'cenoura', 'abobora', 'abóbora'],
            'Limpeza': ['sabao', 'sabão', 'detergente', 'amaciante', 'agua sanitaria', 'água sanitária', 'desinfetante', 'esponja', 'papel higienico', 'papel higiênico'],
            'Bebidas': ['refrigerante', 'suco', 'agua', 'água', 'cerveja', 'vinho', 'cafe', 'café', 'cha', 'chá'],
            'Padaria': ['pao', 'pão', 'bolo', 'torta', 'doce', 'biscoito', 'bolacha']
        }
        
        for segmento, palavras_chave in segmentos.items():
            for palavra in palavras_chave:
                if palavra in produto_lower:
                    return segmento
        
        return 'Outros'
    
    def limpar_dados_mercado(self, texto_extraido, mercado_nome=None):
        """Extrai e limpa dados do texto OCR conforme especificação"""
        produtos = []
        
        # Padrões regex melhorados para identificar produtos
        # Formato esperado: PRODUTO MARCA QUANTIDADE PREÇO ou variações
        linhas = texto_extraido.split('\n')
        
        # Marcações de marcas conhecidas (expandida)
        marcas_comuns = [
            'tio joao', 't. joao', 'tio joão', 't. joão', 'dona elza', 'dona elsa',
            'italac', 'parmalat', 'nestle', 'nestlé', 'danone', 'vigor',
            'omo', 'ariel', 'comfort', 'downy', 'ype', 'veja', 'pinho sol',
            'sadia', 'perdigao', 'perdigão', 'seara', 'friboi', 'swift',
            'coca cola', 'coca-cola', 'pepsi', 'guarana', 'sprite', 'fanta',
            'maggi', 'knorr', 'hellmanns', 'maionese', 'heinz', 'quero',
            'bombril', 'assolan', 'vanish', 'cif', 'ajax'
        ]
        
        for linha in linhas:
            linha = linha.strip()
            if not linha or len(linha) < 5:
                continue
            
            # Padrão para preço: R$ XX,XX ou R$XX,XX ou XX,XX
            preco_patterns = [
                r'R\$\s*(\d+)[,.](\d{2})',
                r'(\d+)[,.](\d{2})\s*R\$',
                r'(\d+)[,.](\d{2})\s*reais',
                r'preco[:\s]*(\d+)[,.](\d{2})',
                r'preço[:\s]*(\d+)[,.](\d{2})'
            ]
            
            preco_match = None
            for pattern in preco_patterns:
                preco_match = re.search(pattern, linha, re.IGNORECASE)
                if preco_match:
                    break
            
            if not preco_match:
                continue
            
            preco = float(f"{preco_match.group(1)}.{preco_match.group(2)}")
            
            # Remover preço da linha para processar o resto
            linha_sem_preco = re.sub(r'R\$\s*\d+[,.]\d{2}|\d+[,.]\d{2}\s*R\$|\d+[,.]\d{2}', '', linha, flags=re.IGNORECASE).strip()
            
            # Padrão para quantidade: Xkg, Xg, XL, Xml, etc.
            qtd_patterns = [
                r'(\d+(?:[,.]\d+)?)\s*(kg|g|L|l|ml|un|pct|pac|und|unid|unidade)',
                r'(\d+(?:[,.]\d+)?)\s*(quilo|quilos|grama|gramas|litro|litros|mililitro|mililitros)'
            ]
            
            quantidade = None
            for pattern in qtd_patterns:
                qtd_match = re.search(pattern, linha_sem_preco, re.IGNORECASE)
                if qtd_match:
                    num = qtd_match.group(1).replace(',', '.')
                    unidade = qtd_match.group(2).lower()
                    # Normalizar unidade
                    if unidade in ['quilo', 'quilos']:
                        unidade = 'kg'
                    elif unidade in ['grama', 'gramas']:
                        unidade = 'g'
                    elif unidade in ['litro', 'litros']:
                        unidade = 'L'
                    elif unidade in ['mililitro', 'mililitros']:
                        unidade = 'ml'
                    elif unidade in ['un', 'und', 'unid', 'unidade', 'pct', 'pac']:
                        unidade = 'un'
                    quantidade = f"{num}{unidade}"
                    linha_sem_preco = re.sub(pattern, '', linha_sem_preco, flags=re.IGNORECASE).strip()
                    break
            
            # Identificar marca
            marca = None
            produto_nome = linha_sem_preco
            
            for marca_candidata in marcas_comuns:
                if marca_candidata.lower() in linha_sem_preco.lower():
                    # Normalizar nome da marca
                    if marca_candidata == 't. joao' or marca_candidata == 't. joão':
                        marca = 'Tio João'
                    elif marca_candidata == 'dona elsa':
                        marca = 'Dona Elza'
                    else:
                        marca = marca_candidata.title()
                    # Remover marca do nome do produto
                    produto_nome = re.sub(marca_candidata, '', linha_sem_preco, flags=re.IGNORECASE).strip()
                    break
            
            # Se não encontrou marca conhecida, tentar padrões comuns
            if not marca:
                # Padrão: última palavra pode ser marca (se começar com maiúscula)
                palavras = produto_nome.split()
                if len(palavras) > 1 and palavras[-1][0].isupper():
                    marca = palavras[-1]
                    produto_nome = ' '.join(palavras[:-1])
                else:
                    marca = 'Genérico'
            
            # Limpar e normalizar nome do produto
            produto_nome = re.sub(r'\s+', ' ', produto_nome).strip()
            produto_nome = produto_nome.title()
            
            # Identificar segmento
            segmento = self.identificar_segmento(produto_nome)
            
            if produto_nome and preco > 0:
                produtos.append({
                    'segmento': segmento,
                    'produto': produto_nome,
                    'marca': marca,
                    'quantidade': quantidade or 'un',
                    'preco': preco,
                    'preco_oferta': preco,  # Mesmo valor para compatibilidade
                    'mercado': mercado_nome or 'Desconhecido',
                    'data_extracao': datetime.now().strftime('%Y-%m-%d')
                })
        
        return produtos
    
    def processar_imagens_mercado(self, mercado_nome):
        """Processa todas as imagens de um mercado"""
        produtos_todos = []
        
        # Buscar imagens do mercado (incluindo PDFs convertidos)
        for filename in os.listdir(IMAGES_DIR):
            if mercado_nome.lower() in filename.lower() and (filename.endswith('.jpg') or filename.endswith('.png') or filename.endswith('.jpeg')):
                image_path = os.path.join(IMAGES_DIR, filename)
                print(f"Processando {filename}...")
                
                texto = self.extract_text(image_path)
                produtos = self.limpar_dados_mercado(texto, mercado_nome)
                produtos_todos.extend(produtos)
        
        return produtos_todos
    
    def normalizar_produto(self, produto, marca, quantidade):
        """Cria chave única para comparação - normaliza variações como 'Arroz 5kg T. Joao' e 'Arroz Tio João 5kg'"""
        # Normalizar strings - remover acentos e caracteres especiais
        produto_norm = re.sub(r'[^a-z0-9]', '', produto.lower())
        
        # Normalizar marca (ex: 't. joao' -> 'tiojoao', 'tio joão' -> 'tiojoao')
        marca_norm = re.sub(r'[^a-z0-9]', '', marca.lower())
        # Mapear variações comuns
        marca_map = {
            'tjoao': 'tiojoao',
            'tjoão': 'tiojoao',
            'donaelza': 'donaelza',
            'donaelsa': 'donaelza'
        }
        marca_norm = marca_map.get(marca_norm, marca_norm)
        
        # Normalizar quantidade (ex: '5kg' -> '5kg', '5 kg' -> '5kg')
        qtd_norm = re.sub(r'[^a-z0-9]', '', quantidade.lower())
        
        return f"{produto_norm}-{marca_norm}-{qtd_norm}"

