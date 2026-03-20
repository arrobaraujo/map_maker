# GTFS Map Maker

Gerador de mapas de itinerários GTFS com interface gráfica moderna e suporte a SIG.

## Funcionalidades
- Leitura de arquivos GTFS (.zip) com robustez a erros de codificação.
- Seleção de rotas específicas com sistema de **Cache de Geometrias** (carregamento instantâneo).
- **Cache de Mapa (Tiles):** Armazenamento local de blocos de mapa visitados, permitindo uso offline e economia de banda.
- Customização de cor e espessura das linhas.
- Controle de ordem de camadas (z-index).
- Diferentes opções de mapas de fundo (Basemaps), incluindo Rio PGeo3.
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
- **GeoPandas** (para exportação SIG)
- **Shapely**
- **Pyogrio** (motor de alta performance para SIG)
- Pillow (PIL)

## Como usar
1. Instale as dependências: `pip install customtkinter tkintermapview pandas geopandas shapely pyogrio pillow`
2. Execute o aplicativo: `python codigos/gtfs_map_app.py`
3. Selecione o arquivo GTFS .zip no menu superior.
4. Use o painel lateral para filtrar e adicionar rotas ao mapa.
5. Use "Exportar SIG" para salvar os dados espaciais em formatos compatíveis com QGIS/ArcGIS.
