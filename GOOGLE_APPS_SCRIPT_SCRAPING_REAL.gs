/**
 * Script Google Apps Script para fazer SCRAPING REAL dos produtos de múltiplos supermercados
 * Acessa as URLs das categorias e encartes e extrai TODOS os produtos
 */

// ✅ CONFIGURAÇÃO DA PLANILHA
const PLANILHA_PRODUTOS_ID = '1gWYvYjPrTNAvEXkeYTh5SjnyWMir371D_5vTmacWAO8';
const NOME_ABA = 'Página1';

// ✅ URLs DAS CATEGORIAS DO GUANABARA (TODAS AS CATEGORIAS)
const CATEGORIAS_GUANABARA = [
  {nome: 'Açougue', url: 'https://www.supermercadosguanabara.com.br/produtos/42'},
  {nome: 'Frios e Laticínios', url: 'https://www.supermercadosguanabara.com.br/produtos/62'},
  {nome: 'Limpeza', url: 'https://www.supermercadosguanabara.com.br/produtos/102'},
  {nome: 'Bebida', url: 'https://www.supermercadosguanabara.com.br/produtos/82'},
  {nome: 'Biscoito', url: 'https://www.supermercadosguanabara.com.br/produtos/32'},
  {nome: 'Massas', url: 'https://www.supermercadosguanabara.com.br/produtos/22'},
  {nome: 'Conservas', url: 'https://www.supermercadosguanabara.com.br/produtos/92'},
  {nome: 'Cantinho do Bebê', url: 'https://www.supermercadosguanabara.com.br/produtos/203'},
  {nome: 'Embutidos', url: 'https://www.supermercadosguanabara.com.br/produtos/52'},
  {nome: 'Matinais e Padaria', url: 'https://www.supermercadosguanabara.com.br/produtos/12'},
  {nome: 'Salgados', url: 'https://www.supermercadosguanabara.com.br/produtos/72'},
  {nome: 'Cereais e Farináceos', url: 'https://www.supermercadosguanabara.com.br/produtos'},
  {nome: 'Bombom', url: 'https://www.supermercadosguanabara.com.br/produtos/152'}
];

// ✅ FONTES DE ENCARTES E OFERTAS DE TODOS OS SUPERMERCADOS
const FONTES_ENCARTES_OFERTAS = [
  {mercado: 'Guanabara', tipo: 'Encarte', url: 'https://www.supermercadosguanabara.com.br/encarte'},
  {mercado: 'Mundial', tipo: 'Ofertas', url: 'https://www.supermercadosmundial.com.br/ofertas'},
  {mercado: 'Mundial', tipo: 'Ofertas', url: 'https://www.supermercadosmundial.com.br/departamentos/categoria/ofertas?utm_source=chatgpt.com&page=1'},
  {mercado: 'Supermarket', tipo: 'Ofertas', url: 'https://redesupermarket.com.br/ofertas/'},
  {mercado: 'Prezunic', tipo: 'Ofertas', url: 'https://www.prezunic.com.br/ofertas'},
  {mercado: 'Prezunic', tipo: 'Encarte', url: 'https://blog.prezunic.com.br/encarte/'}
];

