# Guia de Instalação - iGo Market

## Pré-requisitos

### Backend (Python)
- Python 3.8 ou superior
- Tesseract OCR instalado (veja `backend/scripts/instalar_tesseract.md`)
- Chrome/Chromium instalado (para Selenium)

### Frontend (Node.js)
- Node.js 18 ou superior
- npm ou yarn

## Instalação Passo a Passo

### 1. Backend

```bash
# Navegar para o diretório backend
cd backend

# Criar ambiente virtual (recomendado)
python -m venv venv

# Ativar ambiente virtual
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Instalar dependências
pip install -r requirements.txt

# Instalar Tesseract OCR (veja instruções específicas)
# Windows: Baixe de https://github.com/UB-Mannheim/tesseract/wiki
# Linux: sudo apt-get install tesseract-ocr tesseract-ocr-por
# Mac: brew install tesseract tesseract-lang
```

### 2. Frontend

```bash
# Navegar para o diretório frontend
cd frontend

# Instalar dependências
npm install
```

## Executando o Projeto

### Terminal 1 - Backend

```bash
cd backend
python app.py
```

O backend estará disponível em: http://localhost:5000

### Terminal 2 - Frontend

```bash
cd frontend
npm run dev
```

O frontend estará disponível em: http://localhost:8000

## Primeira Execução

1. Acesse http://localhost:8000
2. Clique em "Atualizar Dados" para fazer o primeiro scraping
3. Aguarde o processamento (pode levar alguns minutos)
4. Após concluir, você poderá buscar produtos

## Agendamento Automático (Opcional)

Para executar atualizações automáticas:

```bash
cd backend
python scheduler.py
```

Isso executará atualizações:
- Diárias às 02:00
- Especiais de hortifruti toda terça-feira às 22:00

## Solução de Problemas

### Erro: Tesseract não encontrado
- Verifique se o Tesseract está instalado
- Configure o caminho no arquivo `ocr_processor.py` se necessário

### Erro: ChromeDriver
- O webdriver-manager baixará automaticamente o ChromeDriver
- Certifique-se de ter Chrome/Chromium instalado

### Erro: Porta já em uso
- Backend: Altere a porta em `app.py` (linha final)
- Frontend: Use `npm run dev -- -p 3001` para outra porta


