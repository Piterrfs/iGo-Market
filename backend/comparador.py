import pandas as pd
from datetime import datetime
import os
from config import CSV_DIR, DATA_DIR

class ComparadorPrecos:
    def __init__(self):
        self.df = None
    
    def carregar_dados(self, arquivo_csv=None):
        """Carrega dados do CSV ou cria DataFrame vazio"""
        if arquivo_csv and os.path.exists(arquivo_csv):
            self.df = pd.read_csv(arquivo_csv)
        else:
            # Buscar CSV mais recente (excluir tabelas comparativas)
            csv_files = [f for f in os.listdir(CSV_DIR) if f.endswith('.csv') and not f.startswith('tabela_comparativa')]
            if csv_files:
                latest = max(csv_files, key=lambda f: os.path.getmtime(os.path.join(CSV_DIR, f)))
                self.df = pd.read_csv(os.path.join(CSV_DIR, latest))
            else:
                self.df = pd.DataFrame(columns=[
                    'segmento', 'produto', 'marca', 'quantidade', 'preco', 
                    'preco_oferta', 'mercado', 'data_extracao', 'url_fonte'
                ])
        
        # Garantir que campos obrigatórios existam
        if self.df is not None and not self.df.empty:
            # Adicionar campos faltantes com valores padrão
            if 'segmento' not in self.df.columns:
                self.df['segmento'] = 'Outros'
            if 'preco_oferta' not in self.df.columns:
                self.df['preco_oferta'] = self.df.get('preco', 0)
            if 'url_fonte' not in self.df.columns:
                self.df['url_fonte'] = ''
    
    def comparar_produtos(self, produto_busca=None, marca=None, quantidade=None):
        """Compara preços de produtos com lógica de Business Intelligence"""
        if self.df is None or self.df.empty:
            return []
        
        df_filtrado = self.df.copy()
        
        # Filtrar por produto
        if produto_busca:
            df_filtrado = df_filtrado[
                df_filtrado['produto'].str.contains(produto_busca, case=False, na=False)
            ]
        
        # Filtrar por marca
        if marca:
            df_filtrado = df_filtrado[
                df_filtrado['marca'].str.contains(marca, case=False, na=False)
            ]
        
        # Filtrar por quantidade
        if quantidade:
            df_filtrado = df_filtrado[
                df_filtrado['quantidade'].str.contains(quantidade, case=False, na=False)
            ]
        
        # Agrupar por produto, marca e quantidade para comparar (SKU único)
        resultados = []
        grupos = df_filtrado.groupby(['produto', 'marca', 'quantidade'])
        
        for (prod, marc, qtd), grupo in grupos:
            grupo_ordenado = grupo.sort_values('preco')
            menor_preco = grupo_ordenado.iloc[0]
            
            # Calcular economia e preço médio da concorrência
            preco_medio_concorrencia = grupo_ordenado['preco'].mean()
            economia = 0
            percentual_economia = 0
            
            if len(grupo_ordenado) > 1:
                segundo_menor = grupo_ordenado.iloc[1]
                economia = segundo_menor['preco'] - menor_preco['preco']
                percentual_economia = (economia / segundo_menor['preco']) * 100
            
            # Identificar se é "isca" (desconto > 30% em relação à segunda menor oferta)
            is_isca = percentual_economia > 30
            
            # Calcular delta do preço em relação à média da concorrência
            delta_medio = preco_medio_concorrencia - menor_preco['preco']
            percentual_delta_medio = (delta_medio / preco_medio_concorrencia * 100) if preco_medio_concorrencia > 0 else 0
            
            resultados.append({
                'produto': prod,
                'marca': marc,
                'quantidade': qtd,
                'segmento': menor_preco.get('segmento', 'Outros'),
                'menor_preco': float(menor_preco['preco']),
                'preco_oferta': float(menor_preco['preco']),
                'preco_medio_concorrencia': round(float(preco_medio_concorrencia), 2),
                'mercado_menor_preco': menor_preco['mercado'],
                'todos_precos': grupo_ordenado[['mercado', 'preco']].to_dict('records'),
                'economia': round(economia, 2),
                'percentual_economia': round(percentual_economia, 2),
                'delta_medio': round(delta_medio, 2),
                'percentual_delta_medio': round(percentual_delta_medio, 2),
                'is_isca': bool(is_isca),
                'mercados_comparados': grupo_ordenado['mercado'].unique().tolist(),
                'url_fonte': menor_preco.get('url_fonte', '')
            })
        
        # Ordenar por economia (maior primeiro)
        resultados.sort(key=lambda x: x['economia'], reverse=True)
        
        return resultados
    
    def buscar_produto(self, termo_busca):
        """Busca produtos por termo"""
        if self.df is None or self.df.empty:
            return []
        
        df_filtrado = self.df[
            (self.df['produto'].str.contains(termo_busca, case=False, na=False)) |
            (self.df['marca'].str.contains(termo_busca, case=False, na=False))
        ]
        
        return df_filtrado.to_dict('records')
    
    def exportar_planilha(self, nome_arquivo=None):
        """Exporta dados para planilha Excel"""
        if self.df is None or self.df.empty:
            return None
        
        if not nome_arquivo:
            nome_arquivo = f"comparacao_precos_{datetime.now().strftime('%Y%m%d')}.xlsx"
        
        caminho_arquivo = os.path.join(DATA_DIR, nome_arquivo)
        
        # Criar Excel com múltiplas abas
        with pd.ExcelWriter(caminho_arquivo, engine='openpyxl') as writer:
            # Aba 1: Todos os dados
            self.df.to_excel(writer, sheet_name='Todos os Produtos', index=False)
            
            # Aba 2: Melhores ofertas
            melhores_ofertas = []
            grupos = self.df.groupby(['produto', 'marca', 'quantidade'])
            for (prod, marc, qtd), grupo in grupos:
                menor = grupo.loc[grupo['preco'].idxmin()]
                melhores_ofertas.append({
                    'Produto': prod,
                    'Marca': marc,
                    'Quantidade': qtd,
                    'Menor Preço': menor['preco'],
                    'Mercado': menor['mercado'],
                    'Economia vs 2º Menor': ''
                })
            
            df_melhores = pd.DataFrame(melhores_ofertas)
            df_melhores.to_excel(writer, sheet_name='Melhores Ofertas', index=False)
            
            # Aba 3: Comparação por mercado
            for mercado in self.df['mercado'].unique():
                df_mercado = self.df[self.df['mercado'] == mercado]
                df_mercado.to_excel(writer, sheet_name=f'{mercado}', index=False)
        
        return caminho_arquivo
    
    def calcular_carrinho_mais_barato(self, produtos_ids):
        """
        Calcula o carrinho mais barato para uma lista de produtos.
        produtos_ids: lista de dicionários com {'produto': nome, 'marca': marca, 'quantidade': qtd}
        Retorna: dicionário com total por mercado e recomendação
        """
        if self.df is None or self.df.empty:
            return None
        
        # Encontrar o menor preço de cada produto solicitado
        produtos_encontrados = {}
        for produto_info in produtos_ids:
            produto = produto_info.get('produto', '')
            marca = produto_info.get('marca', '')
            quantidade = produto_info.get('quantidade', '')
            
            # Filtrar produtos que correspondem
            df_filtrado = self.df.copy()
            if produto:
                df_filtrado = df_filtrado[
                    df_filtrado['produto'].str.contains(produto, case=False, na=False)
                ]
            if marca:
                df_filtrado = df_filtrado[
                    df_filtrado['marca'].str.contains(marca, case=False, na=False)
                ]
            if quantidade:
                df_filtrado = df_filtrado[
                    df_filtrado['quantidade'].str.contains(quantidade, case=False, na=False)
                ]
            
            # Agrupar por SKU e pegar o menor preço
            grupos = df_filtrado.groupby(['produto', 'marca', 'quantidade'])
            for (prod, marc, qtd), grupo in grupos:
                menor = grupo.loc[grupo['preco'].idxmin()]
                chave = f"{prod}_{marc}_{qtd}"
                produtos_encontrados[chave] = {
                    'produto': prod,
                    'marca': marc,
                    'quantidade': qtd,
                    'menor_preco': float(menor['preco']),
                    'mercado': menor['mercado']
                }
        
        # Calcular total por mercado
        totais_por_mercado = {}
        produtos_por_mercado = {}
        
        for chave, produto_info in produtos_encontrados.items():
            mercado = produto_info['mercado']
            preco = produto_info['menor_preco']
            
            if mercado not in totais_por_mercado:
                totais_por_mercado[mercado] = 0
                produtos_por_mercado[mercado] = []
            
            totais_por_mercado[mercado] += preco
            produtos_por_mercado[mercado].append(produto_info)
        
        # Encontrar mercado mais barato
        mercado_mais_barato = min(totais_por_mercado.items(), key=lambda x: x[1])[0] if totais_por_mercado else None
        
        return {
            'totais_por_mercado': {mercado: round(total, 2) for mercado, total in totais_por_mercado.items()},
            'produtos_por_mercado': produtos_por_mercado,
            'mercado_mais_barato': mercado_mais_barato,
            'total_mais_barato': round(totais_por_mercado.get(mercado_mais_barato, 0), 2) if mercado_mais_barato else 0,
            'economia_total': round(max(totais_por_mercado.values()) - min(totais_por_mercado.values()), 2) if totais_por_mercado else 0
        }

