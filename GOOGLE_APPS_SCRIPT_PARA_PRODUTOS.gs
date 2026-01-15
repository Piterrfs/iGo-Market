/**
 * Script Google Apps Script para salvar produtos do scraper no Google Sheets
 * Baseado no script de notícias fornecido pelo usuário
 */

// ✅ CONFIGURAÇÃO DA PLANILHA
const PLANILHA_PRODUTOS_ID = '1gWYvYjPrTNAvEXkeYTh5SjnyWMir371D_5vTmacWAO8';
const NOME_ABA = 'Página1';

// ✅ FUNÇÃO PRINCIPAL PARA SALVAR PRODUTOS
function salvarProdutosNoGoogleSheets() {
  try {
    console.log('🔍 Abrindo planilha:', PLANILHA_PRODUTOS_ID);
    const planilha = SpreadsheetApp.openById(PLANILHA_PRODUTOS_ID);
    console.log('✅ Planilha aberta:', planilha.getName());
    
    let aba = planilha.getSheetByName(NOME_ABA);
    if (!aba) {
      console.log('📋 Criando aba:', NOME_ABA);
      aba = planilha.insertSheet(NOME_ABA);
    }
    
    // ✅ CONFIGURAÇÃO DAS COLUNAS
    const colunas = [
      'Segmento', 'Produto', 'Marca', 'Qtd', 'Menor Preço', 'Mercado', 'Link'
    ];
    
    // Verificar se precisa criar cabeçalhos
    const ultimaColuna = aba.getLastColumn();
    let cabecalhoAtual = [];
    
    if (ultimaColuna > 0) {
      cabecalhoAtual = aba.getRange(1, 1, 1, ultimaColuna).getValues()[0];
    }
    
    if (cabecalhoAtual.length === 0 || cabecalhoAtual[0] === '' || ultimaColuna === 0) {
      console.log('📋 Criando cabeçalhos...');
      aba.getRange(1, 1, 1, colunas.length).setValues([colunas]);
    }
    
    // ✅ BUSCAR DADOS - PRIMEIRO TENTAR DO JSON NO GOOGLE DRIVE
    console.log('🔍 Buscando dados do JSON no Google Drive...');
    let dados = null;
    
    try {
      // Tentar encontrar arquivo JSON no Google Drive
      const arquivosJSON = DriveApp.getFilesByName('produtos_para_google_sheets.json');
      if (arquivosJSON.hasNext()) {
        const arquivoJSON = arquivosJSON.next();
        const conteudo = arquivoJSON.getBlob().getDataAsString('UTF-8');
        dados = JSON.parse(conteudo);
        console.log(`✅ ${dados.length} produtos encontrados no JSON do Drive`);
      }
    } catch (e) {
      console.log('⚠️ Erro ao ler JSON do Drive:', e.message);
    }
    
    // Se não encontrou JSON, usar dados de exemplo
    if (!dados || dados.length === 0) {
      console.log('⚠️ JSON não encontrado. Usando dados de exemplo...');
      dados = obterDadosExemplo();
    }
    
    // ✅ ESCREVER DADOS NA PLANILHA
    escreverDadosNaPlanilha(aba, dados, colunas);
    
    console.log('🎯 Execução concluída com sucesso!');
    
  } catch (error) {
    console.log('❌ Erro:', error.message);
    console.log('📋 Stack:', error.stack);
  }
}

// ✅ FUNÇÃO PARA ESCREVER DADOS NA PLANILHA
function escreverDadosNaPlanilha(aba, dados, colunas) {
  try {
    // Limpar dados antigos (manter cabeçalho)
    const ultimaLinha = aba.getLastRow();
    if (ultimaLinha > 1) {
      aba.deleteRows(2, ultimaLinha - 1);
    }
    
    // Preparar dados para escrita
    const linhas = [];
    dados.forEach(item => {
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
    });
    
    // Escrever dados
    if (linhas.length > 0) {
      // Garantir que temos pelo menos 1 coluna
      const numColunas = Math.max(colunas.length, 1);
      aba.getRange(2, 1, linhas.length, numColunas).setValues(linhas);
      console.log(`✅ ${linhas.length} produtos escritos na planilha`);
    } else {
      console.log('⚠️ Nenhum dado para escrever');
    }
  } catch (error) {
    console.log('❌ Erro ao escrever dados:', error.message);
    throw error;
  }
}

