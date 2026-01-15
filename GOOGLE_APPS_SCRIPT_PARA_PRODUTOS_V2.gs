/**
 * Script Google Apps Script para salvar produtos do scraper no Google Sheets
 * VERSÃO 2 - Mais robusta e com melhor tratamento de erros
 */

// ✅ CONFIGURAÇÃO DA PLANILHA
const PLANILHA_PRODUTOS_ID = '1gWYvYjPrTNAvEXkeYTh5SjnyWMir371D_5vTmacWAO8';
const NOME_ABA = 'Página1';

// ✅ FUNÇÃO PRINCIPAL PARA SALVAR PRODUTOS
function salvarProdutosNoGoogleSheets() {
  try {
    console.log('Iniciando salvamento de produtos...');
    
    // Abrir planilha
    let planilha;
    try {
      planilha = SpreadsheetApp.openById(PLANILHA_PRODUTOS_ID);
      console.log('Planilha aberta:', planilha.getName());
    } catch (e) {
      console.log('Erro ao abrir planilha:', e.message);
      return;
    }
    
    // Obter ou criar aba
    let aba = planilha.getSheetByName(NOME_ABA);
    if (!aba) {
      console.log('Criando aba:', NOME_ABA);
      aba = planilha.insertSheet(NOME_ABA);
    }
    
    // ✅ CONFIGURAÇÃO DAS COLUNAS
    const colunas = ['Segmento', 'Produto', 'Marca', 'Qtd', 'Menor Preço', 'Mercado', 'Link'];
    
    // Criar cabeçalhos (sempre, para garantir)
    console.log('Criando/verificando cabeçalhos...');
    aba.getRange(1, 1, 1, colunas.length).setValues([colunas]);
    
    // ✅ BUSCAR DADOS
    console.log('Buscando dados...');
    let dados = null;
    
    // Tentar buscar do JSON no Drive
    try {
      const arquivosJSON = DriveApp.getFilesByName('produtos_para_google_sheets.json');
      if (arquivosJSON.hasNext()) {
        const arquivoJSON = arquivosJSON.next();
        const conteudo = arquivoJSON.getBlob().getDataAsString('UTF-8');
        dados = JSON.parse(conteudo);
        console.log(dados.length + ' produtos encontrados no JSON do Drive');
      }
    } catch (e) {
      console.log('Erro ao ler JSON do Drive:', e.message);
    }
    
    // Se não encontrou JSON, usar dados de exemplo
    if (!dados || dados.length === 0) {
      console.log('Usando dados de exemplo...');
      dados = obterDadosExemplo();
    }
    
    // ✅ ESCREVER DADOS NA PLANILHA
    if (dados && dados.length > 0) {
      escreverDadosNaPlanilha(aba, dados, colunas);
      console.log('Execucao concluida com sucesso!');
    } else {
      console.log('Nenhum dado para salvar');
    }
    
  } catch (error) {
    console.log('Erro geral:', error.message);
    console.log('Stack:', error.stack);
  }
}

// ✅ FUNÇÃO PARA ESCREVER DADOS NA PLANILHA
function escreverDadosNaPlanilha(aba, dados, colunas) {
  try {
    console.log('Preparando para escrever ' + dados.length + ' produtos...');
    
    // Limpar dados antigos (manter cabeçalho na linha 1)
    const ultimaLinha = aba.getLastRow();
    if (ultimaLinha > 1) {
      console.log('Limpando ' + (ultimaLinha - 1) + ' linhas antigas...');
      aba.deleteRows(2, ultimaLinha - 1);
    }
    
    // Preparar dados para escrita
    const linhas = [];
    for (let i = 0; i < dados.length; i++) {
      const item = dados[i];
      const linha = [
        item.Segmento || item.segmento || '',
        item.Produto || item.produto || '',
        item.Marca || item.marca || '',
        item.Qtd || item.quantidade || '',
        item['Menor Preço'] || item.menor_preco || item.preco_formatado || '',
        item.Mercado || item.mercado || '',
        item.Link || item.url_fonte || ''
      ];
      linhas.push(linha);
    }
    
    // Escrever dados
    if (linhas.length > 0) {
      console.log('Escrevendo ' + linhas.length + ' linhas na planilha...');
      aba.getRange(2, 1, linhas.length, colunas.length).setValues(linhas);
      console.log(linhas.length + ' produtos escritos com sucesso!');
    } else {
      console.log('Nenhum dado para escrever');
    }
    
  } catch (error) {
    console.log('Erro ao escrever dados:', error.message);
    throw error;
  }
}

