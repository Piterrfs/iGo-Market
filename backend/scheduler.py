import schedule
import time
import os
from datetime import datetime
from scraper import MercadoScraper
from ocr_processor import OCRProcessor
from comparador import ComparadorPrecos
from config import CSV_DIR
import pandas as pd

def atualizar_dados():
    """Função para atualização diária dos dados"""
    print(f"Iniciando atualização diária em {datetime.now()}")
    
    scraper = MercadoScraper()
    ocr = OCRProcessor()
    
    # Executar scraping
    resultados = scraper.scrape_all()
    
    # Processar com OCR
    todos_produtos = []
    for mercado in ['guanabara', 'mundial', 'supermarket', 'prezunic']:
        produtos = ocr.processar_imagens_mercado(mercado.title())
        todos_produtos.extend(produtos)
    
    # Salvar dados
    if todos_produtos:
        df = pd.DataFrame(todos_produtos)
        csv_path = os.path.join(CSV_DIR, f"produtos_{datetime.now().strftime('%Y%m%d')}.csv")
        df.to_csv(csv_path, index=False)
        print(f"Dados salvos em {csv_path}")
    
    print(f"Atualização concluída. {len(todos_produtos)} produtos processados.")

# Agendar atualização diária às 2h da manhã
schedule.every().day.at("02:00").do(atualizar_dados)

# Agendar atualização especial de hortifruti toda terça-feira às 22h
schedule.every().tuesday.at("22:00").do(atualizar_dados)

if __name__ == '__main__':
    print("Agendador iniciado. Atualizações programadas:")
    print("- Diária: 02:00")
    print("- Hortifruti (terça): 22:00")
    
    while True:
        schedule.run_pending()
        time.sleep(60)  # Verifica a cada minuto

