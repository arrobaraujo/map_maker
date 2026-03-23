# GTFS Map Maker

[**English Version**](README_EN.md)

Gerador de mapas de itinerários GTFS com interface gráfica moderna e suporte a SIG.

## 📥 Download (Versão Pronta)

Se você quer apenas rodar o aplicativo sem precisar instalar o Python:
1. Acesse a aba [**Releases**](https://github.com/arrobaraujo/map_maker/releases) deste repositório.
2. Baixe o arquivo `.exe` mais recente ao fim da página na seção "Assets".
3. Execute o arquivo diretamente! (Se o Windows bloquear, veja [este guia](DISTRIBUTION_PT.md)).

## ✨ Funcionalidades
- Leitura de arquivos GTFS (.zip) com robustez a erros de codificação.
- Seleção de rotas específicas com sistema de **Cache de Geometrias** (carregamento instantâneo), **Carregamento Assíncrono** e **Virtualização de Lista** para suportar milhares de rotas.
- **Desenho Inteligente:** Algoritmo de *Douglas-Peucker* para simplificar rotas complexas (decimação), garantindo fluidez e baixo consumo de memória.
- **Cache de Mapa (Tiles):** Armazenamento local de blocos de mapa visitados.
- **Exportação Transparente de Alta Fidelidade:** Opção de mapa "Transparent" que gera PNGs com fundo invisível (Alpha) via **renderização digital direta**. Isso garante cores 100% sólidas sem efeito de fade nas bordas e **elimina marcas d'água do sistema (como "Ativar Windows")**.
- **Controle de Legenda:** Habilite ou desabilite a legenda. No modo transparente, ela também é renderizada digitalmente.
- **Cores Oficiais do GTFS:** Aplicação automática das cores originais da agência (`route_color`).
- Customização manual de cor e espessura das linhas.
- Controle de ordem de camadas (z-index).
- Diferentes opções de mapas de fundo (Basemaps) de alta performance.
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
   pyinstaller --noconsole --onefile --add-data ".venv/Lib/site-packages/customtkinter;customtkinter/" src/app.py
   ```
3. O arquivo final estará na pasta `dist/`.

## 📂 Estrutura do Projeto

- `src/`: Código fonte.
  - `app.py`: Interface principal (GUI).
  - `processor.py`: Lógica GTFS.
  - `utils/renderer.py`: Renderização de mapas.
- `tests/`: Testes automatizados (`pytest`).
- `map_tiles_cache/`: Cache de mapas offline.