// ✅ FUNÇÃO PRINCIPAL PARA FAZER SCRAPING E SALVAR
function fazerScrapingESalvar() {
  try {
    console.log('Iniciando scraping de todas as categorias e encartes...');
    
    // Abrir planilha
    const planilha = SpreadsheetApp.openById(PLANILHA_PRODUTOS_ID);
    console.log('Planilha aberta:', planilha.getName());
    
    // Obter ou criar aba
    let aba = planilha.getSheetByName(NOME_ABA);
    if (!aba) {
      aba = planilha.insertSheet(NOME_ABA);
    }
    
    // Criar cabeçalhos
    const colunas = ['Segmento', 'Produto', 'Marca', 'Qtd', 'Menor Preço', 'Mercado', 'Link'];
    aba.getRange(1, 1, 1, colunas.length).setValues([colunas]);
    
    // ✅ FAZER SCRAPING DE TODAS AS CATEGORIAS DO GUANABARA
    let todosProdutos = [];
    
    console.log('=== PROCESSANDO CATEGORIAS DO GUANABARA ===');
    for (let i = 0; i < CATEGORIAS_GUANABARA.length; i++) {
      const categoria = CATEGORIAS_GUANABARA[i];
      console.log('Processando categoria ' + (i + 1) + '/' + CATEGORIAS_GUANABARA.length + ': ' + categoria.nome);
      
      try {
        const produtos = extrairProdutosDaCategoria(categoria.url, categoria.nome, 'Guanabara');
        console.log('  Encontrados ' + produtos.length + ' produtos em ' + categoria.nome);
        todosProdutos = todosProdutos.concat(produtos);
        
        // Pequena pausa entre requisições para não sobrecarregar
        Utilities.sleep(1000);
      } catch (e) {
        console.log('  Erro ao processar ' + categoria.nome + ':', e.message);
      }
    }
    
    // ✅ FAZER SCRAPING DOS ENCARTES E OFERTAS DE TODOS OS SUPERMERCADOS
    console.log('=== PROCESSANDO ENCARTES E OFERTAS ===');
    for (let i = 0; i < FONTES_ENCARTES_OFERTAS.length; i++) {
      const fonte = FONTES_ENCARTES_OFERTAS[i];
      console.log('Processando ' + fonte.mercado + ' - ' + fonte.tipo + ' (' + (i + 1) + '/' + FONTES_ENCARTES_OFERTAS.length + ')');
      
      try {
        const produtos = extrairProdutosDaCategoria(fonte.url, fonte.tipo, fonte.mercado);
        console.log('  Encontrados ' + produtos.length + ' produtos em ' + fonte.mercado + ' - ' + fonte.tipo);
        todosProdutos = todosProdutos.concat(produtos);
        
        // Pequena pausa entre requisições para não sobrecarregar
        Utilities.sleep(1000);
      } catch (e) {
        console.log('  Erro ao processar ' + fonte.mercado + ' - ' + fonte.tipo + ':', e.message);
      }
    }
    
    console.log('Total de produtos encontrados: ' + todosProdutos.length);
    
    // ✅ SALVAR NA PLANILHA
    if (todosProdutos.length > 0) {
      escreverDadosNaPlanilha(aba, todosProdutos, colunas);
      console.log('Scraping concluido! ' + todosProdutos.length + ' produtos salvos.');
    } else {
      console.log('Nenhum produto encontrado. Verifique os logs acima.');
    }
    
  } catch (error) {
    console.log('Erro geral:', error.message);
    console.log('Stack:', error.stack);
  }
}

