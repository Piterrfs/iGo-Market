"""Script para testar cada categoria do Guanabara isoladamente"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scraper import MercadoScraper
from config import MERCADOS, IMAGES_DIR
import time
from datetime import datetime

def testar_categoria(categoria_nome, categoria_url):
    """Testa uma categoria específica"""
    print(f"\n{'='*80}")
    print(f"TESTANDO: {categoria_nome}")
    print(f"URL: {categoria_url}")
    print(f"{'='*80}")
    
    scraper = MercadoScraper()
    driver = None
    
    try:
        driver = scraper.setup_selenium()
        driver.get(categoria_url)
        
        # Aguardar carregamento
        print("Aguardando carregamento...")
        time.sleep(15)  # Aumentado para 15 segundos
        
        # Scroll múltiplo
        print("Fazendo scroll para carregar conteúdo dinâmico...")
        for i in range(5):
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(2)
            driver.execute_script("window.scrollTo(0, 0);")
            time.sleep(1)
        
        # Verificar conteúdo
        html_content = driver.page_source
        texto_limpo = driver.find_element(By.TAG_NAME, "body").text
        
        print(f"\nEstatísticas da página:")
        print(f"  HTML: {len(html_content)} caracteres")
        print(f"  Texto limpo: {len(texto_limpo)} caracteres")
        print(f"  Contém 'produto': {'produto' in texto_limpo.lower()}")
        print(f"  Contém 'R$': {'R$' in html_content}")
        
        # Contar padrões de preço
        import re
        precos_html = len(re.findall(r'R\$\s*\d+[,.]\d{2}|\d+[,.]\d{2}', html_content))
        precos_texto = len(re.findall(r'R\$\s*\d+[,.]\d{2}|\d+[,.]\d{2}', texto_limpo))
        print(f"  Padrões de preço no HTML: {precos_html}")
        print(f"  Padrões de preço no texto: {precos_texto}")
        
        # Salvar HTML para debug
        debug_file = os.path.join(IMAGES_DIR, f"debug_{categoria_nome.replace(' ', '_')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html")
        with open(debug_file, 'w', encoding='utf-8') as f:
            f.write(html_content)
        print(f"  HTML salvo em: {debug_file}")
        
        # Extrair produtos
        print("\nExtraindo produtos...")
        produtos = scraper.extrair_produtos_html(driver, 'guanabara', categoria_nome)
        
        print(f"\nRESULTADO:")
        print(f"  Produtos encontrados: {len(produtos) if produtos else 0}")
        
        if produtos and len(produtos) > 0:
            print(f"\nPrimeiros 5 produtos:")
            for i, p in enumerate(produtos[:5], 1):
                print(f"  {i}. {p.get('nome', 'N/A')} - R$ {p.get('preco', 0):.2f} - {p.get('quantidade', 'un')}")
            return True, produtos
        else:
            print("  ⚠ NENHUM PRODUTO ENCONTRADO!")
            return False, []
            
    except Exception as e:
        print(f"\n❌ ERRO: {e}")
        import traceback
        traceback.print_exc()
        return False, []
    finally:
        if driver:
            try:
                driver.quit()
            except:
                pass

if __name__ == '__main__':
    from selenium.webdriver.common.by import By
    
    print("="*80)
    print("TESTE DE CATEGORIAS DO GUANABARA")
    print("="*80)
    
    resultados = {}
    
    for categoria in MERCADOS['guanabara']['categorias']:
        sucesso, produtos = testar_categoria(categoria['nome'], categoria['url'])
        resultados[categoria['nome']] = {
            'sucesso': sucesso,
            'produtos': len(produtos) if produtos else 0
        }
        time.sleep(5)  # Pausa entre categorias
    
    # Resumo final
    print("\n" + "="*80)
    print("RESUMO FINAL")
    print("="*80)
    
    total_produtos = 0
    categorias_com_produtos = 0
    
    for cat_nome, resultado in resultados.items():
        status = "✅" if resultado['sucesso'] else "❌"
        print(f"{status} {cat_nome}: {resultado['produtos']} produtos")
        if resultado['sucesso']:
            categorias_com_produtos += 1
            total_produtos += resultado['produtos']
    
    print(f"\nTotal: {categorias_com_produtos}/{len(resultados)} categorias com produtos")
    print(f"Total de produtos encontrados: {total_produtos}")
