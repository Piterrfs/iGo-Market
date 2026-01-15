import requests
from bs4 import BeautifulSoup
import time
import os
import re
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from config import MERCADOS, SCRAPING_CONFIG, IMAGES_DIR
import json
from datetime import datetime
try:
    from pdf2image import convert_from_path
except ImportError:
    convert_from_path = None
import fitz  # PyMuPDF

class MercadoScraper:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
    
    def setup_selenium(self):
        """Configura o driver Selenium para sites com JavaScript"""
        chrome_options = Options()
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--window-size=1920,1080')
        chrome_options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36')
        
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=chrome_options)
        return driver
    
    def download_image(self, url, filename):
        """Baixa uma imagem de uma URL"""
        try:
            response = self.session.get(url, timeout=SCRAPING_CONFIG['timeout'])
            response.raise_for_status()
            
            filepath = os.path.join(IMAGES_DIR, filename)
            with open(filepath, 'wb') as f:
                f.write(response.content)
            return filepath
        except Exception as e:
            print(f"Erro ao baixar imagem {url}: {e}")
            return None
    
    def download_pdf(self, url, filename):
        """Baixa um PDF e converte para imagens"""
        try:
            response = self.session.get(url, timeout=SCRAPING_CONFIG['timeout'])
            response.raise_for_status()
            
            pdf_path = os.path.join(IMAGES_DIR, filename)
            with open(pdf_path, 'wb') as f:
                f.write(response.content)
            
            # Converter PDF para imagens
            image_paths = []
            
            # Tentar com pdf2image primeiro
            if convert_from_path:
                try:
                    images = convert_from_path(pdf_path, dpi=300)
                    for i, image in enumerate(images):
                        image_filename = filename.replace('.pdf', f'_page_{i+1}.jpg')
                        image_path = os.path.join(IMAGES_DIR, image_filename)
                        image.save(image_path, 'JPEG')
                        image_paths.append(image_path)
                        print(f"Página {i+1} convertida: {image_filename}")
                    if image_paths:
                        return image_paths
                except Exception as e:
                    print(f"Erro ao converter PDF com pdf2image: {e}")
            
            # Tentar com PyMuPDF como alternativa
            try:
                doc = fitz.open(pdf_path)
                for page_num in range(len(doc)):
                    page = doc[page_num]
                    pix = page.get_pixmap(matrix=fitz.Matrix(2, 2))  # 2x zoom para melhor qualidade
                    image_filename = filename.replace('.pdf', f'_page_{page_num+1}.png')
                    image_path = os.path.join(IMAGES_DIR, image_filename)
                    pix.save(image_path)
                    image_paths.append(image_path)
                    print(f"Página {page_num+1} convertida com PyMuPDF: {image_filename}")
                doc.close()
                return image_paths if image_paths else None
            except Exception as e2:
                print(f"Erro ao converter PDF com PyMuPDF: {e2}")
                return None
        except Exception as e:
            print(f"Erro ao baixar PDF {url}: {e}")
            return None
    
    def encontrar_encarte_url(self, driver, mercado):
        """Encontra a URL do encarte (PDF ou imagem) na página"""
        encarte_urls = []
        
        try:
            # Procurar por links de PDF (EXPANDIDO)
            pdf_links = driver.find_elements(By.XPATH, "//a[contains(@href, '.pdf') or contains(@href, 'pdf') or contains(@href, 'encarte')]")
            for link in pdf_links:
                href = link.get_attribute('href')
                if href and ('.pdf' in href.lower() or 'encarte' in href.lower()):
                    encarte_urls.append(('pdf', href))
            
            # Procurar por botões de download de PDF
            pdf_buttons = driver.find_elements(By.XPATH, "//button[contains(@onclick, 'pdf') or contains(@onclick, 'encarte')] | //a[contains(@class, 'pdf') or contains(@class, 'encarte')]")
            for button in pdf_buttons:
                onclick = button.get_attribute('onclick')
                href = button.get_attribute('href')
                if onclick and '.pdf' in onclick.lower():
                    # Extrair URL do onclick
                    url_match = re.search(r'["\']([^"\']*\.pdf[^"\']*)["\']', onclick)
                    if url_match:
                        encarte_urls.append(('pdf', url_match.group(1)))
                elif href and '.pdf' in href.lower():
                    encarte_urls.append(('pdf', href))
            
            # Procurar por imagens de encarte (EXPANDIDO)
            img_elements = driver.find_elements(By.TAG_NAME, 'img')
            for img in img_elements:
                src = img.get_attribute('src')
                data_src = img.get_attribute('data-src')  # Lazy loading
                srcset = img.get_attribute('srcset')
                
                # Verificar src principal
                if src and any(palavra in src.lower() for palavra in ['encarte', 'oferta', 'promocao', 'promoção', 'flyer', 'catalogo', 'catálogo']):
                    if src.startswith('http'):
                        encarte_urls.append(('image', src))
                    else:
                        base_url = MERCADOS[mercado]['url']
                        if not src.startswith('/'):
                            src = '/' + src
                        encarte_urls.append(('image', base_url.rsplit('/', 1)[0] + src))
                
                # Verificar data-src (lazy loading)
                if data_src and any(palavra in data_src.lower() for palavra in ['encarte', 'oferta', 'promocao']):
                    if data_src.startswith('http'):
                        encarte_urls.append(('image', data_src))
                
                # Verificar srcset
                if srcset:
                    urls_srcset = [url.split()[0] for url in srcset.split(',')]
                    for url in urls_srcset:
                        if any(palavra in url.lower() for palavra in ['encarte', 'oferta', 'promocao']):
                            encarte_urls.append(('image', url))
            
            # Procurar por canvas ou elementos que possam conter o encarte
            canvas_elements = driver.find_elements(By.TAG_NAME, 'canvas')
            if canvas_elements:
                # Tentar capturar screenshot do canvas
                for i, canvas in enumerate(canvas_elements):
                    screenshot_path = os.path.join(IMAGES_DIR, f"{mercado}_canvas_{i}.png")
                    canvas.screenshot(screenshot_path)
                    encarte_urls.append(('image', screenshot_path))
            
            # Procurar por divs/seções com produtos listados diretamente no HTML
            # Muitos sites têm produtos em divs com classes específicas
            produto_elements = driver.find_elements(By.XPATH, 
                "//div[contains(@class, 'produto')] | "
                "//div[contains(@class, 'product')] | "
                "//div[contains(@class, 'item')] | "
                "//div[contains(@class, 'oferta')] | "
                "//li[contains(@class, 'produto')] | "
                "//li[contains(@class, 'product')]"
            )
            if produto_elements and len(produto_elements) > 0:
                # Se encontrou produtos no HTML, marcar para processamento
                encarte_urls.append(('html', 'html_products'))
        
        except Exception as e:
            print(f"Erro ao encontrar encarte: {e}")
        
        return encarte_urls
    
    def extrair_produtos_html(self, driver, mercado, categoria_nome=None):
        """Extrai produtos usando BeautifulSoup - ABORDAGEM SIMPLES COMO CAPTURA DE NOTÍCIAS"""
        produtos = []
        try:
            # Aguardar carregamento completo e scroll para carregar conteúdo dinâmico
            time.sleep(3)
            
            # Scroll para carregar conteúdo lazy loading
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(2)
            driver.execute_script("window.scrollTo(0, 0);")
            time.sleep(1)
            
            # Obter HTML completo da página (após scroll)
            html_content = driver.page_source
            
            # Debug: salvar HTML para análise (apenas primeira categoria para não encher disco)
            if categoria_nome and 'Açougue' in categoria_nome:
                debug_file = os.path.join(IMAGES_DIR, f"debug_html_{categoria_nome.replace(' ', '_')}.html")
                try:
                    with open(debug_file, 'w', encoding='utf-8') as f:
                        f.write(html_content)
                    print(f"  HTML salvo para debug: {debug_file}")
                except:
                    pass
            
            # Usar BeautifulSoup para parsear (como fazem com notícias)
            soup = BeautifulSoup(html_content, 'html.parser')
            
            print(f"  HTML carregado: {len(html_content)} caracteres")
            
            # Debug: contar padrões de preço no HTML bruto
            precos_no_html = len(re.findall(r'R\$\s*\d+[,.]\d{2}|\d+[,.]\d{2}', html_content))
            print(f"  Padrões de preço no HTML bruto: {precos_no_html}")
            
            # Debug: verificar se tem texto de produtos
            texto_completo = soup.get_text()
            tem_arroz = 'arroz' in texto_completo.lower()
            tem_preco = bool(re.search(r'\d+[,.]\d{2}', texto_completo))
            print(f"  Contém 'arroz': {tem_arroz}")
            print(f"  Contém padrão de preço: {tem_preco}")
            
            # ESTRATÉGIA 0: Buscar diretamente no TEXTO LIMPO (MAIS EFETIVO)
            # Padrão GUANABARA: "13,95 Arroz Branco Ouro Nobre 5Kg" (preço SEM R$ seguido de nome)
            print("  Estratégia 0: Buscando padrões no texto limpo (sem tags HTML)...")
            
            # Obter texto limpo do BeautifulSoup (sem tags HTML)
            texto_limpo = soup.get_text(separator=' ', strip=True)
            print(f"  Texto limpo: {len(texto_limpo)} caracteres")
            
            # Padrão específico para Guanabara: número seguido de vírgula/ponto e 2 dígitos, seguido de texto (nome)
            # Exemplo: "13,95 Arroz Branco..." ou "18,95 Arroz Combrasil..."
            # CORRIGIDO: padrão que funciona (testado com HTML real)
            padrao_guanabara = r'(\d+[,.]\d{2})\s+([A-Za-zÁÉÍÓÚÂÊÔÃÕÇáéíóúâêôãõç][A-Za-zÁÉÍÓÚÂÊÔÃÕÇáéíóúâêôãõç0-9\s]{3,60}?)(?=\s*\d+[,.]\d{2}|\s*cada|</|<|$)'
            
            # Buscar no texto limpo (onde funciona melhor)
            matches_guanabara = list(re.finditer(padrao_guanabara, texto_limpo, re.MULTILINE | re.DOTALL))
            print(f"  Padrões Guanabara encontrados: {len(matches_guanabara)}")
            
            # Se não encontrou, tentar padrão mais simples
            if len(matches_guanabara) < 3:
                print("  Tentando padrão mais simples...")
                padrao_simples = r'(\d+[,.]\d{2})\s+([A-Za-zÁÉÍÓÚÂÊÔÃÕÇáéíóúâêôãõç][A-Za-zÁÉÍÓÚÂÊÔÃÕÇáéíóúâêôãõç0-9\s]{3,50})'
                matches_guanabara = list(re.finditer(padrao_simples, texto_limpo, re.MULTILINE))
                print(f"  Padrão simples encontrou: {len(matches_guanabara)}")
            
            # Debug: mostrar primeiros matches encontrados
            if matches_guanabara:
                print(f"  Primeiros 3 matches:")
                for i, m in enumerate(matches_guanabara[:3], 1):
                    print(f"    {i}. Preço: {m.group(1)}, Nome: {m.group(2)[:50]}")
            
            produtos_do_texto = produtos_de_elementos.copy()  # Começar com produtos de elementos
            
            # Processar padrão específico Guanabara
            for match in matches_guanabara:
                try:
                    preco_str = match.group(1).replace(',', '.')
                    preco = float(preco_str)
                    
                    if preco < 0.01 or preco > 10000:
                        continue
                    
                    nome = match.group(2).strip()
                    # Limpar nome - remover tags HTML que podem ter escapado
                    nome = re.sub(r'<[^>]+>', '', nome)
                    # Remover quebras de linha e espaços múltiplos
                    nome = re.sub(r'\s+', ' ', nome)
                    # Remover espaços no início/fim
                    nome = nome.strip()
                    # Remover "cada" no final (ex: "Arroz Máximo 5Kg cada" -> "Arroz Máximo 5Kg")
                    nome = re.sub(r'\s+cada\s*$', '', nome, flags=re.IGNORECASE)
                    nome = nome.strip()
                    
                    # Validar nome
                    if nome and len(nome) >= 3 and len(nome) <= 200:
                        # Pular se for só número ou caracteres especiais
                        if not re.match(r'^[0-9,.\s]+$', nome):
                            # Extrair quantidade
                            qtd_match = re.search(r'(\d+(?:[,.]\d+)?)\s*(kg|g|L|l|ml|un|pct|pac|und)', nome, re.IGNORECASE)
                            quantidade = qtd_match.group(0) if qtd_match else 'un'
                            
                            produto_key = f"{nome.lower()}_{preco}_{quantidade}"
                            if produto_key not in [p.get('_key', '') for p in produtos_do_texto]:
                                produtos_do_texto.append({
                                    '_key': produto_key,
                                    'nome': nome,
                                    'preco': preco,
                                    'quantidade': quantidade,
                                    'categoria': categoria_nome,
                                    'texto_completo': nome[:200]
                                })
                except Exception as e:
                    continue
            
            # Processar padrões gerais (backup)
            for match in re.finditer(r'R\$\s*(\d+)[,.](\d{2})|(\d+)[,.](\d{2})', html_content):
                try:
                    # Extrair preço
                    if match.group(1):
                        preco = float(f"{match.group(1)}.{match.group(2)}")
                    else:
                        preco = float(f"{match.group(3)}.{match.group(4)}")
                    
                    if preco < 0.01 or preco > 10000:
                        continue
                    
                    # Pegar contexto ANTES e DEPOIS do preço (Guanabara tem preço ANTES do nome)
                    inicio = max(0, match.start() - 50)  # Pouco antes (preço geralmente está no início)
                    fim = min(len(html_content), match.end() + 300)  # Muito depois (nome vem depois)
                    contexto = html_content[inicio:fim]
                    
                    # Parsear contexto com BeautifulSoup para extrair texto limpo
                    contexto_soup = BeautifulSoup(contexto, 'html.parser')
                    texto_limpo = contexto_soup.get_text(separator=' ', strip=True)
                    
                    # Padrão GUANABARA: "13,95 Arroz Branco Ouro Nobre 5Kg"
                    # Preço vem ANTES do nome
                    preco_texto = match.group(0)
                    pos_preco = texto_limpo.find(preco_texto)
                    
                    if pos_preco >= 0:
                        # Nome vem DEPOIS do preço
                        texto_depois_preco = texto_limpo[pos_preco + len(preco_texto):].strip()
                        
                        # Limpar e extrair nome (até encontrar próximo número ou fim)
                        # Remover palavras comuns que não são parte do nome
                        palavras = texto_depois_preco.split()
                        nome_palavras = []
                        
                        for palavra in palavras:
                            palavra_limpa = palavra.strip('.,;:!?()[]{}')
                            # Parar se encontrar outro preço ou número grande
                            if re.match(r'^\d+[,.]\d{2}$', palavra_limpa):
                                break
                            # Parar se encontrar palavras de fim de lista
                            if palavra_limpa.lower() in ['cada', 'unidade', 'un', 'kg', 'g', 'l', 'ml'] and len(nome_palavras) > 3:
                                # Adicionar a palavra se for unidade (kg, g, etc)
                                if palavra_limpa.lower() in ['kg', 'g', 'l', 'ml', 'un', 'pct', 'pac']:
                                    nome_palavras.append(palavra_limpa)
                                break
                            # Adicionar palavra se não for só número
                            if palavra_limpa and not re.match(r'^\d+$', palavra_limpa):
                                nome_palavras.append(palavra_limpa)
                            # Limitar tamanho do nome
                            if len(nome_palavras) >= 15:
                                break
                        
                        nome = ' '.join(nome_palavras).strip()
                        
                        # Validar nome
                        if nome and len(nome) >= 2 and len(nome) <= 200:
                            if not re.match(r'^[R$0-9,.\s]+$', nome):
                                # Extrair quantidade do nome
                                qtd_match = re.search(r'(\d+(?:[,.]\d+)?)\s*(kg|g|L|l|ml|un|pct|pac|und)', nome, re.IGNORECASE)
                                quantidade = qtd_match.group(0) if qtd_match else 'un'
                                
                                produto_key = f"{nome.lower()}_{preco}_{quantidade}"
                                if produto_key not in [p.get('_key', '') for p in produtos_do_texto]:
                                    produtos_do_texto.append({
                                        '_key': produto_key,
                                        'nome': nome,
                                        'preco': preco,
                                        'quantidade': quantidade,
                                        'categoria': categoria_nome,
                                        'texto_completo': texto_limpo[:200]
                                    })
                except Exception as e:
                    continue
            
            print(f"  ✓ {len(produtos_do_texto)} produtos encontrados por busca direta no HTML")
            
            # ESTRATÉGIA 1: Buscar TODOS os elementos que podem conter produtos
            todos_elementos = soup.find_all(['div', 'li', 'article', 'span', 'p', 'h1', 'h2', 'h3', 'h4', 'h5', 'a', 'td', 'tr', 'section'])
            
            print(f"  Total de elementos encontrados: {len(todos_elementos)}")
            
            produtos_encontrados = []
            
            for elem in todos_elementos:
                try:
                    texto = elem.get_text(strip=True)
                    
                    # Verificar se tem padrão de produto: texto + preço
                    if not texto or len(texto) < 5 or len(texto) > 500:
                        continue
                    
                    # Buscar preço no texto
                    preco_match = re.search(r'R\$\s*(\d+)[,.](\d{2})|(\d+)[,.](\d{2})', texto)
                    if not preco_match:
                        continue
                    
                    # Extrair preço
                    if preco_match.group(1):
                        preco = float(f"{preco_match.group(1)}.{preco_match.group(2)}")
                    else:
                        preco = float(f"{preco_match.group(3)}.{preco_match.group(4)}")
                    
                    # Validar preço razoável
                    if preco < 0.01 or preco > 10000:
                        continue
                    
                    # GUANABARA: Preço pode vir ANTES ou DEPOIS do nome
                    # Tentar ambas as direções
                    texto_antes_preco = texto[:preco_match.start()].strip()
                    texto_depois_preco = texto[preco_match.end():].strip()
                    
                    nome = ""
                    
                    # Estratégia 1: Nome DEPOIS do preço (padrão Guanabara: "13,95 Arroz...")
                    if texto_depois_preco and len(texto_depois_preco) > 2:
                        palavras = texto_depois_preco.split()
                        nome_palavras = []
                        for palavra in palavras[:15]:  # Limitar a 15 palavras
                            palavra_limpa = palavra.strip('.,;:!?()[]{}')
                            # Parar se encontrar outro preço
                            if re.match(r'^\d+[,.]\d{2}$', palavra_limpa):
                                break
                            if palavra_limpa and not re.match(r'^\d+$', palavra_limpa):
                                nome_palavras.append(palavra_limpa)
                        nome = ' '.join(nome_palavras).strip()
                    
                    # Estratégia 2: Nome ANTES do preço (padrão comum: "Arroz... R$ 13,95")
                    if not nome or len(nome) < 2:
                        if texto_antes_preco and len(texto_antes_preco) > 2:
                            linhas = [l.strip() for l in texto_antes_preco.split('\n') if l.strip()]
                            if linhas:
                                nome = max(linhas, key=len)
                    
                    # Estratégia 3: Tentar pegar texto do elemento pai
                    if not nome or len(nome) < 2:
                        try:
                            if elem.parent:
                                texto_pai = elem.parent.get_text(strip=True)
                                # Buscar padrão: preço seguido de nome
                                preco_pos = texto_pai.find(preco_match.group(0))
                                if preco_pos >= 0:
                                    texto_depois = texto_pai[preco_pos + len(preco_match.group(0)):].strip()
                                    palavras = texto_depois.split()[:15]
                                    nome_palavras = [p.strip('.,;:!?()[]{}') for p in palavras if p.strip('.,;:!?()[]{}') and not re.match(r'^\d+$', p.strip('.,;:!?()[]{}'))]
                                    nome = ' '.join(nome_palavras).strip()
                        except:
                            pass
                    
                    # Limpar nome final
                    nome = re.sub(r'\s+', ' ', nome).strip()
                    
                    # Se ainda não tem nome, tentar pegar do atributo alt, title, ou data-*
                    if not nome or len(nome) < 2:
                        for attr in ['alt', 'title', 'data-name', 'data-product-name']:
                            try:
                                attr_value = elem.get(attr, '')
                                if attr_value and len(attr_value) > 2:
                                    nome = attr_value.strip()
                                    break
                            except:
                                continue
                    
                    # Validar nome
                    if not nome or len(nome) < 2 or len(nome) > 200:
                        continue
                    
                    # Pular se for só número ou preço
                    if re.match(r'^[R$0-9,.\s]+$', nome):
                        continue
                    
                    # Extrair quantidade do nome
                    qtd_match = re.search(r'(\d+(?:[,.]\d+)?)\s*(kg|g|L|l|ml|un|pct|pac|und)', nome, re.IGNORECASE)
                    quantidade = qtd_match.group(0) if qtd_match else 'un'
                    
                    # Adicionar produto (evitar duplicatas)
                    produto_key = f"{nome.lower()}_{preco}_{quantidade}"
                    if produto_key not in [p.get('_key', '') for p in produtos_encontrados]:
                        produtos_encontrados.append({
                            '_key': produto_key,
                            'nome': nome,
                            'preco': preco,
                            'quantidade': quantidade,
                            'categoria': categoria_nome,
                            'texto_completo': texto[:200]
                        })
                        
                except Exception as e:
                    continue
            
            print(f"  ✓ {len(produtos_encontrados)} produtos únicos encontrados por padrão de texto")
            
            # Combinar produtos encontrados por diferentes estratégias
            todos_produtos = produtos_do_texto + produtos_encontrados
            
            # Remover duplicatas finais
            produtos_finais = {}
            for p in todos_produtos:
                key = p.get('_key', f"{p.get('nome', '').lower()}_{p.get('preco', 0)}_{p.get('quantidade', 'un')}")
                if key not in produtos_finais:
                    produtos_finais[key] = p
            
            produtos_encontrados = list(produtos_finais.values())
            print(f"  ✓ Total combinado (sem duplicatas): {len(produtos_encontrados)} produtos")
            
            # ESTRATÉGIA 2: Buscar em elementos com classes específicas (backup)
            if len(produtos_encontrados) < 10:
                print("  Tentando busca por classes específicas...")
                
                # Buscar elementos com classes comuns de produto
                classes_produto = ['produto', 'product', 'item', 'card', 'oferta', 'product-card']
                
                for classe in classes_produto:
                    elementos = soup.find_all(attrs={'class': re.compile(classe, re.I)})
                    for elem in elementos:
                        try:
                            texto = elem.get_text(strip=True)
                            if not texto or len(texto) < 5:
                                continue
                            
                            # Buscar preço
                            preco_match = re.search(r'R\$\s*(\d+)[,.](\d{2})|(\d+)[,.](\d{2})', texto)
                            if not preco_match:
                                continue
                            
                            if preco_match.group(1):
                                preco = float(f"{preco_match.group(1)}.{preco_match.group(2)}")
                            else:
                                preco = float(f"{preco_match.group(3)}.{preco_match.group(4)}")
                            
                            if preco < 0.01 or preco > 10000:
                                continue
                            
                            # Extrair nome
                            texto_antes_preco = texto[:preco_match.start()].strip()
                            nome = re.sub(r'\s+', ' ', texto_antes_preco).strip()
                            linhas = [l.strip() for l in nome.split('\n') if l.strip()]
                            if linhas:
                                nome = linhas[0]
                            
                            if not nome or len(nome) < 2:
                                continue
                            
                            qtd_match = re.search(r'(\d+(?:[,.]\d+)?)\s*(kg|g|L|l|ml|un|pct|pac|und)', nome, re.IGNORECASE)
                            quantidade = qtd_match.group(0) if qtd_match else 'un'
                            
                            produto_key = f"{nome.lower()}_{preco}_{quantidade}"
                            if produto_key not in [p.get('_key', '') for p in produtos_encontrados]:
                                produtos_encontrados.append({
                                    '_key': produto_key,
                                    'nome': nome,
                                    'preco': preco,
                                    'quantidade': quantidade,
                                    'categoria': categoria_nome,
                                    'texto_completo': texto[:200]
                                })
                        except:
                            continue
                
                print(f"  Após busca por classes: {len(produtos_encontrados)} produtos")
            
            # Converter para formato final (remover _key)
            for p in produtos_encontrados:
                produtos.append({
                    'nome': p['nome'],
                    'preco': p['preco'],
                    'quantidade': p['quantidade'],
                    'categoria': p['categoria'],
                    'texto_completo': p['texto_completo']
                })
            
            print(f"  ✓ Total final: {len(produtos)} produtos extraídos")
            
            # Debug: mostrar produtos encontrados
            if produtos:
                print(f"  Primeiros 5 produtos extraídos:")
                for i, p in enumerate(produtos[:5], 1):
                    print(f"    {i}. {p.get('nome', 'N/A')} - R$ {p.get('preco', 0):.2f} - {p.get('categoria', 'N/A')}")
            else:
                print(f"  ⚠ NENHUM PRODUTO EXTRAÍDO!")
                print(f"  Verifique:")
                print(f"    - Se o HTML foi carregado corretamente")
                print(f"    - Se os padrões de preço foram encontrados")
                print(f"    - Se a regex está funcionando")
                # Salvar texto limpo para debug
                try:
                    debug_file = os.path.join(IMAGES_DIR, f"debug_texto_{categoria_nome.replace(' ', '_') if categoria_nome else 'geral'}.txt")
                    with open(debug_file, 'w', encoding='utf-8') as f:
                        f.write(texto_limpo[:5000])  # Primeiros 5000 caracteres
                    print(f"    Texto limpo salvo em: {debug_file}")
                except:
                    pass
            
        except Exception as e:
            print(f"  ✗ Erro ao extrair produtos: {e}")
            import traceback
            traceback.print_exc()
        
        return produtos
    
    def scrape_guanabara(self):
        """Scraping do site Guanabara - MELHORADO para capturar encarte E categorias"""
        produtos = []
        driver = None
        try:
            driver = self.setup_selenium()
            
            # 1. PROCESSAR ENCARTE (método original)
            print("Processando encarte do Guanabara...")
            driver.get(MERCADOS['guanabara']['url'])
            time.sleep(8)  # Aguarda carregamento completo
            
            # Tentar encontrar e clicar no botão "Baixar encarte" para obter o PDF
            try:
                download_buttons = driver.find_elements(By.XPATH, 
                    "//a[contains(text(), 'Baixar') or contains(text(), 'Download') or contains(@class, 'download')] | "
                    "//button[contains(text(), 'Baixar') or contains(text(), 'Download')] | "
                    "//a[contains(@href, 'pdf') or contains(@href, 'download')]"
                )
                
                for btn in download_buttons:
                    try:
                        href = btn.get_attribute('href')
                        if href and ('.pdf' in href.lower() or 'download' in href.lower()):
                            print(f"Encontrado link de download: {href}")
                            if href.startswith('http'):
                                filename = f"guanabara_{datetime.now().strftime('%Y%m%d')}.pdf"
                                self.download_pdf(href, filename)
                            elif href.startswith('/'):
                                base_url = MERCADOS['guanabara']['url'].rsplit('/', 1)[0]
                                full_url = base_url + href
                                filename = f"guanabara_{datetime.now().strftime('%Y%m%d')}.pdf"
                                self.download_pdf(full_url, filename)
                            break
                    except:
                        continue
            except Exception as e:
                print(f"Erro ao tentar baixar encarte: {e}")
            
            # Capturar screenshot da área do encarte
            try:
                encarte_elements = driver.find_elements(By.XPATH,
                    "//iframe[contains(@src, 'pdf') or contains(@src, 'encarte')] | "
                    "//div[contains(@class, 'encarte') or contains(@class, 'flyer')] | "
                    "//canvas | //embed[contains(@src, 'pdf')]"
                )
                
                if encarte_elements:
                    for i, elem in enumerate(encarte_elements):
                        try:
                            screenshot_path = os.path.join(IMAGES_DIR, f"guanabara_encarte_{datetime.now().strftime('%Y%m%d')}_{i+1}.png")
                            elem.screenshot(screenshot_path)
                            print(f"Screenshot do encarte salvo: {screenshot_path}")
                        except:
                            screenshot_path = os.path.join(IMAGES_DIR, f"guanabara_fullpage_{datetime.now().strftime('%Y%m%d')}.png")
                            driver.save_screenshot(screenshot_path)
                            print(f"Screenshot da página salvo: {screenshot_path}")
                else:
                    screenshot_path = os.path.join(IMAGES_DIR, f"guanabara_fullpage_{datetime.now().strftime('%Y%m%d')}.png")
                    driver.save_screenshot(screenshot_path)
                    print(f"Screenshot da página salvo: {screenshot_path}")
            except Exception as e:
                print(f"Erro ao capturar screenshot: {e}")
            
            # Extrair produtos do encarte HTML
            produtos_html = self.extrair_produtos_html(driver, 'guanabara', 'Encarte')
            if produtos_html:
                print(f"Produtos extraídos do encarte HTML: {len(produtos_html)}")
                produtos.extend(produtos_html)
            
            # Encontrar URLs de encartes (PDFs ou imagens)
            encarte_urls = self.encontrar_encarte_url(driver, 'guanabara')
            for tipo, url in encarte_urls:
                if tipo == 'pdf':
                    filename = f"guanabara_{datetime.now().strftime('%Y%m%d')}.pdf"
                    self.download_pdf(url, filename)
                elif tipo == 'image':
                    if url.startswith('http'):
                        filename = f"guanabara_{datetime.now().strftime('%Y%m%d')}.jpg"
                        self.download_image(url, filename)
            
            # 2. PROCESSAR CATEGORIAS DE PRODUTOS (APENAS HTML - SEM OCR)
            if 'categorias' in MERCADOS['guanabara']:
                print(f"\nProcessando {len(MERCADOS['guanabara']['categorias'])} categorias do Guanabara (HTML puro)...")
                for categoria in MERCADOS['guanabara']['categorias']:
                    try:
                        print(f"\n  Processando categoria: {categoria['nome']}")
                        print(f"  URL: {categoria['url']}")
                        
                        print(f"    Acessando: {categoria['url']}")
                        driver.get(categoria['url'])
                        time.sleep(10)  # Aguardar carregamento completo
                        
                        # Aguardar elementos carregarem
                        try:
                            WebDriverWait(driver, 15).until(
                                EC.presence_of_element_located((By.TAG_NAME, "body"))
                            )
                        except:
                            print(f"      ⚠ Timeout aguardando body carregar")
                        
                        # Verificar se página carregou
                        page_title = driver.title
                        print(f"      Título da página: {page_title[:50]}")
                        
                        # Verificar se tem conteúdo
                        body_text = driver.find_element(By.TAG_NAME, "body").text
                        print(f"      Texto no body: {len(body_text)} caracteres")
                        
                        if len(body_text) < 100:
                            print(f"      ⚠ Página parece vazia ou não carregou corretamente")
                        
                        # Scroll múltiplo para carregar todos os produtos dinâmicos (lazy loading)
                        last_height = driver.execute_script("return document.body.scrollHeight")
                        scroll_attempts = 0
                        max_scrolls = 5
                        
                        while scroll_attempts < max_scrolls:
                            # Scroll para baixo
                            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                            time.sleep(2)
                            
                            # Scroll para cima um pouco
                            driver.execute_script("window.scrollTo(0, document.body.scrollHeight * 0.7);")
                            time.sleep(1)
                            
                            # Verificar se há mais conteúdo
                            new_height = driver.execute_script("return document.body.scrollHeight")
                            if new_height == last_height:
                                break
                            last_height = new_height
                            scroll_attempts += 1
                        
                        # Voltar ao topo
                        driver.execute_script("window.scrollTo(0, 0);")
                        time.sleep(1)
                        
                        # Extrair produtos desta categoria (HTML puro)
                        produtos_categoria = self.extrair_produtos_html(driver, 'guanabara', categoria['nome'])
                        print(f"  Retorno de extrair_produtos_html: {len(produtos_categoria) if produtos_categoria else 0} produtos")
                        
                        if produtos_categoria and len(produtos_categoria) > 0:
                            print(f"  ✓ {len(produtos_categoria)} produtos encontrados em {categoria['nome']}")
                            # Mostrar primeiros 3 produtos encontrados
                            for i, p in enumerate(produtos_categoria[:3], 1):
                                print(f"    {i}. {p.get('nome', 'N/A')} - R$ {p.get('preco', 0):.2f}")
                            produtos.extend(produtos_categoria)
                            print(f"  Total acumulado: {len(produtos)} produtos")
                        else:
                            print(f"  ⚠ Nenhum produto encontrado em {categoria['nome']}")
                            # Tentar capturar HTML da página para debug
                            try:
                                page_source = driver.page_source
                                texto_page = BeautifulSoup(page_source, 'html.parser').get_text()
                                tem_arroz = 'arroz' in texto_page.lower()
                                tem_preco = bool(re.search(r'\d+[,.]\d{2}', texto_page))
                                print(f"    Debug - Tem 'arroz': {tem_arroz}, Tem preço: {tem_preco}")
                                print(f"    Tamanho do texto: {len(texto_page)} caracteres")
                            except Exception as e:
                                print(f"    Erro ao verificar página: {e}")
                    except Exception as e:
                        print(f"  ✗ Erro ao processar categoria {categoria['nome']}: {e}")
                        import traceback
                        traceback.print_exc()
                        continue
            
        except Exception as e:
            print(f"Erro ao fazer scraping do Guanabara: {e}")
            import traceback
            traceback.print_exc()
        finally:
            if driver:
                try:
                    driver.quit()
                except:
                    pass
        
        print(f"\n=== RESUMO SCRAPING GUANABARA ===")
        print(f"Total de produtos encontrados: {len(produtos)}")
        if produtos:
            print(f"\nPrimeiros 5 produtos:")
            for i, p in enumerate(produtos[:5], 1):
                print(f"  {i}. {p.get('nome', 'N/A')} - R$ {p.get('preco', 0):.2f} - {p.get('categoria', 'N/A')}")
        else:
            print("  NENHUM PRODUTO ENCONTRADO!")
            print("  Verifique os logs acima para identificar o problema.")
        return produtos
    
    def scrape_mundial(self):
        """Scraping do site Mundial"""
        produtos = []
        try:
            driver = self.setup_selenium()
            driver.get(MERCADOS['mundial']['url'])
            time.sleep(5)
            
            # Tentar extrair produtos diretamente do HTML primeiro
            produtos_html = self.extrair_produtos_html(driver, 'mundial')
            if produtos_html:
                produtos.extend(produtos_html)
            
            encarte_urls = self.encontrar_encarte_url(driver, 'mundial')
            
            for tipo, url in encarte_urls:
                if tipo == 'pdf':
                    filename = f"mundial_{datetime.now().strftime('%Y%m%d')}.pdf"
                    self.download_pdf(url, filename)
                elif tipo == 'image':
                    if url.startswith('http'):
                        filename = f"mundial_{datetime.now().strftime('%Y%m%d')}.jpg"
                        self.download_image(url, filename)
            
            driver.quit()
        except Exception as e:
            print(f"Erro ao fazer scraping do Mundial: {e}")
        
        return produtos
    
    def scrape_supermarket(self):
        """Scraping do site Supermarket"""
        produtos = []
        try:
            driver = self.setup_selenium()
            driver.get(MERCADOS['supermarket']['url'])
            time.sleep(5)
            
            # Tentar extrair produtos diretamente do HTML primeiro
            produtos_html = self.extrair_produtos_html(driver, 'supermarket')
            if produtos_html:
                produtos.extend(produtos_html)
            
            encarte_urls = self.encontrar_encarte_url(driver, 'supermarket')
            
            for tipo, url in encarte_urls:
                if tipo == 'pdf':
                    filename = f"supermarket_{datetime.now().strftime('%Y%m%d')}.pdf"
                    self.download_pdf(url, filename)
                elif tipo == 'image':
                    if url.startswith('http'):
                        filename = f"supermarket_{datetime.now().strftime('%Y%m%d')}.jpg"
                        self.download_image(url, filename)
            
            driver.quit()
        except Exception as e:
            print(f"Erro ao fazer scraping do Supermarket: {e}")
        
        return produtos
    
    def scrape_prezunic(self):
        """Scraping do site Prezunic"""
        produtos = []
        try:
            driver = self.setup_selenium()
            driver.get(MERCADOS['prezunic']['url'])
            time.sleep(5)
            
            # Tentar extrair produtos diretamente do HTML primeiro
            produtos_html = self.extrair_produtos_html(driver, 'prezunic')
            if produtos_html:
                produtos.extend(produtos_html)
            
            encarte_urls = self.encontrar_encarte_url(driver, 'prezunic')
            
            for tipo, url in encarte_urls:
                if tipo == 'pdf':
                    filename = f"prezunic_{datetime.now().strftime('%Y%m%d')}.pdf"
                    self.download_pdf(url, filename)
                elif tipo == 'image':
                    if url.startswith('http'):
                        filename = f"prezunic_{datetime.now().strftime('%Y%m%d')}.jpg"
                        self.download_image(url, filename)
            
            driver.quit()
        except Exception as e:
            print(f"Erro ao fazer scraping do Prezunic: {e}")
        
        return produtos
    
    def scrape_all(self):
        """Executa scraping de todos os mercados"""
        print("Iniciando scraping de todos os mercados...")
        resultados = {
            'guanabara': self.scrape_guanabara(),
            'mundial': self.scrape_mundial(),
            'supermarket': self.scrape_supermarket(),
            'prezunic': self.scrape_prezunic()
        }
        return resultados


