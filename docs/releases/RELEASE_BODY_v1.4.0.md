# GTFS Map Maker v1.4.0

Esta versao entrega uma refatoracao arquitetural ampla para facilitar manutencao, testes e evolucao do projeto.

## Novidades

### Arquitetura modular
- Nova camada de controllers para orquestracao de fluxo:
  - `src/controllers/map_controller.py`
  - `src/controllers/gtfs_controller.py`
- Nova camada de services para regras de negocio:
  - `src/services/layer_service.py`
  - `src/services/zoom_service.py`
  - `src/services/export_service.py`
- Nova camada de UI builder:
  - `src/ui/ui_builder.py`

### Melhorias tecnicas
- `src/app.py` simplificado e focado em coordenacao.
- Separacao clara entre interface, orquestracao e regras de negocio.
- Ajuste para evitar redraw desnecessario na reordenacao de camadas sem mudanca real.

### Qualidade
- Suite de testes expandida para controllers e services.
- Cobertura de cenarios para:
  - selecao e reordenacao de camadas
  - parse/clamp de zoom
  - exportacao KML/SVG
  - carregamento GTFS assincrono

## Compatibilidade
- Mantem comportamento da interface e fluxo principal do usuario.
- Requer Python 3.10+.
