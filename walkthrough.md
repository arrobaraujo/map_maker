# GTFS Map Maker - Exportação de Alta Fidelidade

O aplicativo agora conta com um motor de renderização digital para o modo transparente, garantindo resultados perfeitos para design profissional.

## Mudanças Realizadas

### [gtfs_map_app.py](file:///c:/R_SMTR/projetos/map_maker/codigos/gtfs_map_app.py)

1.  **Renderização Digital Direta (Modo Transparent):** Ao salvar como PNG no modo transparente, o app não faz mais uma captura de tela (`ImageGrab`). Em vez disso, ele converte as coordenadas geográficas em pixels e desenha as rotas diretamente em uma imagem `RGBA` do Pillow.
    *   **Resultado 1:** Bordas perfeitamente nítidas e cores sólidas (sem o efeito de "fade/esfumaçado").
    *   **Resultado 2:** Captura limpa. Como não é um print da tela, **marcas d'água do Windows (como "Ativar o Windows") não aparecem no arquivo final**.
2.  **Legenda Digital:** A legenda no modo transparente também passou a ser gerada digitalmente, garantindo que o fundo branco da legenda seja nítido e bem posicionado.
3.  **Legenda Circular Inteligente (Novo):** O sistema agora detecta automaticamente se uma linha é circular (via `trip_headsign`). Para estas linhas, a legenda exibe apenas o **Número - Vista (Long Name)**, removendo o sufixo "(Ida)" que era redundante.
4.  **DPI Inteligente:** O sistema de renderização digital respeita o valor de DPI selecionado, gerando arquivos em altíssima resolução sem perda de qualidade.

## Como Testar as Funções

1.  **Exportação Perfeita:** Selecione "Transparent", adicione algumas rotas e salve como PNG. Abra o arquivo e dê zoom nas bordas; você verá que a cor é sólida até o último pixel.
2.  **Fim da Marca d'água:** Mesmo que o seu Windows exiba avisos de ativação no canto da tela, o modo Transparente gerará um arquivo totalmente limpo, pois ele ignora o buffer de tela do SO.

---
**Walkthrough concluído.**
