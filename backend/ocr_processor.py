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
        """Extrai texto de uma imagem usando OCR com múltiplas estratégias para capturar mais produtos"""
        textos = []
        try:
            # Pré-processar imagem
            processed_img = self.preprocess_image(image_path)
            
            # Estratégia 1: PSM 6 (bloco uniforme de texto) - padrão
            try:
                custom_config = f'-l {OCR_CONFIG["lang"]} --psm 6'
                texto1 = pytesseract.image_to_string(processed_img, config=custom_config)
                if texto1 and len(texto1.strip()) > 10:
                    textos.append(texto1)
            except:
                pass
            
            # Estratégia 2: PSM 11 (texto esparso) - para layouts complexos
            try:
                custom_config = f'-l {OCR_CONFIG["lang"]} --psm 11'
                texto2 = pytesseract.image_to_string(processed_img, config=custom_config)
                if texto2 and len(texto2.strip()) > 10:
                    textos.append(texto2)
            except:
                pass
            
            # Estratégia 3: PSM 3 (bloco totalmente automático) - fallback
            try:
                custom_config = f'-l {OCR_CONFIG["lang"]} --psm 3'
                texto3 = pytesseract.image_to_string(processed_img, config=custom_config)
                if texto3 and len(texto3.strip()) > 10:
                    textos.append(texto3)
            except:
                pass
            
            # Retornar o texto mais completo
            if textos:
                return max(textos, key=len)
            else:
                # Fallback: usar configuração padrão
                custom_config = f'-l {OCR_CONFIG["lang"]} --psm {OCR_CONFIG["psm"]}'
                return pytesseract.image_to_string(processed_img, config=custom_config)
        except Exception as e:
            print(f"Erro ao processar OCR em {image_path}: {e}")
            return ""
    
    def identificar_segmento(self, produto_nome):
        """Identifica o segmento do produto baseado no nome"""
        produto_lower = produto_nome.lower()
        
        segmentos = {
            'Mercearia': [
                'arroz', 'feijao', 'feijão', 'macarrao', 'macarrão', 'massa', 'oleo', 'óleo', 'acucar', 'açúcar', 
                'sal', 'farinha', 'biscoito', 'bolacha', 'açúcar', 'acucar', 'açucar', 'açucar cristal',
                'farinha de trigo', 'farinha de mandioca', 'polvilho', 'fermento', 'gelatina', 'pudim',
                'achocolatado', 'nescau', 'toddy', 'ovomaltine', 'leite em pó', 'leite em po',
                'café', 'cafe', 'café solúvel', 'cafe soluvel', 'chá', 'cha', 'mate', 'erva mate',
                'molho de tomate', 'extrato de tomate', 'polpa de tomate', 'milho', 'ervilha',
                'seleta', 'conserva', 'atum', 'sardinha', 'azeite', 'vinagre', 'mostarda',
                'ketchup', 'maionese', 'tempero', 'caldo', 'sazon', 'kitano'
            ],
            'Açougue': [
                'carne', 'frango', 'peixe', 'alcatra', 'patinho', 'contra file', 'contra-filé', 'picanha', 
                'linguiça', 'linguiça', 'salsicha', 'hamburguer', 'hambúrguer', 'bacon', 'presunto',
                'mortadela', 'salame', 'apresuntado', 'peito de frango', 'coxa', 'sobrecoxa',
                'filé de frango', 'file de frango', 'peito de peru', 'lombo', 'costela',
                'músculo', 'musculo', 'acém', 'acem', 'paleta', 'maminha', 'fraldinha',
                'carne moída', 'carne moida', 'carne de sol', 'charque', 'linguiça calabresa',
                'linguiça toscana', 'salsicha hot dog', 'salsicha vienna'
            ],
            'Laticínios': [
                'leite', 'queijo', 'manteiga', 'requeijao', 'requeijão', 'iogurte', 'yogurte', 
                'creme de leite', 'nata', 'leite condensado', 'leite condensado', 'chantilly',
                'queijo mussarela', 'queijo prato', 'queijo minas', 'queijo coalho', 'queijo ralado',
                'ricota', 'cottage', 'cream cheese', 'requeijão cremoso', 'margarina', 'manteiga',
                'iogurte grego', 'iogurte natural', 'bebida láctea', 'bebida lactea'
            ],
            'Hortifruti': [
                'banana', 'maça', 'maçã', 'laranja', 'tomate', 'cebola', 'batata', 'alface', 
                'couve', 'repolho', 'cenoura', 'abobora', 'abóbora', 'abobrinha', 'berinjela',
                'pimentão', 'pimentao', 'pimenta', 'alho', 'gengibre', 'limão', 'limao',
                'mamão', 'mamao', 'manga', 'abacaxi', 'melancia', 'melão', 'melao',
                'uva', 'morango', 'kiwi', 'pera', 'pêssego', 'pessego', 'ameixa',
                'brócolis', 'brocolis', 'couve-flor', 'couve flor', 'beterraba', 'rabanete',
                'rúcula', 'rucula', 'agrião', 'agriao', 'espinafre', 'salsa', 'cebolinha',
                'coentro', 'manjericão', 'manjericao'
            ],
            'Limpeza': [
                'sabao', 'sabão', 'detergente', 'amaciante', 'agua sanitaria', 'água sanitária', 
                'desinfetante', 'esponja', 'papel higienico', 'papel higiênico', 'sabão em pó',
                'sabao em po', 'sabão líquido', 'sabao liquido', 'sabonete', 'detergente',
                'água sanitária', 'agua sanitaria', 'cloro', 'multiuso', 'limpa vidros',
                'lustra móveis', 'lustra moveis', 'removedor', 'desengordurante', 'saponáceo',
                'saponaceo', 'veja multiuso', 'pinho sol', 'ajax', 'cif', 'brilhante',
                'qboa', 'minuano', 'santa clara', 'limpol', 'vanish', 'assolan',
                'saco de lixo', 'saco plastico', 'saco plástico', 'luvas', 'esponja de aço',
                'palha de aço', 'bombril', 'saco para lixo'
            ],
            'Bebidas': [
                'refrigerante', 'suco', 'agua', 'água', 'cerveja', 'vinho', 'cafe', 'café', 
                'cha', 'chá', 'água mineral', 'agua mineral', 'água com gás', 'agua com gas',
                'refrigerante cola', 'refrigerante guaraná', 'refrigerante laranja', 'refrigerante limão',
                'suco de laranja', 'suco de uva', 'suco de maracujá', 'suco de maracuja',
                'néctar', 'nectar', 'água de coco', 'agua de coco', 'isotônico', 'isotonico',
                'energético', 'energetico', 'cerveja', 'cerveja sem álcool', 'cerveja sem alcool',
                'vinho tinto', 'vinho branco', 'vinho rosé', 'vinho rose', 'espumante',
                'champagne', 'licor', 'whisky', 'vodka', 'cachaça', 'cachaca'
            ],
            'Padaria': [
                'pao', 'pão', 'bolo', 'torta', 'doce', 'biscoito', 'bolacha', 'pão de forma',
                'pao de forma', 'pão doce', 'pao doce', 'pão francês', 'pao frances',
                'pão integral', 'pao integral', 'pão de hambúrguer', 'pao de hamburguer',
                'rosquinha', 'sonho', 'coxinha', 'empada', 'pastel', 'torta doce',
                'torta salgada', 'bolo de chocolate', 'bolo de cenoura', 'brigadeiro',
                'beijinho', 'cocada', 'pudim', 'mousse', 'torta de limão', 'torta de limao'
            ],
            'Pet Shop': [
                'racao', 'ração', 'petisco', 'areia', 'sache', 'sachê', 'ração para cães',
                'racao para caes', 'ração para gatos', 'racao para gatos', 'petisco para cães',
                'petisco para caes', 'areia sanitária', 'areia sanitaria', 'brinquedo',
                'coleira', 'guia', 'casinha', 'cama', 'comedouro', 'bebedouro'
            ],
            'Bazar': [
                'papel', 'pilha', 'bateria', 'fita', 'adesivo', 'papel alumínio', 'papel aluminio',
                'papel filme', 'papel toalha', 'papel higiênico', 'papel higienico', 'guardanapo',
                'saco de lixo', 'saco plastico', 'saco plástico', 'fralda', 'absorvente',
                'algodão', 'algodao', 'cotonete', 'lenço', 'lenco', 'toalha de banho',
                'toalha de rosto', 'copo', 'prato', 'talher', 'caneca', 'garrafa',
                'vasilha', 'tampa', 'saco zip', 'saco zip lock'
            ],
            'Higiene Pessoal': [
                'shampoo', 'condicionador', 'sabonete', 'desodorante', 'pasta de dente',
                'escova de dente', 'fio dental', 'enxaguante bucal', 'protetor solar',
                'hidratante', 'perfume', 'colônia', 'colonia', 'desodorante aerosol',
                'desodorante roll on', 'absorvente', 'fralda', 'lenço umedecido', 'lenco umedecido',
                'algodão', 'algodao', 'cotonete', 'aparelho de barbear', 'lâmina', 'lamina'
            ],
            'Congelados': [
                'hambúrguer', 'hamburguer', 'nuggets', 'batata frita', 'pizza', 'lasanha',
                'sorvete', 'picolé', 'picole', 'açaí', 'acai', 'polpa', 'fruta congelada',
                'legume congelado', 'vegetal congelado', 'peixe congelado', 'frango congelado'
            ]
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
        
        # Marcações de marcas conhecidas (EXPANDIDA AO MÁXIMO)
        marcas_comuns = [
            # Arroz e Feijão
            'tio joao', 't. joao', 'tio joão', 't. joão', 'dona elza', 'dona elsa', 'camil', 'prato fino', 'tio urbano',
            'cristal', 'tio jorge', 'tio ben', 'uniao', 'kicaldo', 'kicaldo', 'sao joao',
            # Laticínios
            'italac', 'parmalat', 'nestle', 'nestlé', 'danone', 'vigor', 'itambe', 'elegê', 'batavo',
            'piracanjuba', 'jussara', 'lacta', 'garoto', 'nestlé', 'lactalis', 'tirolez', 'tirolez',
            'catupiry', 'polenguinho', 'requeijão', 'requeijao', 'requeijão cremoso',
            # Limpeza
            'omo', 'ariel', 'comfort', 'downy', 'ype', 'veja', 'pinho sol', 'assolan', 'vanish', 'cif', 'ajax',
            'brilhante', 'qboa', 'minuano', 'santa clara', 'limpol', 'detergente ype', 'amaciante ype',
            'sabão em pó', 'sabao em po', 'sabão líquido', 'sabao liquido', 'sabonete', 'desinfetante',
            'água sanitária', 'agua sanitaria', 'cloro', 'multiuso', 'limpa vidros', 'lustra móveis',
            # Carnes
            'sadia', 'perdigao', 'perdigão', 'seara', 'friboi', 'swift', 'jbs', 'marfrig', 'aurora',
            'frimesa', 'cooperativa', 'frigorífico', 'frigorifico',
            # Bebidas
            'coca cola', 'coca-cola', 'pepsi', 'guarana', 'sprite', 'fanta', 'schweppes', 'soda',
            'antarctica', 'brahma', 'skol', 'heineken', 'stella artois', 'eisberg', 'bohemia',
            'devassa', 'original', 'itaipava', 'petra', 'sub zero', 'glacial',
            'del valle', 'maguary', 'do bem', 'suco del valle', 'suco maguary',
            # Condimentos e Temperos
            'maggi', 'knorr', 'hellmanns', 'maionese', 'heinz', 'quero', 'elefante', 'arisco',
            'kitano', 'sazon', 'caldo knorr', 'caldo maggi', 'tempero completo', 'tempero pronto',
            # Pet Shop
            'dog chow', 'whiskas', 'pedigree', 'royal canin', 'golden', 'friskies', 'premier',
            'gran plus', 'rações', 'ração', 'petisco', 'areia sanitária', 'areia sanitaria',
            'pipicat', 'pipi cat', 'sansão', 'sansao',
            # Bazar e Utilidades
            'wyda', 'duracell', 'rayovac', 'panasonic', 'energizer', 'pilha', 'bateria',
            'papel alumínio', 'papel aluminio', 'papel filme', 'papel toalha', 'papel higiênico',
            'papel higienico', 'toalha de papel', 'guardanapo', 'saco de lixo', 'saco plastico',
            # Padaria
            'wickbold', 'panco', 'pullman', 'seven boys', 'visconti', 'bauducco', 'marilan',
            'piraquê', 'piraque', 'nestlé', 'lacta', 'garoto',
            # Congelados
            'sadia', 'perdigão', 'seara', 'friboi', 'bom sabor', 'bom sabor',
            # Higiene Pessoal
            'colgate', 'sorriso', 'close up', 'sensodyne', 'oral b', 'crest', 'pasta de dente',
            'shampoo', 'condicionador', 'sabonete', 'desodorante', 'rexona', 'dove', 'nivea',
            'johnson', 'johnson & johnson', 'huggies', 'pampers', 'monange',
            # Outros
            'bombril', 'palha de aço', 'esponja', 'saco de lixo', 'fralda', 'absorvente'
        ]
        
        # Processar linhas e também tentar detectar produtos em múltiplas linhas
        # Estratégia: processar linha por linha E tentar combinar linhas adjacentes
        i = 0
        linhas_processadas = set()  # Evitar processar a mesma linha duas vezes
        
        while i < len(linhas):
            if i in linhas_processadas:
                i += 1
                continue
                
            linha = linhas[i].strip()
            
            # Tentar combinar linhas adjacentes se a linha atual parece incompleta
            linha_combinada = linha
            j = i + 1
            linhas_usadas = [i]
            
            # Combinar até 3 linhas seguintes se parecerem relacionadas
            while j < len(linhas) and len(linhas_usadas) < 4:
                linha_seguinte = linhas[j].strip()
                if not linha_seguinte or len(linha_seguinte) < 2:
                    break
                
                # Verificar se próxima linha parece ser continuação (tem preço, quantidade, ou é curta)
                tem_preco = bool(re.search(r'R\$\s*\d+|(\d+)[,.]\d{2}', linha_seguinte, re.IGNORECASE))
                tem_qtd = bool(re.search(r'(\d+)\s*(kg|g|L|ml|un)', linha_seguinte, re.IGNORECASE))
                eh_curta = len(linha_seguinte) < 30
                
                if tem_preco or tem_qtd or (eh_curta and not linha_seguinte[0].isupper()):
                    linha_combinada += ' ' + linha_seguinte
                    linhas_usadas.append(j)
                    j += 1
                else:
                    break
            
            # Marcar linhas como processadas
            for idx in linhas_usadas:
                linhas_processadas.add(idx)
            
            linha = linha_combinada.strip()
            
            if not linha or len(linha) < 3:
                i += 1
                continue
            
            # Padrão para preço: R$ XX,XX ou R$XX,XX ou XX,XX (EXPANDIDO)
            preco_patterns = [
                r'R\$\s*(\d+)[,.](\d{2})',  # R$ 12,99
                r'R\$\s*(\d+)[,.](\d{2})',  # R$12,99
                r'(\d+)[,.](\d{2})\s*R\$',  # 12,99 R$
                r'(\d+)[,.](\d{2})\s*reais',  # 12,99 reais
                r'preco[:\s]*(\d+)[,.](\d{2})',  # preço: 12,99
                r'preço[:\s]*(\d+)[,.](\d{2})',  # preco: 12,99
                r'por\s*R\$\s*(\d+)[,.](\d{2})',  # por R$ 12,99
                r'apenas\s*R\$\s*(\d+)[,.](\d{2})',  # apenas R$ 12,99
                r'(\d+)[,.](\d{2})',  # 12,99 (sem R$, último recurso)
                r'R\$\s*(\d+)',  # R$ 12 (sem centavos)
                r'(\d+)\s*reais'  # 12 reais
            ]
            
            preco_match = None
            preco_valor = None
            for pattern in preco_patterns:
                preco_match = re.search(pattern, linha, re.IGNORECASE)
                if preco_match:
                    try:
                        if len(preco_match.groups()) >= 2:
                            # Formato com centavos
                            preco_valor = float(f"{preco_match.group(1)}.{preco_match.group(2)}")
                        else:
                            # Formato sem centavos
                            preco_valor = float(preco_match.group(1))
                        break
                    except (ValueError, IndexError):
                        continue
            
            if not preco_match or preco_valor is None or preco_valor <= 0:
                i += 1
                continue
            
            preco = preco_valor
            
            # Remover preço da linha para processar o resto
            linha_sem_preco = re.sub(r'R\$\s*\d+[,.]\d{2}|\d+[,.]\d{2}\s*R\$|\d+[,.]\d{2}', '', linha, flags=re.IGNORECASE).strip()
            
            # Padrão para quantidade: Xkg, Xg, XL, Xml, etc. (EXPANDIDO)
            qtd_patterns = [
                r'(\d+(?:[,.]\d+)?)\s*(kg|g|L|l|ml|un|pct|pac|und|unid|unidade|und\.|un\.)',
                r'(\d+(?:[,.]\d+)?)\s*(quilo|quilos|grama|gramas|litro|litros|mililitro|mililitros)',
                r'(\d+)\s*x\s*(\d+)\s*(g|kg|ml|L)',  # 4 x 250ml
                r'(\d+)\s*unidades',  # 4 unidades
                r'(\d+)\s*un\.',  # 4 un.
                r'pacote\s*(\d+)\s*(g|kg|ml|L)',  # pacote 500g
                r'(\d+)\s*ml',  # 250ml (sem espaço)
                r'(\d+)\s*kg',  # 5kg (sem espaço)
                r'(\d+)\s*g',  # 500g (sem espaço)
                r'(\d+)\s*L',  # 1L (sem espaço)
            ]
            
            quantidade = None
            for pattern in qtd_patterns:
                qtd_match = re.search(pattern, linha_sem_preco, re.IGNORECASE)
                if qtd_match:
                    try:
                        if len(qtd_match.groups()) == 3:  # Formato 4 x 250ml
                            num1 = float(qtd_match.group(1).replace(',', '.'))
                            num2 = float(qtd_match.group(2).replace(',', '.'))
                            unidade = qtd_match.group(3).lower()
                            total = int(num1 * num2)
                            quantidade = f"{total}{unidade}"
                        else:
                            num = qtd_match.group(1).replace(',', '.')
                            unidade = qtd_match.group(2).lower() if len(qtd_match.groups()) >= 2 else 'un'
                            # Normalizar unidade
                            if unidade in ['quilo', 'quilos']:
                                unidade = 'kg'
                            elif unidade in ['grama', 'gramas']:
                                unidade = 'g'
                            elif unidade in ['litro', 'litros']:
                                unidade = 'L'
                            elif unidade in ['mililitro', 'mililitros']:
                                unidade = 'ml'
                            elif unidade in ['un', 'und', 'unid', 'unidade', 'pct', 'pac', 'und.', 'un.']:
                                unidade = 'un'
                            quantidade = f"{num}{unidade}"
                        linha_sem_preco = re.sub(pattern, '', linha_sem_preco, flags=re.IGNORECASE).strip()
                        break
                    except (ValueError, IndexError):
                        continue
            
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
            
            # Se não encontrou marca conhecida, tentar estratégias mais agressivas
            if not marca:
                palavras = produto_nome.split()
                if len(palavras) > 1:
                    # Estratégia 1: Última palavra pode ser marca
                    ultima_palavra = palavras[-1]
                    if len(ultima_palavra) > 2 and ultima_palavra[0].isupper():
                        marca = ultima_palavra.title()
                        produto_nome = ' '.join(palavras[:-1])
                    # Estratégia 2: Primeira palavra pode ser marca (ex: "Nestlé Leite")
                    elif len(palavras) > 2 and palavras[0][0].isupper() and len(palavras[0]) > 3:
                        # Verificar se primeira palavra parece marca
                        primeira = palavras[0].lower()
                        if primeira not in ['arroz', 'feijao', 'feijão', 'leite', 'carne', 'frango', 'sabao', 'sabão', 'refrigerante', 'suco']:
                            marca = palavras[0].title()
                            produto_nome = ' '.join(palavras[1:])
                    # Estratégia 3: Se não encontrou, manter como "Genérico"
                    if not marca:
                        marca = 'Genérico'
                else:
                    marca = 'Genérico'
            
            # Limpar e normalizar nome do produto
            produto_nome = re.sub(r'\s+', ' ', produto_nome).strip()
            produto_nome = produto_nome.title()
            
            # Identificar segmento
            segmento = self.identificar_segmento(produto_nome)
            
            # Validar produto (deve ter pelo menos 2 caracteres)
            if produto_nome and len(produto_nome) >= 2 and preco > 0:
                # Capitalizar primeira letra de cada palavra
                produto_nome_formatado = ' '.join([p.capitalize() if len(p) > 1 else p for p in produto_nome.split()])
                
                produtos.append({
                    'segmento': segmento,
                    'produto': produto_nome_formatado,
                    'marca': marca,
                    'quantidade': quantidade or 'un',
                    'preco': preco,
                    'preco_oferta': preco,
                    'mercado': mercado_nome or 'Desconhecido',
                    'url_fonte': '',  # Será preenchido pelo scraper
                    'data_extracao': datetime.now().strftime('%Y-%m-%d')
                })
        
        return produtos
    
    def processar_imagens_mercado(self, mercado_nome):
        """Processa todas as imagens de um mercado"""
        produtos_todos = []
        
        # Verificar se o diretório existe
        if not os.path.exists(IMAGES_DIR):
            print(f"Diretório {IMAGES_DIR} não existe")
            return produtos_todos
        
        # Buscar imagens do mercado (incluindo PDFs convertidos)
        for filename in os.listdir(IMAGES_DIR):
            # Buscar por nome do mercado (case insensitive) e também por variações
            mercado_variations = [
                mercado_nome.lower(),
                mercado_nome.title(),
                mercado_nome.upper()
            ]
            
            # Verificar se o arquivo pertence ao mercado
            filename_lower = filename.lower()
            is_mercado_file = any(var in filename_lower for var in mercado_variations)
            
            # Verificar extensões de imagem
            is_image = filename.lower().endswith(('.jpg', '.jpeg', '.png', '.bmp', '.gif'))
            
            if is_mercado_file and is_image:
                image_path = os.path.join(IMAGES_DIR, filename)
                try:
                    print(f"Processando {filename}...")
                    
                    texto = self.extract_text(image_path)
                    if texto and len(texto.strip()) > 10:  # Validar que há texto suficiente
                        produtos = self.limpar_dados_mercado(texto, mercado_nome)
                        print(f"  -> {len(produtos)} produtos extraídos de {filename}")
                        produtos_todos.extend(produtos)
                    else:
                        print(f"  -> Nenhum texto extraído de {filename}")
                except Exception as e:
                    print(f"  -> Erro ao processar {filename}: {e}")
        
        print(f"Total de produtos processados para {mercado_nome}: {len(produtos_todos)}")
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