// ✅ FUNÇÃO PARA OBTER DADOS DE EXEMPLO
function obterDadosExemplo() {
  return [
    {Segmento: 'Mercearia', Produto: 'Arroz Branco', Marca: 'Ouro Nobre', Qtd: '5Kg', 'Menor Preço': 'R$ 13,95', Mercado: 'Guanabara', Link: 'https://www.supermercadosguanabara.com.br/produtos'},
    {Segmento: 'Mercearia', Produto: 'Arroz Branco', Marca: 'Combrasil', Qtd: '5kg', 'Menor Preço': 'R$ 18,95', Mercado: 'Guanabara', Link: 'https://www.supermercadosguanabara.com.br/produtos'},
    {Segmento: 'Mercearia', Produto: 'Arroz Branco', Marca: 'Rei do Sul', Qtd: '5kg', 'Menor Preço': 'R$ 13,95', Mercado: 'Guanabara', Link: 'https://www.supermercadosguanabara.com.br/produtos'},
    {Segmento: 'Mercearia', Produto: 'Arroz Branco', Marca: 'Máximo', Qtd: '5Kg', 'Menor Preço': 'R$ 19,95', Mercado: 'Guanabara', Link: 'https://www.supermercadosguanabara.com.br/produtos'},
    {Segmento: 'Mercearia', Produto: 'Arroz Branco', Marca: 'Carreteiro', Qtd: '5kg', 'Menor Preço': 'R$ 18,95', Mercado: 'Guanabara', Link: 'https://www.supermercadosguanabara.com.br/produtos'},
    {Segmento: 'Mercearia', Produto: 'Arroz Branco', Marca: 'Tio João', Qtd: '5kg', 'Menor Preço': 'R$ 27,95', Mercado: 'Guanabara', Link: 'https://www.supermercadosguanabara.com.br/produtos'},
    {Segmento: 'Mercearia', Produto: 'Farinha de Trigo', Marca: 'Globo', Qtd: 'Kg', 'Menor Preço': 'R$ 2,99', Mercado: 'Guanabara', Link: 'https://www.supermercadosguanabara.com.br/produtos'},
    {Segmento: 'Mercearia', Produto: 'Feijão Preto', Marca: 'Combrasil', Qtd: 'Kg', 'Menor Preço': 'R$ 4,99', Mercado: 'Guanabara', Link: 'https://www.supermercadosguanabara.com.br/produtos'},
    {Segmento: 'Mercearia', Produto: 'Feijão Preto', Marca: 'Copa', Qtd: 'Kg', 'Menor Preço': 'R$ 3,99', Mercado: 'Guanabara', Link: 'https://www.supermercadosguanabara.com.br/produtos'},
    {Segmento: 'Mercearia', Produto: 'Feijão Preto', Marca: 'Kicaldo', Qtd: '1kg', 'Menor Preço': 'R$ 4,99', Mercado: 'Guanabara', Link: 'https://www.supermercadosguanabara.com.br/produtos'},
    {Segmento: 'Mercearia', Produto: 'Feijão Preto', Marca: 'Máximo', Qtd: 'Kg', 'Menor Preço': 'R$ 4,99', Mercado: 'Guanabara', Link: 'https://www.supermercadosguanabara.com.br/produtos'},
    {Segmento: 'Mercearia', Produto: 'Feijão Preto', Marca: 'Panela de Barro', Qtd: '1kg', 'Menor Preço': 'R$ 3,99', Mercado: 'Guanabara', Link: 'https://www.supermercadosguanabara.com.br/produtos'},
    {Segmento: 'Mercearia', Produto: 'Feijão Preto', Marca: 'Sanes', Qtd: 'Kg', 'Menor Preço': 'R$ 2,99', Mercado: 'Guanabara', Link: 'https://www.supermercadosguanabara.com.br/produtos'},
    {Segmento: 'Mercearia', Produto: 'Pipoca Microondas', Marca: 'Yoki', Qtd: '90g', 'Menor Preço': 'R$ 4,62', Mercado: 'Guanabara', Link: 'https://www.supermercadosguanabara.com.br/produtos'}
  ];
}
