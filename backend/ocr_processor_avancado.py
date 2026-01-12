"""
OCR Processor Avançado - Lida com diferentes formatos e posições
Usa múltiplas estratégias para extrair dados de layouts variados
"""
import pytesseract
from PIL import Image
import re
import pandas as pd
from datetime import datetime
import os
from config import OCR_CONFIG, IMAGES_DIR
import cv2
import numpy as np

class OCRProcessorAvancado:
    def __init__(self):
        """Inicializa processador OCR avançado"""
        self.marcas_comuns = [
            'tio joao', 't. joao', 'tio joão', 't. joão', 'dona elza', 'dona elsa',
            'italac', 'parmalat', 'nestle', 'nestlé', 'danone', 'vigor',
            'omo', 'ariel', 'comfort', 'downy', 'ype', 'veja', 'pinho sol',
            'sadia', 'perdigao', 'perdigão', 'seara', 'friboi', 'swift',
            'coca cola', 'coca-cola', 'pepsi', 'guarana', 'sprite', 'fanta',
            'maggi', 'knorr', 'hellmanns', 'maionese', 'heinz', 'quero',
            'bombril', 'assolan', 'vanish', 'cif', 'ajax', 'antarctica',
            'heineken', 'brahma', 'skol', 'stella artois', 'eisberg',
            'dog chow', 'whiskas', 'pedigree', 'royal canin', 'golden',
            'pipicat', 'wyda', 'duracell', 'rayovac'
        ]
    
    def detectar_regioes_produto(self, image_path):
        """
        Detecta regiões de produtos na imagem usando análise de contornos
        Útil para layouts em grid/cards
        """
        img = cv2.imread(image_path)
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        
        # Aplicar threshold
        _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        
        # Encontrar contornos (possíveis cards de produtos)
        contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        # Filtrar contornos por tamanho (produtos geralmente têm tamanho similar)
        regions = []
        for contour in contours:
            x, y, w, h = cv2.boundingRect(contour)
            area = w * h
            # Filtrar por área mínima e máxima (ajustar conforme necessário)
            if 5000 < area < 50000:  # Área típica de um card de produto
                regions.append((x, y, w, h))
        
        return regions
    
    def extrair_texto_regiao(self, image_path, x, y, w, h):
        """Extrai texto de uma região específica da imagem"""
        img = cv2.imread(image_path)
        roi = img[y:y+h, x:x+w]  # Region of Interest
        
        # Pré-processar ROI
        gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
        _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        
        # OCR na região
        custom_config = f'-l {OCR_CONFIG["lang"]} --psm 7'  # PSM 7 = linha única
        text = pytesseract.image_to_string(thresh, config=custom_config)
        return text.strip()
    
    def processar_layout_tabela(self, texto_extraido):
        """
        Processa layout em formato de tabela
        Detecta colunas e linhas
        """
        linhas = texto_extraido.split('\n')
        produtos = []
        
        # Detectar padrão de tabela (múltiplas colunas)
        for i, linha in enumerate(linhas):
            # Se linha tem múltiplos preços ou múltiplos produtos, pode ser tabela
            precos = re.findall(r'R\$\s*(\d+)[,.](\d{2})', linha)
            if len(precos) > 1:
                # Processar cada coluna
                colunas = linha.split()  # Dividir por espaços
                # Tentar identificar produtos em cada coluna
                pass
        
        return produtos
    
    def processar_layout_card(self, texto_extraido):
        """
        Processa layout em formato de cards (produtos em blocos)
        Cada card pode ter produto, marca, quantidade e preço em posições variadas
        """
        produtos = []
        
        # Dividir em blocos (cards separados por linhas vazias ou padrões)
        blocos = re.split(r'\n\s*\n', texto_extraido)
        
        for bloco in blocos:
            linhas_bloco = bloco.split('\n')
            produto_info = {}
            
            # Buscar preço em qualquer linha do bloco
            for linha in linhas_bloco:
                preco_match = re.search(r'R\$\s*(\d+)[,.](\d{2})', linha)
                if preco_match:
                    produto_info['preco'] = float(f"{preco_match.group(1)}.{preco_match.group(2)}")
                    break
            
            # Buscar quantidade em qualquer linha
            for linha in linhas_bloco:
                qtd_match = re.search(r'(\d+(?:[,.]\d+)?)\s*(kg|g|L|l|ml|un|pct|pac)', linha, re.IGNORECASE)
                if qtd_match:
                    produto_info['quantidade'] = f"{qtd_match.group(1)}{qtd_match.group(2).lower()}"
                    break
            
            # Buscar marca em qualquer linha
            for linha in linhas_bloco:
                for marca in self.marcas_comuns:
                    if marca.lower() in linha.lower():
                        produto_info['marca'] = marca.title()
                        # Remover marca da linha para obter produto
                        produto_info['produto'] = re.sub(marca, '', linha, flags=re.IGNORECASE).strip()
                        break
                if 'marca' in produto_info:
                    break
            
            # Se encontrou preço, adicionar produto
            if 'preco' in produto_info:
                produtos.append(produto_info)
        
        return produtos
    
    def processar_layout_linha(self, texto_extraido):
        """
        Processa layout em formato de linha (tudo em uma linha)
        Formato: PRODUTO MARCA QTD PREÇO (ordem variável)
        """
        produtos = []
        linhas = texto_extraido.split('\n')
        
        for linha in linhas:
            linha = linha.strip()
            if not linha or len(linha) < 5:
                continue
            
            produto_info = {}
            
            # Múltiplos padrões de preço (diferentes posições)
            preco_patterns = [
                r'R\$\s*(\d+)[,.](\d{2})',  # R$ no início
                r'(\d+)[,.](\d{2})\s*R\$',  # R$ no final
                r'(\d+)[,.](\d{2})\s*reais',  # "reais" no final
                r'preco[:\s]*(\d+)[,.](\d{2})',  # "preço: XX,XX"
                r'(\d+)[,.](\d{2})',  # Apenas número (último recurso)
            ]
            
            preco_match = None
            for pattern in preco_patterns:
                preco_match = re.search(pattern, linha, re.IGNORECASE)
                if preco_match:
                    produto_info['preco'] = float(f"{preco_match.group(1)}.{preco_match.group(2)}")
                    # Remover preço da linha
                    linha = re.sub(pattern, '', linha, flags=re.IGNORECASE).strip()
                    break
            
            if not preco_match:
                continue
            
            # Múltiplos padrões de quantidade (diferentes posições)
            qtd_patterns = [
                r'(\d+(?:[,.]\d+)?)\s*(kg|g|L|l|ml|un|pct|pac|und|unid)',
                r'(\d+(?:[,.]\d+)?)\s*(quilo|quilos|grama|gramas|litro|litros)',
                r'(\d+)\s*x\s*(\d+)\s*(g|kg|ml|L)',  # Ex: 4 x 250ml
            ]
            
            for pattern in qtd_patterns:
                qtd_match = re.search(pattern, linha, re.IGNORECASE)
                if qtd_match:
                    if len(qtd_match.groups()) == 3:  # Formato 4 x 250ml
                        num = int(qtd_match.group(1)) * int(qtd_match.group(2))
                        unidade = qtd_match.group(3).lower()
                        produto_info['quantidade'] = f"{num}{unidade}"
                    else:
                        num = qtd_match.group(1).replace(',', '.')
                        unidade = qtd_match.group(2).lower()
                        produto_info['quantidade'] = f"{num}{unidade}"
                    linha = re.sub(pattern, '', linha, flags=re.IGNORECASE).strip()
                    break
            
            # Buscar marca (pode estar em qualquer posição)
            marca_encontrada = None
            for marca in self.marcas_comuns:
                if marca.lower() in linha.lower():
                    marca_encontrada = marca.title()
                    linha = re.sub(marca, '', linha, flags=re.IGNORECASE).strip()
                    break
            
            produto_info['marca'] = marca_encontrada or 'Genérico'
            produto_info['produto'] = linha.strip() or 'Produto'
            
            produtos.append(produto_info)
        
        return produtos
    
    def processar_imagem_multiplas_estrategias(self, image_path, mercado_nome=None):
        """
        Processa imagem usando múltiplas estratégias para lidar com diferentes layouts
        """
        todos_produtos = []
        
        # Estratégia 1: OCR completo da imagem
        texto_completo = self.extract_text_completo(image_path)
        
        # Tentar diferentes estratégias de parsing
        estrategias = [
            ('layout_card', self.processar_layout_card),
            ('layout_linha', self.processar_layout_linha),
            ('layout_tabela', self.processar_layout_tabela),
        ]
        
        for nome_estrategia, funcao_processamento in estrategias:
            try:
                produtos = funcao_processamento(texto_completo)
                if produtos:
                    print(f"  Estrategia {nome_estrategia}: {len(produtos)} produtos encontrados")
                    todos_produtos.extend(produtos)
            except Exception as e:
                print(f"  Erro na estrategia {nome_estrategia}: {e}")
        
        # Estratégia 2: Detecção de regiões (se nenhuma estratégia anterior funcionou)
        if not todos_produtos:
            try:
                regions = self.detectar_regioes_produto(image_path)
                for x, y, w, h in regions:
                    texto_regiao = self.extrair_texto_regiao(image_path, x, y, w, h)
                    produtos_regiao = self.processar_layout_linha(texto_regiao)
                    todos_produtos.extend(produtos_regiao)
            except Exception as e:
                print(f"  Erro na deteccao de regioes: {e}")
        
        # Adicionar metadados
        for produto in todos_produtos:
            produto['mercado'] = mercado_nome or 'Desconhecido'
            produto['data_extracao'] = datetime.now().strftime('%Y-%m-%d')
            produto['segmento'] = self.identificar_segmento(produto.get('produto', ''))
        
        return todos_produtos
    
    def extract_text_completo(self, image_path):
        """Extrai todo o texto da imagem"""
        img = cv2.imread(image_path)
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        
        # Múltiplas configurações PSM para diferentes layouts
        textos = []
        for psm in [6, 11, 12]:  # 6=bloco, 11=sparse, 12=sparse com OSD
            try:
                custom_config = f'-l {OCR_CONFIG["lang"]} --psm {psm}'
                texto = pytesseract.image_to_string(thresh, config=custom_config)
                textos.append(texto)
            except:
                pass
        
        # Retornar o texto mais completo
        return max(textos, key=len) if textos else ""
    
    def identificar_segmento(self, produto_nome):
        """Identifica segmento do produto"""
        produto_lower = produto_nome.lower()
        
        segmentos = {
            'Mercearia': ['arroz', 'feijao', 'feijão', 'macarrao', 'macarrão', 'massa', 'oleo', 'óleo', 'acucar', 'açúcar', 'sal', 'farinha', 'biscoito', 'bolacha'],
            'Açougue': ['carne', 'frango', 'peixe', 'alcatra', 'patinho', 'contra file', 'contra-filé', 'picanha', 'linguiça', 'salsicha', 'hamburguer', 'hambúrguer'],
            'Laticínios': ['leite', 'queijo', 'manteiga', 'requeijao', 'requeijão', 'iogurte', 'yogurte', 'creme de leite', 'nata'],
            'Hortifruti': ['banana', 'maça', 'maçã', 'laranja', 'tomate', 'cebola', 'batata', 'alface', 'couve', 'repolho', 'cenoura', 'abobora', 'abóbora'],
            'Limpeza': ['sabao', 'sabão', 'detergente', 'amaciante', 'agua sanitaria', 'água sanitária', 'desinfetante', 'esponja', 'papel higienico', 'papel higiênico'],
            'Bebidas': ['refrigerante', 'suco', 'agua', 'água', 'cerveja', 'vinho', 'cafe', 'café', 'cha', 'chá'],
            'Pet Shop': ['racao', 'ração', 'petisco', 'areia', 'sache', 'sachê'],
            'Bazar': ['papel', 'pilha', 'bateria', 'fita', 'adesivo']
        }
        
        for segmento, palavras_chave in segmentos.items():
            for palavra in palavras_chave:
                if palavra in produto_lower:
                    return segmento
        
        return 'Outros'
