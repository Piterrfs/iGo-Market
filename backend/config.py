import os
from dotenv import load_dotenv

load_dotenv()

# URLs dos mercados
MERCADOS = {
    'guanabara': {
        'url': 'https://www.supermercadosguanabara.com.br/encarte',
        'nome': 'Guanabara'
    },
    'mundial': {
        'url': 'https://www.supermercadosmundial.com.br/ofertas',
        'nome': 'Mundial'
    },
    'supermarket': {
        'url': 'https://redesupermarket.com.br/ofertas/',
        'nome': 'Supermarket'
    },
    'prezunic': {
        'url': 'https://www.prezunic.com.br/ofertas',
        'nome': 'Prezunic'
    }
}

# Configurações de scraping
SCRAPING_CONFIG = {
    'timeout': 30,
    'retry_attempts': 3,
    'delay_between_requests': 2
}

# Configurações de OCR
OCR_CONFIG = {
    'lang': 'por',
    'psm': 6  # Assume uniform block of text
}

# Diretórios
DATA_DIR = os.path.join(os.path.dirname(__file__), '..', 'data')
IMAGES_DIR = os.path.join(DATA_DIR, 'images')
CSV_DIR = os.path.join(DATA_DIR, 'csv')

# Criar diretórios se não existirem
os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(IMAGES_DIR, exist_ok=True)
os.makedirs(CSV_DIR, exist_ok=True)


