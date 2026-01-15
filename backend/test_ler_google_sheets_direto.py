"""Teste direto da função ler_google_sheets"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import ler_google_sheets

print("=" * 60)
print("TESTE DIRETO DA FUNÇÃO ler_google_sheets()")
print("=" * 60)

try:
    resultado = ler_google_sheets()
    
    if resultado:
        print(f"\n✓ SUCESSO!")
        print(f"Total de produtos: {len(resultado)}")
        print(f"\nPrimeiros 5 produtos:")
        for i, produto in enumerate(resultado[:5], 1):
            print(f"  {i}. {produto.get('Produto')} - {produto.get('Marca')} - {produto.get('Menor Preço')}")
    else:
        print("\n✗ FUNÇÃO RETORNOU VAZIO")
        print("Verifique os logs acima para ver o erro")
        
except Exception as e:
    print(f"\n✗ ERRO: {e}")
    import traceback
    traceback.print_exc()
