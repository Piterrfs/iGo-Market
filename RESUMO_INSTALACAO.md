# ✅ Instalação Concluída - iGo Market

## Status da Instalação

### ✅ Backend (Python)
- **Ambiente virtual criado**: `backend/venv/`
- **Dependências instaladas**: Todas as bibliotecas Python foram instaladas com sucesso
- **Versão Python**: 3.13.2
- **Pacotes instalados**:
  - Flask 3.1.2
  - Selenium 4.39.0
  - Pandas 2.3.3
  - OpenCV 4.12.0
  - Tesseract (pytesseract) 0.3.13
  - E todas as outras dependências

### ✅ Frontend (Next.js)
- **Dependências instaladas**: 369 pacotes instalados
- **Versão Node.js**: v23.1.0
- **Framework**: Next.js 14.0.4
- **React**: 18.2.0

### ✅ Dados de Exemplo
- **Arquivo criado**: `data/csv/produtos_20260112.csv`
- **Total de produtos**: 11 produtos de exemplo
- **Mercados incluídos**: Supermarket, Guanabara, Mundial, Prezunic

### ✅ Estrutura de Diretórios
- `data/csv/` - Arquivos CSV com dados extraídos
- `data/images/` - Imagens dos encartes baixados
- `backend/venv/` - Ambiente virtual Python
- `frontend/node_modules/` - Dependências Node.js

## Próximos Passos

### 1. Iniciar o Sistema

**Opção A - Script Automático (Windows):**
```bash
start.bat
```

**Opção B - Manual:**

Terminal 1 - Backend:
```bash
cd backend
.\venv\Scripts\Activate.ps1
python app.py
```

Terminal 2 - Frontend:
```bash
cd frontend
npm run dev
```

### 2. Acessar o App

Abra seu navegador em: **http://localhost:8000**

### 3. Testar Funcionalidades

1. **Buscar Produtos**: Digite "arroz" ou "leite" na busca
2. **Ver Comparações**: Veja os preços comparados entre mercados
3. **Baixar Planilha**: Clique em "Baixar Planilha" para exportar dados
4. **Atualizar Dados**: Clique em "Atualizar Dados" para fazer scraping real

## ⚠️ Observações Importantes

### Tesseract OCR
Para o scraping real funcionar, você precisa instalar o Tesseract OCR:

1. **Windows**: Baixe de https://github.com/UB-Mannheim/tesseract/wiki
2. Instale em `C:\Program Files\Tesseract-OCR`
3. Baixe o pacote de idioma português (por.traineddata)
4. Coloque em `C:\Program Files\Tesseract-OCR\tessdata\`

**Nota**: O sistema funciona com dados de exemplo mesmo sem Tesseract instalado.

### Chrome/Chromium
O Selenium precisa do Chrome instalado. O webdriver-manager baixará automaticamente o ChromeDriver.

## Testando a API

Você pode testar os endpoints da API:

```powershell
# Health check
Invoke-WebRequest -Uri http://localhost:5000/api/health

# Estatísticas
Invoke-WebRequest -Uri http://localhost:5000/api/estatisticas

# Buscar produtos
Invoke-WebRequest -Uri "http://localhost:5000/api/buscar?q=arroz"

# Comparar preços
Invoke-WebRequest -Uri "http://localhost:5000/api/comparar?produto=leite"
```

## Arquivos Importantes

- `README.md` - Documentação principal
- `INSTALACAO.md` - Guia detalhado de instalação
- `USO.md` - Guia de uso do sistema
- `backend/scripts/criar_dados_exemplo.py` - Script para gerar dados de teste
- `backend/scripts/testar_api.py` - Script para testar API

## Suporte

Se encontrar problemas:
1. Verifique se o backend está rodando na porta 5000
2. Verifique se o frontend está rodando na porta 8000
3. Confira os logs no terminal
4. Veja `INSTALACAO.md` para solução de problemas comuns


