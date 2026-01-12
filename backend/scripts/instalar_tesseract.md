# Instalação do Tesseract OCR

## Windows

1. Baixe o instalador do Tesseract:
   https://github.com/UB-Mannheim/tesseract/wiki

2. Instale o Tesseract (recomendado: C:\Program Files\Tesseract-OCR)

3. Adicione ao PATH do sistema ou configure no código:
   ```python
   pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
   ```

4. Baixe o pacote de idioma português (por.traineddata) e coloque em:
   C:\Program Files\Tesseract-OCR\tessdata\

## Linux (Ubuntu/Debian)

```bash
sudo apt-get update
sudo apt-get install tesseract-ocr
sudo apt-get install tesseract-ocr-por
```

## macOS

```bash
brew install tesseract
brew install tesseract-lang
```


