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
  {mercado: 'Mundial', tipo: 'Grãos e Cereais', url: 'https://www.supermercadosmundial.com.br/departamentos/categoria/ofertas?utm_source=chatgpt.com&page=1&productCategory=34'},
  {mercado: 'Mundial', tipo: 'Frios, Salames, Embutidos e Queijos', url: 'https://www.supermercadosmundial.com.br/departamentos/categoria/ofertas?utm_source=chatgpt.com&page=1&productCategory=13&productCategory=14'},
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
        
        // Extrair quantidade - melhorado para capturar unidades sozinhas também
        // Primeiro tenta padrão com número: "5Kg", "1kg", "500g", etc.
        let qtdMatch = nome.match(/(\d+(?:[,.]\d+)?)\s*(kg|Kg|KG|g|G|L|l|ml|mL|ML|un|Un|UN|pct|Pct|PCT|pac|Pac|PAC|und|Und|UND)/i);
        let quantidade = qtdMatch ? qtdMatch[0] : '';
        
        // Se não encontrou com número, tenta unidades sozinhas no final: "Kg", "kg", "KG"
        if (!qtdMatch) {
          // Procurar unidades sozinhas no final do nome (com ou sem espaço antes)
          const unidadesSozinhas = nome.match(/\s*(kg|Kg|KG|g|G|L|l|ml|mL|ML|un|Un|UN|pct|Pct|PCT|pac|Pac|PAC|und|Und|UND)\s*$/i);
          if (unidadesSozinhas) {
            quantidade = unidadesSozinhas[1]; // Pegar apenas a unidade
            qtdMatch = unidadesSozinhas; // Para usar na remoção depois
          }
        }
        
        // Se ainda não encontrou, usar 'un' como padrão
        if (!quantidade) {
          quantidade = 'un';
        }
        
        // Identificar marca (lista expandida com marcas comuns)
        const nomeLower = nome.toLowerCase();
        let marca = '';
        let marcaEncontrada = '';
        let marcaNomeFormatado = '';
        
        // Dicionário expandido de marcas conhecidas
        const marcas = {
          // Alimentos básicos
          'tio joao': 'Tio João', 't. joao': 'Tio João', 'tio joão': 'Tio João',
          'ouro nobre': 'Ouro Nobre', 'combrasil': 'Combrasil', 'rei do sul': 'Rei do Sul',
          'maximo': 'Máximo', 'carreteiro': 'Carreteiro', 'globo': 'Globo', 'copa': 'Copa',
          'kicaldo': 'Kicaldo', 'panela de barro': 'Panela de Barro', 'sanes': 'Sanes',
          'yoki': 'Yoki', 'italac': 'Italac', 'sadia': 'Sadia',
          // Carnes e frios
          'levida band': 'Levida Band', 'perdigão': 'Perdigão', 'vitória': 'Vitória',
          'juliana': 'Juliana', 'monteminas': 'Monteminas', 'wilson': 'Wilson',
          // Laticínios
          'claybom': 'Claybom', 'qualy': 'Qualy',
          // Limpeza
          'vitral': 'Vitral', 'big soft': 'Big Soft', 'downy': 'Downy', 'ypê': 'Ypê',
          'ype': 'Ypê', 'tixan': 'Tixan', 'tixan ype': 'Tixan Ypê', 'uau': 'Uau',
          'minuano': 'Minuano', 'urca': 'Urca', 'sbp': 'SBP', 'neutral': 'Neutral',
          'ruth coco': 'Ruth Coco', 'assolan': 'Assolan',
          // Bebidas
          'antarctica': 'Antarctica', 'bohemia': 'Bohemia', 'brahma': 'Brahma',
          'budweiser': 'Budweiser', 'corona': 'Corona', 'original': 'Original',
          'skol': 'Skol', 'spaten': 'Spaten', 'chandon': 'Chandon', 'beefeater': 'Beefeater',
          'tanqueray': 'Tanqueray', 'pepsi': 'Pepsi', 'tang': 'Tang', 'johnnie walker': 'Johnnie Walker',
          'guaravita': 'Guaravita', 'gatorade': 'Gatorade',
          // Conservas
          'gomes da costa': 'Gomes da Costa', 'gallo': 'Gallo', 'o-live': 'O-Live',
          'pramesa': 'Pramesa', 'hellmanns': 'Hellmanns', 'pomarola': 'Pomarola',
          'knorr': 'Knorr', 'kitano': 'Kitano', 'piracanjuba': 'Piracanjuba', 'moça': 'Moça',
          // Biscoitos
          'crac': 'Crac', 'piraquê': 'Piraquê',
          // Matinais
          'guarani': 'Guarani', 'união': 'União', 'quaker': 'Quaker', 'italakinho': 'Italakinho',
          '3 corações': '3 Corações', 'melitta': 'Melitta', 'patusco': 'Patusco',
          'glória': 'Glória', 'molico': 'Molico', 'ninho': 'Ninho', 'plus vita': 'Plus Vita',
          'seven boys': 'Seven Boys',
          // Bebês
          'babysec': 'Babysec', 'huggies': 'Huggies', 'personal baby': 'Personal Baby',
          'dove': 'Dove', 'dove baby': 'Dove Baby', 'hipoglos': 'Hipoglos', 'granado': 'Granado',
          'sed': 'Seda', 'sed juntinhos': 'Seda Juntinhos',
          // Outros
          'omo': 'Omo', 'coca cola': 'Coca-Cola', 'nestle': 'Nestlé', 'dona elza': 'Dona Elza'
        };
        
        // Buscar marca no dicionário (ordenar por tamanho para pegar marcas compostas primeiro)
        const marcasOrdenadas = Object.entries(marcas).sort((a, b) => b[0].length - a[0].length);
        for (const [marcaKey, marcaNome] of marcasOrdenadas) {
          if (nomeLower.includes(marcaKey)) {
            marca = marcaNome;
            marcaEncontrada = marcaKey;
            marcaNomeFormatado = marcaNome;
            break;
          }
        }
        
        // Se não encontrou no dicionário, tentar detectar marca no final do nome
        // (palavras em maiúsculas ou palavras que parecem marcas)
        if (!marca) {
          const palavras = nome.split(/\s+/);
          // Verificar últimas 1-3 palavras como possível marca
          for (let i = Math.min(3, palavras.length); i >= 1; i--) {
            const possivelMarca = palavras.slice(-i).join(' ');
            const possivelMarcaLower = possivelMarca.toLowerCase();
            
            // Se a palavra está toda em maiúsculas ou tem características de marca
            if (possivelMarca === possivelMarca.toUpperCase() && possivelMarca.length >= 2) {
              marca = possivelMarca;
              marcaEncontrada = possivelMarcaLower;
              marcaNomeFormatado = possivelMarca;
              break;
            }
            
            // Verificar se é uma palavra conhecida que pode ser marca
            if (possivelMarca.length >= 2 && possivelMarca.length <= 20) {
              // Remover quantidade se estiver na possível marca
              const semQtd = possivelMarca.replace(/(\d+(?:[,.]\d+)?)\s*(kg|g|L|l|ml|un|pct|pac|und)/i, '').trim();
              if (semQtd && semQtd.length >= 2) {
                marca = semQtd;
                marcaEncontrada = semQtd.toLowerCase();
                marcaNomeFormatado = semQtd;
                break;
              }
            }
          }
        }
        
        // Se ainda não encontrou, tentar detectar marca por padrões comuns
        if (!marca) {
          const palavras = nome.split(/\s+/);
          
          // Padrão comum: "Produto Marca Quantidade" ou "Produto Marca"
          // A marca geralmente está no final, antes da quantidade
          let indiceQtd = -1;
          if (qtdMatch) {
            for (let i = 0; i < palavras.length; i++) {
              if (palavras[i].toLowerCase().includes(qtdMatch[0].toLowerCase())) {
                indiceQtd = i;
                break;
              }
            }
          }
          
          // Se encontrou quantidade, a marca pode estar antes dela
          if (indiceQtd > 0) {
            // Pegar última palavra antes da quantidade como possível marca
            const possivelMarca = palavras[indiceQtd - 1];
            if (possivelMarca && possivelMarca.length >= 2 && possivelMarca.length <= 25) {
              marca = possivelMarca;
              marcaEncontrada = possivelMarca.toLowerCase();
              marcaNomeFormatado = possivelMarca;
            }
          }
          
          // Se ainda não encontrou, tentar últimas palavras (exceto quantidade)
          if (!marca) {
            for (let i = palavras.length - 1; i >= 0; i--) {
              const palavra = palavras[i];
              // Ignorar quantidade, palavras muito curtas e palavras comuns (incluindo todas variações de unidades)
              const palavrasComuns = ['cada', 'kg', 'Kg', 'KG', 'g', 'G', 'l', 'L', 'ml', 'mL', 'ML', 
                                      'un', 'Un', 'UN', 'pct', 'Pct', 'PCT', 'pac', 'Pac', 'PAC', 
                                      'und', 'Und', 'UND', 'itro', 'itros', 'Itro', 'Itros'];
              // Verificar se não é uma unidade ou quantidade
              const isUnidade = palavrasComuns.includes(palavra) || 
                                palavra.match(/^(\d+(?:[,.]\d+)?)\s*(kg|Kg|KG|g|G|L|l|ml|mL|ML|un|Un|UN|pct|Pct|PCT|pac|Pac|PAC|und|Und|UND)$/i);
              
              if (!isUnidade && palavra.length >= 2 && palavra.length <= 25) {
                marca = palavra;
                marcaEncontrada = palavra.toLowerCase();
                marcaNomeFormatado = palavra;
                break;
              }
            }
          }
        }
        
        // Se ainda não encontrou marca, usar "Genérico" como fallback
        if (!marca) {
          marca = 'Genérico';
          marcaNomeFormatado = 'Genérico';
        }
        
        // Limpar marca para remover unidades que possam ter sido capturadas
        if (marca !== 'Genérico' && marcaNomeFormatado !== 'Genérico') {
          // Remover unidades da marca (Kg, kg, KG, g, L, ml, etc.)
          marcaNomeFormatado = marcaNomeFormatado.replace(/\s*(kg|Kg|KG|g|G|L|l|ml|mL|ML|un|Un|UN|pct|Pct|PCT|pac|Pac|PAC|und|Und|UND)\s*$/i, '').trim();
          marcaEncontrada = marcaNomeFormatado.toLowerCase();
          marca = marcaNomeFormatado;
          
          // Se a marca ficou vazia após limpar, usar Genérico
          if (!marcaNomeFormatado || marcaNomeFormatado.length < 2) {
            marca = 'Genérico';
            marcaNomeFormatado = 'Genérico';
            marcaEncontrada = 'genérico';
          }
        }
        
        // Remover marca e quantidade do nome para obter apenas o produto
        let nomeLimpo = nome;
        
        // Remover quantidade primeiro (para não interferir na remoção da marca)
        if (qtdMatch && qtdMatch[0]) {
          // Remover a quantidade encontrada (pode ser "5Kg" ou só "Kg")
          nomeLimpo = nomeLimpo.replace(qtdMatch[0], '').trim();
        }
        
        // Remover unidades sozinhas que possam ter sobrado (Kg, kg, KG, etc.)
        nomeLimpo = nomeLimpo.replace(/\s+(kg|Kg|KG|g|G|L|l|ml|mL|ML|un|Un|UN|pct|Pct|PCT|pac|Pac|PAC|und|Und|UND)\s*$/i, '').trim();
        nomeLimpo = nomeLimpo.replace(/\s+(kg|Kg|KG|g|G|L|l|ml|mL|ML|un|Un|UN|pct|Pct|PCT|pac|Pac|PAC|und|Und|UND)\s+/gi, ' ').trim();
        
        // Remover marca do nome (usar regex para remover a marca encontrada)
        if (marcaEncontrada && marca !== 'Genérico' && marcaNomeFormatado !== 'Genérico') {
          // Tentar remover a marca formatada primeiro (preserva maiúsculas)
          if (marcaNomeFormatado) {
            const regexMarcaFormatada = new RegExp('\\b' + marcaNomeFormatado.replace(/[.*+?^${}()|[\]\\]/g, '\\$&') + '\\b', 'g');
            nomeLimpo = nomeLimpo.replace(regexMarcaFormatada, '').trim();
          }
          
          // Se ainda contém a marca (case insensitive), remover
          if (nomeLimpo.toLowerCase().includes(marcaEncontrada)) {
            const regexMarca = new RegExp('\\b' + marcaEncontrada.replace(/[.*+?^${}()|[\]\\]/g, '\\$&') + '\\b', 'gi');
            nomeLimpo = nomeLimpo.replace(regexMarca, '').trim();
          }
        }
        
        // Limpar espaços extras e palavras comuns que sobraram (incluindo todas variações de unidades)
        nomeLimpo = nomeLimpo.replace(/\s+cada\s*/gi, ' ')
                              .replace(/\s+itro\s*/gi, ' ')
                              .replace(/\s+itros\s*/gi, ' ')
                              .replace(/\s+(kg|Kg|KG)\s*/gi, ' ')
                              .replace(/\s+(g|G)\s*/gi, ' ')
                              .replace(/\s+(L|l)\s*/gi, ' ')
                              .replace(/\s+(ml|mL|ML)\s*/gi, ' ')
                              .replace(/\s+/g, ' ')
                              .trim();
        
        // Se o nome ficou muito curto ou vazio após remover marca, usar nome original sem quantidade
        if (!nomeLimpo || nomeLimpo.length < 3) {
          nomeLimpo = nome;
          if (qtdMatch && qtdMatch[0]) {
            nomeLimpo = nomeLimpo.replace(qtdMatch[0], '').trim();
          }
          // Remover unidades sozinhas
          nomeLimpo = nomeLimpo.replace(/\s+(kg|Kg|KG|g|G|L|l|ml|mL|ML|un|Un|UN|pct|Pct|PCT|pac|Pac|PAC|und|Und|UND)\s*$/i, '').trim();
          nomeLimpo = nomeLimpo.replace(/\s+(kg|Kg|KG|g|G|L|l|ml|mL|ML|un|Un|UN|pct|Pct|PCT|pac|Pac|PAC|und|Und|UND)\s+/gi, ' ').trim();
          nomeLimpo = nomeLimpo.replace(/\s+cada\s*/gi, ' ')
                                .replace(/\s+itro\s*/gi, ' ')
                                .replace(/\s+itros\s*/gi, ' ')
                                .replace(/\s+(kg|Kg|KG)\s*/gi, ' ')
                                .replace(/\s+(g|G)\s*/gi, ' ')
                                .replace(/\s+(L|l)\s*/gi, ' ')
                                .replace(/\s+(ml|mL|ML)\s*/gi, ' ')
                                .replace(/\s+/g, ' ')
                                .trim();
        }
        
        // Identificar produto base e segmento (usar categoria como segmento padrão)
        let produto = nomeLimpo;
        let segmento = categoriaNome;
        
        // Tentar identificar produto genérico apenas para alguns casos conhecidos
        const nomeLimpoLower = nomeLimpo.toLowerCase();
        if (nomeLimpoLower.includes('arroz')) {
          produto = 'Arroz Branco';
        } else if (nomeLimpoLower.includes('feijao') || nomeLimpoLower.includes('feijão')) {
          produto = 'Feijão Preto';
        } else if (nomeLimpoLower.includes('farinha')) {
          produto = 'Farinha de Trigo';
        } else if (nomeLimpoLower.includes('pipoca')) {
          produto = 'Pipoca Microondas';
        }
        
        // Se não identificou produto genérico, usar o nome limpo (sem marca e quantidade)
        if (produto === nomeLimpo && nomeLimpo.length > 50) {
          // Se o nome for muito longo, pegar primeiras palavras
          const palavras = nomeLimpo.split(' ');
          produto = palavras.slice(0, 5).join(' ');
        }
        
        // Criar chave única para evitar duplicatas
        const chave = (nome.toLowerCase() + '_' + preco + '_' + quantidade).replace(/\s+/g, '_');
        
        if (!produtosEncontrados.has(chave)) {
          produtosEncontrados.set(chave, {
            Segmento: segmento,
            Produto: produto,
            Marca: marcaNomeFormatado || marca || 'Genérico',
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
