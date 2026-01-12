# OCR Avançado - Suporte a Diferentes Formatos e Posições

## Limitações do Sistema Atual

O sistema atual (`ocr_processor.py`) tem algumas limitações:

1. **Processa linha por linha** - Assume que cada produto está em uma linha
2. **Posições fixas** - Espera padrões específicos de preço/quantidade
3. **Layout único** - Não adapta para diferentes estruturas de encartes

## Melhorias Implementadas

O novo `ocr_processor_avancado.py` implementa:

### 1. Múltiplas Estratégias de Parsing

#### Layout em Linha
- Detecta preço em qualquer posição (início, meio, fim)
- Detecta quantidade em formatos variados
- Busca marca em qualquer lugar da linha

#### Layout em Cards
- Divide texto em blocos (cards separados)
- Busca informações em qualquer linha do card
- Útil para encartes com produtos em grid

#### Layout em Tabela
- Detecta múltiplas colunas
- Processa cada coluna separadamente
- Útil para encartes tabulares

### 2. Detecção de Regiões

- Usa análise de contornos (OpenCV)
- Identifica cards de produtos automaticamente
- Processa cada região separadamente

### 3. Múltiplas Configurações OCR

- Testa diferentes modos PSM (Page Segmentation Mode)
- PSM 6: Bloco uniforme de texto
- PSM 11: Texto esparso
- PSM 12: Texto esparso com OSD (Orientation and Script Detection)
- Escolhe o resultado mais completo

### 4. Padrões Flexíveis

#### Preços
- `R$ 12,99` (início)
- `12,99 R$` (final)
- `12,99 reais` (com texto)
- `preço: 12,99` (com label)

#### Quantidades
- `5kg`, `500g`, `1L`, `250ml`
- `5 quilos`, `500 gramas`
- `4 x 250ml` (pacotes múltiplos)

#### Marcas
- Busca em qualquer posição
- Normaliza variações (T. João = Tio João)
- Lista expandida de marcas conhecidas

## Como Usar

```python
from ocr_processor_avancado import OCRProcessorAvancado

ocr = OCRProcessorAvancado()
produtos = ocr.processar_imagem_multiplas_estrategias('imagem.jpg', 'Guanabara')
```

## Exemplos de Formatos Suportados

### Formato 1: Linha Simples
```
Arroz Tio João 5kg R$ 27,95
```

### Formato 2: Preço no Final
```
Cerveja Antarctica Lata 350ml 2,79 R$
```

### Formato 3: Card/Bloco
```
ARROZ BRANCO
TIO JOÃO
5kg
R$ 27,95
```

### Formato 4: Tabela
```
Produto        | Marca      | Qtd  | Preço
Arroz Branco  | Tio João   | 5kg  | R$ 27,95
Feijão Preto  | Tio João   | 1kg  | R$ 8,90
```

## Próximos Passos

1. **Machine Learning**: Treinar modelo para detectar layouts automaticamente
2. **Template Matching**: Criar templates específicos por mercado
3. **Validação**: Adicionar validação de dados extraídos
4. **Feedback Loop**: Aprender com correções manuais
