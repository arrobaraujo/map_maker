# GTFS Map Maker - Melhorias Profissionais, SIG e Cache

O aplicativo agora conta com ferramentas de exportação geográfica, cache de dados e mapa, e melhorias significativas de performance e interface.

## Mudanças Realizadas

### [gtfs_processor.py](file:///c:/R_SMTR/projetos/map_maker/codigos/gtfs_processor.py)

1.  **Sistema de Cache de Geometria:** Implementado cache de coordenadas. Uma vez que uma rota é carregada, ela é armazenada em memória, tornando a ativação/desativação instantânea.
2.  **Leitura Robusta:** Suporte automático para arquivos GTFS com BOM (UTF-8-sig) e tratamento de erros de parser.

### [gtfs_map_app.py](file:///c:/R_SMTR/projetos/map_maker/codigos/gtfs_map_app.py)

1.  **Cache de Mapa (Tiles):** Implementado diretório `map_tiles_cache`. O aplicativo agora salva automaticamente todos os blocos de mapa visualizados no disco. Isso permite navegar no mapa sem internet nas áreas já visitadas e acelera drasticamente o carregamento.
2.  **Exportação Geográfica (SIG):** Botão **"🌐 Exportar SIG"** para salvar rotas em **GeoPackage (.gpkg)** ou **Shapefile (.shp)**.
3.  **Legenda Inteligente:** Legenda ampliada em 20% com lógica de unificação por cor (Vista vs Headsign).
4.  **DPI de Alta Qualidade:** Controle de resolução para exportações profissionais.

## Como Testar as Funções

1.  **Cache de Mapa:** Navegue por uma área, feche o app e desligue a internet (ou mude de local). O mapa continuará visível nas áreas visitadas.
2.  **Exportação SIG:** Monte seu mapa e exporte para .gpkg para validar no QGIS.
3.  **Performance:** Note a fluidez ao alternar rotas e navegar no mapa.

---
**Walkthrough concluído.**
