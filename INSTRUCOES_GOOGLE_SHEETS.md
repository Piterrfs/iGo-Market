# Instruções para Salvar Produtos no Google Sheets

## Problema Identificado
O Google Apps Script estava travando porque tentava acessar `localhost:5000`, que não é acessível no Google Apps Script.

## Solução

### Opção 1: Usar Dados de Exemplo (Mais Rápido)
O script agora tem dados de exemplo embutidos. Basta executar:

1. Abra: https://script.google.com/u/0/home/projects/1dz-bcrqMqQiOxpabdVE0raR1H-OLzhtHRDLQaQ0XZG6al1hKuOxwL7Lw/edit
2. Cole o código atualizado de `GOOGLE_APPS_SCRIPT_PARA_PRODUTOS.gs`
3. Execute a função `salvarProdutosNoGoogleSheets()`
4. Os dados de exemplo (14 produtos) serão salvos na planilha

### Opção 2: Fazer Upload do JSON (Mais Completo)
1. Faça upload do arquivo `data\csv\produtos_para_google_sheets.json` para o Google Drive
2. O script vai ler automaticamente do Drive
3. Execute a função `salvarProdutosNoGoogleSheets()`

### Opção 3: Copiar Manualmente do Excel
1. Abra o arquivo `data\excel\produtos_completos.xlsx`
2. Copie os dados
3. Cole na planilha do Google Sheets

## Código Atualizado
O código foi atualizado para:
- ✅ Não tentar acessar localhost (que não funciona)
- ✅ Buscar JSON do Google Drive automaticamente
- ✅ Usar dados de exemplo se JSON não for encontrado
- ✅ Ter timeout adequado para não travar
- ✅ Melhor tratamento de erros
