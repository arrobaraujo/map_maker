# GTFS Map Maker - SIG e Otimizações Técnicas

Este plano detalha a implementação de correções técnicas e exportação para arquivos geográficos (GIS).

##Proposed Changes

#### [MODIFY] [gtfs_processor.py](file:///c:/R_SMTR/projetos/map_maker/codigos/gtfs_processor.py)
- **Cache de Shapes:** Implementar dicionário `coords_cache` para evitar re-processamento repetitivo de geometrias.
- **Robustez de Leitura:** Adicionar suporte a arquivos com encoding UTF-8-sig e tratamento de linhas corrompidas no `pd.read_csv`.

#### [MODIFY] [gtfs_map_app.py](file:///c:/R_SMTR/projetos/map_maker/codigos/gtfs_map_app.py)
- **Exportação SIG:** Adicionar botão "Exportar SIG" para salvar camadas ativas nos formatos GeoPackage (.gpkg) e Shapefile (.shp).
- **Dependência Geopandas:** Utilizar o `geopandas` para criar a estrutura espacial necessária para a exportação.

## Verification Plan

### Manual Verification
1.  Carregar um GTFS e adicionar 3 camadas.
2.  Clicar em "Exportar SIG" e salvar como .gpkg.
3.  Alternar repetidamente entre as rotas para validar se o sistema de cache as torna instantâneas.