// ✅ FUNÇÃO PARA EXTRAIR PRODUTOS DE UMA CATEGORIA
function extrairProdutosDaCategoria(url, categoriaNome, mercadoNome) {
  const produtos = [];
  
  try {
    // Fazer requisição HTTP
    const response = UrlFetchApp.fetch(url, {
      muteHttpExceptions: true,
      headers: {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
      }
    });
    
    if (response.getResponseCode() !== 200) {
      console.log('  HTTP ' + response.getResponseCode() + ' para ' + mercadoNome + ' - ' + categoriaNome);
      return produtos;
    }
    
    const html = response.getContentText();
    
    if (!html || html.length < 100) {
      console.log('  HTML muito curto para ' + mercadoNome + ' - ' + categoriaNome);
      return produtos;
    }
    
    // ✅ EXTRAIR PRODUTOS DO HTML
    // Padrão Guanabara: "13,95 Arroz Branco Ouro Nobre 5Kg"
    // Buscar padrão: número seguido de vírgula/ponto e 2 dígitos, seguido de texto
    
    // Estratégia 1: Buscar no texto limpo (sem tags HTML)
    const textoLimpo = html.replace(/<script[^>]*>[\s\S]*?<\/script>/gi, ' ')
                           .replace(/<style[^>]*>[\s\S]*?<\/style>/gi, ' ')
                           .replace(/<[^>]+>/g, ' ')
                           .replace(/&nbsp;/g, ' ')
                           .replace(/&amp;/g, '&')
                           .replace(/&lt;/g, '<')
                           .replace(/&gt;/g, '>')
                           .replace(/&quot;/g, '"')
                           .replace(/\s+/g, ' ')
                           .trim();
    
    // Padrão melhorado: número seguido de vírgula/ponto e 2 dígitos, seguido de texto (nome do produto)
    // Aceita mais variações e é mais flexível para capturar todos os produtos
    const padrao = /(\d+[,.]\d{2})\s+([A-Za-zÁÉÍÓÚÂÊÔÃÕÇáéíóúâêôãõç0-9][A-Za-zÁÉÍÓÚÂÊÔÃÕÇáéíóúâêôãõç0-9\s\.\-]{3,100}?)(?=\s*\d+[,.]\d{2}|\s*cada|\s*Validade|$)/gi;
    
    let match;
    const produtosEncontrados = new Map();
    
    while ((match = padrao.exec(textoLimpo)) !== null) {
      try {
        const precoStr = match[1].replace(',', '.');
        const preco = parseFloat(precoStr);
        
        if (preco < 0.01 || preco > 10000) continue;
        
        let nome = match[2].trim();
        nome = nome.replace(/\s+/g, ' ').trim();
        
        // Remover "cada" do final
        nome = nome.replace(/\s+cada\s*$/i, '').trim();
        
        if (!nome || nome.length < 3 || nome.length > 200) continue;
        
        // Validar nome (não pode ser só números)
        if (/^[0-9,.\s]+$/.test(nome)) continue;
        
        // Extrair quantidade
        const qtdMatch = nome.match(/(\d+(?:[,.]\d+)?)\s*(kg|g|L|l|ml|un|pct|pac|und)/i);
        const quantidade = qtdMatch ? qtdMatch[0] : 'un';
        
        // Identificar marca (lista expandida)
        const nomeLower = nome.toLowerCase();
        let marca = 'Genérico';
        
        const marcas = {
          'tio joao': 'Tio João', 't. joao': 'Tio João', 'ouro nobre': 'Ouro Nobre',
          'combrasil': 'Combrasil', 'rei do sul': 'Rei do Sul', 'maximo': 'Máximo',
          'carreteiro': 'Carreteiro', 'globo': 'Globo', 'copa': 'Copa',
          'kicaldo': 'Kicaldo', 'panela de barro': 'Panela de Barro',
          'sanes': 'Sanes', 'yoki': 'Yoki', 'italac': 'Italac', 'omo': 'Omo',
          'sadia': 'Sadia', 'coca cola': 'Coca-Cola', 'nestle': 'Nestlé',
          'dona elza': 'Dona Elza', 'tio joão': 'Tio João'
        };
        
        for (const [marcaKey, marcaNome] of Object.entries(marcas)) {
          if (nomeLower.includes(marcaKey)) {
            marca = marcaNome;
            break;
          }
        }
        
        // Identificar produto base e segmento (usar categoria como segmento padrão)
        let produto = nome;
        let segmento = categoriaNome;
        
        // Tentar identificar produto genérico apenas para alguns casos conhecidos
        if (nomeLower.includes('arroz')) {
          produto = 'Arroz Branco';
        } else if (nomeLower.includes('feijao') || nomeLower.includes('feijão')) {
          produto = 'Feijão Preto';
        } else if (nomeLower.includes('farinha')) {
          produto = 'Farinha de Trigo';
        } else if (nomeLower.includes('pipoca')) {
          produto = 'Pipoca Microondas';
        }
        
        // Se não identificou, usar o nome completo como produto
        if (produto === nome && nome.length > 50) {
          // Se o nome for muito longo, pegar primeiras palavras
          const palavras = nome.split(' ');
          produto = palavras.slice(0, 5).join(' ');
        }
        
        // Criar chave única para evitar duplicatas
        const chave = (nome.toLowerCase() + '_' + preco + '_' + quantidade).replace(/\s+/g, '_');
        
        if (!produtosEncontrados.has(chave)) {
          produtosEncontrados.set(chave, {
            Segmento: segmento,
            Produto: produto,
            Marca: marca,
            Qtd: quantidade,
            'Menor Preço': 'R$ ' + preco.toFixed(2).replace('.', ','),
            Mercado: mercadoNome || 'Guanabara',
            Link: url
          });
        }
      } catch (e) {
        // Continuar mesmo se houver erro em um produto
        continue;
      }
    }
    
    // Converter Map para Array
    return Array.from(produtosEncontrados.values());
    
  } catch (error) {
    console.log('  Erro ao extrair produtos de ' + mercadoNome + ' - ' + categoriaNome + ':', error.message);
    return produtos;
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
        item.Segmento || '',
        item.Produto || '',
        item.Marca || '',
        item.Qtd || '',
        item['Menor Preço'] || '',
        item.Mercado || '',
        item.Link || ''
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

// ✅ FUNÇÃO ALTERNATIVA: Usar dados de exemplo se scraping falhar
function salvarProdutosNoGoogleSheets() {
  // Esta função mantém compatibilidade com o código anterior
  // Mas agora chama o scraping real
  fazerScrapingESalvar();
}
