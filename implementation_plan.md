# Refinamento de Design e Exportação de Alta Fidelidade

O objetivo é eliminar artefatos visuais causados pela captura de tela no modo transparente.

##Proposed Changes

#### [MODIFY] [gtfs_map_app.py](file:///c:/R_SMTR/projetos/map_maker/codigos/gtfs_map_app.py)
- **Motor de Renderização:** Implementar lógica no `save_map` que utiliza `ImageDraw.Draw` e `map_widget.get_canvas_pos` para desenhar as rotas no modo transparente.
- **Isolamento de Buffer:** Ignorar o `ImageGrab` para evitar a captura de sobreposições do sistema (watermarks).

## Verification Plan

### Manual Verification
1.  Selecionar modo "Transparent".
2.  Salvar o mapa como PNG.
3.  Verificar se a cor da borda está sólida (sem fade).
4.  Confirmar que a marca d'água "Ativar Windows" não está presente na imagem salva.
