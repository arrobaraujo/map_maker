# GTFS Map GUI

Visualizador de itinerários GTFS com interface gráfica moderna.

## Funcionalidades
- Leitura de arquivos GTFS (.zip).
- Seleção de rotas específicas.
- Customização de cor e espessura das linhas.
- Controle de ordem de camadas (z-index).
- Diferentes opções de mapas de fundo (Basemaps).

## Dependências
- Python 3.9+
- CustomTkinter
- TkinterMapView
- Pandas
- GeoPandas
- Shapely
- Pyogrio (recomendado para performance)

## Como usar
1. Instale as dependências: `pip install customtkinter tkintermapview pandas geopandas shapely pyogrio`
2. Execute o aplicativo: `python codigos/gtfs_map_app.py`
3. Selecione o arquivo GTFS .zip no menu superior.
4. Use o painel lateral para filtrar e adicionar rotas ao mapa.
