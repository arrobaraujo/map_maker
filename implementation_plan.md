# Adição de Controle de Qualidade e Refinamentos de Legenda

O objetivo é permitir a exportação de mapas em alta resolução (DPI configurável) e melhorar a legibilidade da legenda através de um aumento de escala.

## Proposed Changes

#### [MODIFY] [gtfs_map_app.py](file:///c:/R_SMTR/projetos/map_maker/codigos/gtfs_map_app.py)

1.  **Controle de DPI:** Adição de `dpi_label` e `dpi_entry` na barra superior.
2.  **Exportação Escalável:** Atualização de `save_map` para redimensionar a imagem (`Image.resize`) com base no DPI selecionado (Lanczos).
3.  **Dimensionamento da Legenda:** Aumento de 20% em todas as fontes (11 -> 14, 13 -> 16) e paddings internos da legenda.
4.  **Sincronização de Legenda:** Refinamento da lógica Cores Iguais (Vista) vs Cores Diferentes (Sentido).

## Verification Plan

### Manual Verification
1.  Executar o aplicativo: `python codigos/gtfs_map_app.py`.
2.  Alterar o valor de **Qualidade (DPI)** para 300.
3.  Salvar o mapa em PNG e PDF.
4.  Abrir o arquivo gerado e verificar se a resolução está superior à captura de tela padrão.
5.  Observar a legenda no mapa e confirmar que está maior e mais legível que na versão anterior.
