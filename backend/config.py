import os
from dotenv import load_dotenv

load_dotenv()

# URLs dos mercados
MERCADOS = {
    'guanabara': {
        'url': 'https://www.supermercadosguanabara.com.br/encarte',
        'nome': 'Guanabara',
        'categorias': [
            {'nome': 'Açougue', 'url': 'https://www.supermercadosguanabara.com.br/produtos/42'},
            {'nome': 'Frios e Laticínios', 'url': 'https://www.supermercadosguanabara.com.br/produtos/62'},
            {'nome': 'Limpeza', 'url': 'https://www.supermercadosguanabara.com.br/produtos/102'},
            {'nome': 'Bebida', 'url': 'https://www.supermercadosguanabara.com.br/produtos/82'},
            {'nome': 'Biscoito', 'url': 'https://www.supermercadosguanabara.com.br/produtos/32'},
            {'nome': 'Massas', 'url': 'https://www.supermercadosguanabara.com.br/produtos/22'},
            {'nome': 'Conservas', 'url': 'https://www.supermercadosguanabara.com.br/produtos/92'},
            {'nome': 'Cantinho do Bebê', 'url': 'https://www.supermercadosguanabara.com.br/produtos/203'},
            {'nome': 'Embutidos', 'url': 'https://www.supermercadosguanabara.com.br/produtos/52'},
            {'nome': 'Matinais e Padaria', 'url': 'https://www.supermercadosguanabara.com.br/produtos/12'},
            {'nome': 'Salgados', 'url': 'https://www.supermercadosguanabara.com.br/produtos/72'},
            {'nome': 'Cereais e Farináceos', 'url': 'https://www.supermercadosguanabara.com.br/produtos'},
            {'nome': 'Bombom', 'url': 'https://www.supermercadosguanabara.com.br/produtos/152'}
        ]
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
EXCEL_DIR = os.path.join(DATA_DIR, 'excel')

# Criar diretórios se não existirem
os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(IMAGES_DIR, exist_ok=True)
os.makedirs(CSV_DIR, exist_ok=True)
os.makedirs(EXCEL_DIR, exist_ok=True)


