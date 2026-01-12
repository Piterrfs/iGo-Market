import requests
from bs4 import BeautifulSoup
import time
import os
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
from pdf2image import convert_from_path
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
            try:
                images = convert_from_path(pdf_path, dpi=300)
                image_paths = []
                for i, image in enumerate(images):
                    image_filename = filename.replace('.pdf', f'_page_{i+1}.jpg')
                    image_path = os.path.join(IMAGES_DIR, image_filename)
                    image.save(image_path, 'JPEG')
                    image_paths.append(image_path)
                return image_paths
            except Exception as e:
                print(f"Erro ao converter PDF para imagem: {e}")
                # Tentar com PyMuPDF como alternativa
                try:
                    doc = fitz.open(pdf_path)
                    image_paths = []
                    for page_num in range(len(doc)):
                        page = doc[page_num]
                        pix = page.get_pixmap(matrix=fitz.Matrix(2, 2))
                        image_filename = filename.replace('.pdf', f'_page_{page_num+1}.png')
                        image_path = os.path.join(IMAGES_DIR, image_filename)
                        pix.save(image_path)
                        image_paths.append(image_path)
                    doc.close()
                    return image_paths
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
            # Procurar por links de PDF
            pdf_links = driver.find_elements(By.XPATH, "//a[contains(@href, '.pdf')]")
            for link in pdf_links:
                href = link.get_attribute('href')
                if href:
                    encarte_urls.append(('pdf', href))
            
            # Procurar por imagens de encarte
            img_elements = driver.find_elements(By.TAG_NAME, 'img')
            for img in img_elements:
                src = img.get_attribute('src')
                if src and ('encarte' in src.lower() or 'oferta' in src.lower() or 'promocao' in src.lower()):
                    if src.startswith('http'):
                        encarte_urls.append(('image', src))
                    else:
                        # URL relativa, construir URL completa
                        base_url = MERCADOS[mercado]['url']
                        if not src.startswith('/'):
                            src = '/' + src
                        encarte_urls.append(('image', base_url.rsplit('/', 1)[0] + src))
            
            # Procurar por canvas ou elementos que possam conter o encarte
            canvas_elements = driver.find_elements(By.TAG_NAME, 'canvas')
            if canvas_elements:
                # Tentar capturar screenshot do canvas
                for i, canvas in enumerate(canvas_elements):
                    screenshot_path = os.path.join(IMAGES_DIR, f"{mercado}_canvas_{i}.png")
                    canvas.screenshot(screenshot_path)
                    encarte_urls.append(('image', screenshot_path))
        
        except Exception as e:
            print(f"Erro ao encontrar encarte: {e}")
        
        return encarte_urls
    
    def scrape_guanabara(self):
        """Scraping do site Guanabara"""
        produtos = []
        try:
            driver = self.setup_selenium()
            driver.get(MERCADOS['guanabara']['url'])
            time.sleep(5)  # Aguarda carregamento
            
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
                    else:
                        # Já é um arquivo local (screenshot)
                        pass
            
            driver.quit()
        except Exception as e:
            print(f"Erro ao fazer scraping do Guanabara: {e}")
        
        return produtos
    
    def scrape_mundial(self):
        """Scraping do site Mundial"""
        produtos = []
        try:
            driver = self.setup_selenium()
            driver.get(MERCADOS['mundial']['url'])
            time.sleep(5)
            
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