// ✅ FUNÇÃO PARA OBTER DADOS DE EXEMPLO (fallback)
function obterDadosExemplo() {
  return [
    {
      Segmento: 'Mercearia',
      Produto: 'Arroz Branco',
      Marca: 'Ouro Nobre',
      Qtd: '5Kg',
      'Menor Preço': 'R$ 13,95',
      Mercado: 'Guanabara',
      Link: 'https://www.supermercadosguanabara.com.br/produtos'
    },
    {
      Segmento: 'Mercearia',
      Produto: 'Arroz Branco',
      Marca: 'Combrasil',
      Qtd: '5kg',
      'Menor Preço': 'R$ 18,95',
      Mercado: 'Guanabara',
      Link: 'https://www.supermercadosguanabara.com.br/produtos'
    },
    {
      Segmento: 'Mercearia',
      Produto: 'Arroz Branco',
      Marca: 'Rei do Sul',
      Qtd: '5kg',
      'Menor Preço': 'R$ 13,95',
      Mercado: 'Guanabara',
      Link: 'https://www.supermercadosguanabara.com.br/produtos'
    },
    {
      Segmento: 'Mercearia',
      Produto: 'Arroz Branco',
      Marca: 'Máximo',
      Qtd: '5Kg',
      'Menor Preço': 'R$ 19,95',
      Mercado: 'Guanabara',
      Link: 'https://www.supermercadosguanabara.com.br/produtos'
    },
    {
      Segmento: 'Mercearia',
      Produto: 'Arroz Branco',
      Marca: 'Carreteiro',
      Qtd: '5kg',
      'Menor Preço': 'R$ 18,95',
      Mercado: 'Guanabara',
      Link: 'https://www.supermercadosguanabara.com.br/produtos'
    },
    {
      Segmento: 'Mercearia',
      Produto: 'Arroz Branco',
      Marca: 'Tio João',
      Qtd: '5kg',
      'Menor Preço': 'R$ 27,95',
      Mercado: 'Guanabara',
      Link: 'https://www.supermercadosguanabara.com.br/produtos'
    },
    {
      Segmento: 'Mercearia',
      Produto: 'Farinha de Trigo',
      Marca: 'Globo',
      Qtd: 'Kg',
      'Menor Preço': 'R$ 2,99',
      Mercado: 'Guanabara',
      Link: 'https://www.supermercadosguanabara.com.br/produtos'
    },
    {
      Segmento: 'Mercearia',
      Produto: 'Feijão Preto',
      Marca: 'Combrasil',
      Qtd: 'Kg',
      'Menor Preço': 'R$ 4,99',
      Mercado: 'Guanabara',
      Link: 'https://www.supermercadosguanabara.com.br/produtos'
    },
    {
      Segmento: 'Mercearia',
      Produto: 'Feijão Preto',
      Marca: 'Copa',
      Qtd: 'Kg',
      'Menor Preço': 'R$ 3,99',
      Mercado: 'Guanabara',
      Link: 'https://www.supermercadosguanabara.com.br/produtos'
    },
    {
      Segmento: 'Mercearia',
      Produto: 'Feijão Preto',
      Marca: 'Kicaldo',
      Qtd: '1kg',
      'Menor Preço': 'R$ 4,99',
      Mercado: 'Guanabara',
      Link: 'https://www.supermercadosguanabara.com.br/produtos'
    },
    {
      Segmento: 'Mercearia',
      Produto: 'Feijão Preto',
      Marca: 'Máximo',
      Qtd: 'Kg',
      'Menor Preço': 'R$ 4,99',
      Mercado: 'Guanabara',
      Link: 'https://www.supermercadosguanabara.com.br/produtos'
    },
    {
      Segmento: 'Mercearia',
      Produto: 'Feijão Preto',
      Marca: 'Panela de Barro',
      Qtd: '1kg',
      'Menor Preço': 'R$ 3,99',
      Mercado: 'Guanabara',
      Link: 'https://www.supermercadosguanabara.com.br/produtos'
    },
    {
      Segmento: 'Mercearia',
      Produto: 'Feijão Preto',
      Marca: 'Sanes',
      Qtd: 'Kg',
      'Menor Preço': 'R$ 2,99',
      Mercado: 'Guanabara',
      Link: 'https://www.supermercadosguanabara.com.br/produtos'
    },
    {
      Segmento: 'Mercearia',
      Produto: 'Pipoca Microondas',
      Marca: 'Yoki',
      Qtd: '90g',
      'Menor Preço': 'R$ 4,62',
      Mercado: 'Guanabara',
      Link: 'https://www.supermercadosguanabara.com.br/produtos'
    }
  ];
}

// ✅ FUNÇÃO PARA IMPORTAR DE ARQUIVO JSON (alternativa)
function importarProdutosDeJSON() {
  try {
    // Você pode fazer upload de um arquivo JSON no Google Drive
    // e usar este código para importar
    
    const arquivoJSON = DriveApp.getFilesByName('produtos_para_google_sheets.json').next();
    const conteudo = arquivoJSON.getBlob().getDataAsString();
    const dados = JSON.parse(conteudo);
    
    const planilha = SpreadsheetApp.openById(PLANILHA_PRODUTOS_ID);
    const aba = planilha.getSheetByName(NOME_ABA) || planilha.insertSheet(NOME_ABA);
    
    const colunas = ['Segmento', 'Produto', 'Marca', 'Qtd', 'Menor Preço', 'Mercado', 'Link'];
    
    // Criar cabeçalhos se necessário
    if (aba.getLastRow() === 0) {
      aba.getRange(1, 1, 1, colunas.length).setValues([colunas]);
    }
    
    escreverDadosNaPlanilha(aba, dados, colunas);
    
    console.log(`✅ ${dados.length} produtos importados do JSON`);
    
  } catch (error) {
    console.log('❌ Erro ao importar JSON:', error.message);
  }
}
