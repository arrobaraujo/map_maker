# GTFS Map Maker

Gerador de mapas de itinerários GTFS com interface gráfica moderna e suporte a SIG.

## Funcionalidades
- Leitura de arquivos GTFS (.zip) com robustez a erros de codificação.
- Seleção de rotas específicas com sistema de **Cache de Geometrias** (carregamento instantâneo).
- **Cache de Mapa (Tiles):** Armazenamento local de blocos de mapa visitados.
- **Exportação Transparente de Alta Fidelidade:** Opção de mapa "Transparent" que gera PNGs com fundo invisível (Alpha) via **renderização digital direta**. Isso garante cores 100% sólidas sem efeito de fade nas bordas e **elimina marcas d'água do sistema (como "Ativar Windows")**.
- **Controle de Legenda:** Habilite ou desabilite a legenda. No modo transparente, ela também é renderizada digitalmente.
- Customização de cor e espessura das linhas.
- Controle de ordem de camadas (z-index).
- Diferentes opções de mapas de fundo (Basemaps) de alta performance.
- **Legenda Inteligente:** Unificação automática por cor para simplificar a visualização.
- Remoção Individual de Camadas com botão (✕).
- Capturas de tela limpas (oculta botões de zoom automaticamente).
- **Exportação de Alta Qualidade:** Controle de DPI para imagens e PDFs nítidos.
- **Exportação Geográfica (SIG):** Salve suas rotas selecionadas em formatos profissionais **GeoPackage (.gpkg)** e **Shapefile (.shp)**.

## Dependências
- Python 3.9+
- CustomTkinter
- TkinterMapView
- Pandas
- GeoPandas
- Shapely
- Pyogrio
- Pillow (PIL)

## Como usar
1. Instale as dependências: `pip install customtkinter tkintermapview pandas geopandas shapely pyogrio pillow`
2. Execute o aplicativo: `python codigos/gtfs_map_app.py`
3. Selecione o arquivo GTFS .zip no menu superior.
4. Escolha o mapa base desejado (ex: "Transparent" para exportação digital perfeita sem fundo).
5. Use o painel lateral para filtrar e adicionar rotas ao mapa.
6. Use o checkbox "Mostrar Legenda" para controlar a exibição dos nomes das linhas.
