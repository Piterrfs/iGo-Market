# iGo Market - Comparador de Preços RJ

App web mobile para comparação de preços de produtos de supermercados no Rio de Janeiro.

## Funcionalidades

- 🔍 Busca de produtos por nome
- 💰 Comparação de preços entre mercados (Guanabara, Mundial, Supermarket, Prezunic)
- 📊 Exportação de dados para planilha
- 🔄 Atualização diária automática
- 📱 Interface mobile-first

## Estrutura do Projeto

```
├── backend/          # API Python com scraping e OCR
├── frontend/         # App Next.js mobile-first
├── data/            # Dados extraídos e planilhas
└── scripts/         # Scripts de automação
```

## Instalação

### Backend
```bash
cd backend
pip install -r requirements.txt
```

### Frontend
```bash
cd frontend
npm install
```

## Uso

### Iniciar Backend
```bash
cd backend
python app.py
```

### Iniciar Frontend
```bash
cd frontend
npm run dev
```

Acesse: http://localhost:8000

## Mercados Monitorados

- Supermercados Guanabara
- Supermercados Mundial
- Rede Supermarket
- Prezunic

## Documentação Adicional

- [Guia de Instalação](INSTALACAO.md) - Instruções detalhadas de instalação
- [Guia de Uso](USO.md) - Como usar o sistema
- [Instalação Tesseract](backend/scripts/instalar_tesseract.md) - Configuração do OCR

## Início Rápido

### Windows
```bash
# Execute o script de inicialização
start.bat
```

### Linux/Mac
```bash
chmod +x start.sh
./start.sh
```

### Manual
1. Instale as dependências (veja INSTALACAO.md)
2. Inicie o backend: `cd backend && python app.py`
3. Inicie o frontend: `cd frontend && npm run dev`
4. Acesse http://localhost:8000

## Estrutura de Dados

Os dados são extraídos e normalizados com:
- **Produto**: Nome genérico (ex: Arroz Branco)
- **Marca**: Marca específica (ex: Tio João)
- **Quantidade**: Unidade (ex: 5kg, 1L)
- **Preço**: Preço em reais
- **Mercado**: Loja de origem
- **Data**: Data da extração

## Funcionalidades Avançadas

- 🔍 Busca inteligente por produto/marca
- 💰 Comparação automática de preços por SKU (mesma marca e quantidade)
- 📊 Identificação de "iscas" (descontos > 30% em relação à segunda menor oferta)
- 📈 Cálculo de economia percentual e delta em relação à média da concorrência
- 🛒 Cálculo de carrinho mais barato (soma de múltiplos produtos)
- 📱 Interface responsiva mobile-first
- 🔄 Atualização automática diária (02:00) e hortifruti às terças (22:00)
- 📥 Exportação para Excel com múltiplas abas
- 🏷️ Classificação automática por segmento (Mercearia, Açougue, Laticínios, etc.)
- 🔄 Normalização inteligente de produtos (ex: "Arroz 5kg T. Joao" = "Arroz Tio João 5kg")

## API Endpoints

### GET /api/health
Verifica se a API está funcionando.

### GET /api/estatisticas
Retorna estatísticas dos dados (total de produtos, mercados, preços, etc.)

### GET /api/buscar?q=termo
Busca produtos por termo (produto ou marca).

### GET /api/comparar?produto=nome&marca=marca&quantidade=qtd
Compara preços de produtos específicos. Retorna:
- Menor preço e mercado
- Todos os preços por mercado
- Economia em relação ao segundo menor preço
- Identificação de "iscas" (desconto > 30%)
- Delta em relação à média da concorrência

### POST /api/scrape
Executa scraping de todos os mercados e processa com OCR.

### GET /api/planilha
Gera e retorna planilha Excel com múltiplas abas.

### POST /api/carrinho
Calcula o carrinho mais barato para uma lista de produtos.
**Body JSON:**
```json
{
  "produtos": [
    {"produto": "arroz", "marca": "tio joao", "quantidade": "5kg"},
    {"produto": "leite", "marca": "italac", "quantidade": "1L"}
  ]
}
```
**Retorna:** Totais por mercado, produtos por mercado, mercado mais barato e economia total.

