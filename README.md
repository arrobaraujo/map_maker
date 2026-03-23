# GTFS Map Maker

[**English Version**](README_EN.md)

Gerador de mapas de itinerários GTFS com interface gráfica moderna e suporte a SIG.

## 📥 Download (Versão Pronta)

Se você quer apenas rodar o aplicativo sem precisar instalar o Python:
1. Acesse a aba [**Releases**](https://github.com/arrobaraujo/map_maker/releases) deste repositório.
2. Baixe o arquivo `.exe` mais recente ao fim da página na seção "Assets".
3. Execute o arquivo diretamente! (Se o Windows bloquear, veja [este guia](DISTRIBUTION_PT.md)).

## ✨ Funcionalidades
- **Zoom Granular (0.1)**: Ajuste de zoom preciso para enquadramentos perfeitos, com suavidade e sem saltos bruscos.
- **Seleção Múltipla Inteligente**: Selecione várias camadas com **Ctrl + Clique** ou uma linha completa (todas as direções) com **Shift + Clique**.
- **Estilização em Lote**: Altere cor e espessura de múltiplas camadas selecionadas simultaneamente.
- **Legenda Inteligente:** Unificação automática por cor para simplificar a visualização.
- Remoção Individual de Camadas com botão (✕).
- Capturas de tela limpas (oculta botões de zoom automaticamente).
- **Exportação de Alta Qualidade:** Controle de DPI para imagens e PDFs nítidos.
- **Exportação Profissional:** Salve suas rotas selecionadas em formatos **SVG (Vetorial)**, **KML (Google Earth)**, **GeoPackage (.gpkg)** e **Shapefile (.shp)**.

## Dependências
- Python 3.9+
- CustomTkinter
- TkinterMapView
## 🚀 Como Executar (Código Fonte)

1. Certifique-se de ter o Python 3.10+ instalado.
2. Instale as dependências:
   ```bash
   pip install -r requirements.txt
   ```
3. Execute a aplicação:
   ```bash
   python src/app.py
   ```

## 📦 Como Gerar o Executável (.exe)

Para criar um arquivo único `.exe` para Windows:

1. Instale o PyInstaller:
   ```bash
   pip install pyinstaller
   ```
2. Gere o executável com o comando (ajuste o caminho da `.venv` se necessário):
   ```bash
   python -m PyInstaller --noconsole --onefile --add-data ".venv/Lib/site-packages/customtkinter;customtkinter/" src/app.py
   ```
3. O arquivo final estará na pasta `dist/`.

## 📂 Estrutura do Projeto

- `src/`: Código fonte.
  - `app.py`: Interface principal (GUI).
  - `processor.py`: Lógica GTFS.
  - `utils/renderer.py`: Renderização de mapas.
- `tests/`: Testes automatizados (`pytest`).
- `map_tiles_cache/`: Cache de mapas offline.
