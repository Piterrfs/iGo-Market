"""Script de teste para scraping do Guanabara"""
from scraper import MercadoScraper
import time

scraper = MercadoScraper()
driver = scraper.setup_selenium()

try:
    print("Acessando página de Açougue do Guanabara...")
    driver.get('https://www.supermercadosguanabara.com.br/produtos/42')
    time.sleep(8)
    
    html = driver.page_source
    print(f'\nHTML carregado: {len(html)} caracteres')
    print(f'Contém "produto": {"produto" in html.lower()}')
    print(f'Contém "product": {"product" in html.lower()}')
    print(f'Contém "R$": {"R$" in html}')
    print(f'Contém "preco": {"preco" in html.lower()}')
    
    # Contar quantos R$ tem na página
    count_r = html.count('R$')
    print(f'\nTotal de "R$" encontrados: {count_r}')
    
    # Extrair produtos
    print('\nExtraindo produtos...')
    produtos = scraper.extrair_produtos_html(driver, 'guanabara', 'Açougue')
    
    print(f'\nProdutos encontrados: {len(produtos)}')
    if produtos:
        print('\nPrimeiros 5 produtos:')
        for i, p in enumerate(produtos[:5], 1):
            print(f'{i}. {p["nome"]} - R$ {p["preco"]:.2f} - {p["quantidade"]}')
    else:
        print('\nNENHUM PRODUTO ENCONTRADO!')
        print('\nVamos ver o HTML...')
        # Salvar HTML para análise
        with open('test_html.html', 'w', encoding='utf-8') as f:
            f.write(html)
        print('HTML salvo em test_html.html')
        
        # Procurar por padrões de preço no HTML
        import re
        precos = re.findall(r'R\$\s*\d+[,.]\d{2}|\d+[,.]\d{2}', html)
        print(f'\nPadrões de preço encontrados no HTML: {len(precos)}')
        if precos:
            print('Primeiros 10:')
            for p in precos[:10]:
                print(f'  - {p}')
        
finally:
    driver.quit()
