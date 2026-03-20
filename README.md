# GTFS Map Maker

Gerador de mapas de itinerários GTFS com interface gráfica moderna.

## Funcionalidades
- Leitura de arquivos GTFS (.zip).
- Seleção de rotas específicas.
- Customização de cor e espessura das linhas.
- Controle de ordem de camadas (z-index).
- Diferentes opções de mapas de fundo (Basemaps), incluindo Rio PGeo3.
- Legenda Inteligente (unificação automática de ida e volta por cor).
- Remoção Individual de Camadas com botão (✕).
- Capturas de tela limpas (oculta botões de zoom automaticamente).
- **Exportação de Alta Qualidade:** Controle de DPI para imagens e PDFs nítidos.
- **Legenda Ampliada:** Escala ajustada em 20% para melhor leitura em grandes formatos.

## Dependências
- Python 3.9+
- CustomTkinter
- TkinterMapView
- Pandas
- GeoPandas
- Shapely
- Pyogrio (recomendado para performance)
- Pillow (PIL)

## Como usar
1. Instale as dependências: `pip install customtkinter tkintermapview pandas geopandas shapely pyogrio pillow`
2. Execute o aplicativo: `python codigos/gtfs_map_app.py`
3. Selecione o arquivo GTFS .zip no menu superior.
4. Use o painel lateral para filtrar e adicionar rotas ao mapa.
