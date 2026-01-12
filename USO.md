# Guia de Uso - iGo Market

## Início Rápido

### 1. Preparar Dados de Exemplo (Para Testes)

Se você quiser testar o sistema sem fazer scraping real:

```bash
cd backend
python scripts/criar_dados_exemplo.py
```

Isso criará um arquivo CSV com dados de exemplo baseados na documentação.

### 2. Iniciar o Sistema

**Terminal 1 - Backend:**
```bash
cd backend
python app.py
```

**Terminal 2 - Frontend:**
```bash
cd frontend
npm run dev
```

### 3. Acessar o App

Abra seu navegador em: **http://localhost:8000**

## Funcionalidades

### Buscar Produtos

1. Digite o nome do produto na barra de busca (ex: "arroz", "leite", "sabão")
2. Clique em "Buscar" ou pressione Enter
3. Veja os resultados comparando preços entre mercados

### Atualizar Dados

1. Clique no botão "Atualizar Dados"
2. O sistema fará scraping de todos os mercados
3. Processará as imagens com OCR
4. Salvará os dados em CSV

⚠️ **Nota:** O scraping real pode levar vários minutos e requer:
- Tesseract OCR instalado
- Chrome/Chromium instalado
- Conexão com internet

### Baixar Planilha

1. Clique em "Baixar Planilha"
2. Um arquivo Excel será gerado com:
   - Aba 1: Todos os produtos
   - Aba 2: Melhores ofertas
   - Abas adicionais: Produtos por mercado

## API Endpoints

### GET /api/health
Verifica se a API está funcionando.

### GET /api/estatisticas
Retorna estatísticas dos dados (total de produtos, mercados, etc.)

### GET /api/buscar?q=termo
Busca produtos por termo.

### GET /api/comparar?produto=nome&marca=marca&quantidade=qtd
Compara preços de produtos específicos.

### POST /api/scrape
Executa scraping de todos os mercados.

### GET /api/planilha
Gera e retorna planilha Excel.

## Testar API

```bash
cd backend
python scripts/testar_api.py
```

## Estrutura de Dados

Os dados são salvos em `data/csv/produtos_YYYYMMDD.csv` com as colunas:

- `produto`: Nome do produto
- `marca`: Marca do produto
- `quantidade`: Quantidade/unidade
- `preco`: Preço em reais
- `mercado`: Nome do mercado
- `data_extracao`: Data da extração
- `segmento`: Categoria do produto

## Atualização Automática

Para executar atualizações automáticas:

```bash
cd backend
python scheduler.py
```

O sistema atualizará:
- **Diariamente às 02:00**
- **Toda terça-feira às 22:00** (especial para hortifruti)

## Dicas

1. **Primeira vez:** Use dados de exemplo para testar antes do scraping real
2. **Performance:** O OCR pode ser lento - seja paciente na primeira execução
3. **Dados:** Os arquivos CSV são salvos em `data/csv/` para histórico
4. **Planilhas:** As planilhas Excel são geradas em `data/` com timestamp


