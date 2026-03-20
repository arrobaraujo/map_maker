# Adição da Camada de Mapa PGeo3 (Rio de Janeiro)

Agora é possível utilizar o mapa base oficial da Prefeitura do Rio de Janeiro diretamente no aplicativo **GTFS Map Maker**.

## Mudanças Realizadas

### [gtfs_map_app.py](file:///c:/R_SMTR/projetos/map_maker/codigos/gtfs_map_app.py)

1.  **Novo Item no Menu:** Adicionada a opção **"Rio PGeo3"** no menu suspenso de mapas base no canto superior direito.
2.  **Configuração de Tiles:** O servidor `pgeo3.rio.rj.gov.br` foi configurado como fonte de tiles para a nova opção.
3.  **Correção da Legenda:** A legenda foi movida para dentro do widget do mapa com a função `lift()`, garantindo que ela apareça sempre acima da camada de mapa.
4.  **Captura de Tela Limpa:** Implementada lógica automática que oculta os botões de zoom (+ e -) e os créditos apenas durante o processo de salvar o mapa (`Save Map`), restaurando-os logo em seguida.
5.  **Mapa Padrão:** O mapa **"Carto Light"** agora é selecionado automaticamente tanto na visualização quanto no menu ao abrir o aplicativo.
6.  **Erro Técnico Corrigido:** Eliminado o erro `TclError: unknown option "-padx"` que ocorria ao tentar carregar a legenda.
7.  **Remoção de Camadas (X):** Adicionado um botão "✕" vermelho ao lado de cada camada na lista lateral, permitindo remover rotas individualmente sem precisar procurá-las na lista principal.
8.  **Reorganização (↑/↓):** Os botões de subir e descer camadas foram movidos da barra superior para a lateral, ficando logo acima da lista, o que facilita o controle de sobreposição.
9.  **Design da Legenda:** A legenda agora é branca com texto preto e bordas arredondadas finas, posicionada no canto inferior esquerdo e integrada diretamente ao widget do mapa. O tamanho geral foi **aumentado em 20%** para garantir legibilidade máxima.
10. **Refinamento do Sidebar:** A barra lateral foi alargada e as proporções entre a lista de busca e as camadas ativas foram reequilibradas para maior conforto visual.
11. **Legenda Inteligente:**
    - Se a ida e volta de uma linha tiverem a **MESMA COR**: A legenda unifica os registros e exibe apenas a "Vista" (nome longo da linha).
    - Se tiverem **CORES DIFERENTES**: A legenda detalha cada sentido com seu destino (Headsign) e direção (Ida/Volta), permitindo identificação individual.
12. **Exportação de Alta Qualidade (DPI):** Adicionado um controle de qualidade na barra superior. Ao definir um DPI mais alto (ex: 300), o aplicativo redimensiona automaticamente a imagem final (PNG/PDF) para garantir nitidez profissional em impressões ou zooms.
13. **Suporte a route_long_name:** O sistema utiliza os nomes longos das rotas do GTFS para as legendas unificadas.

## Como Testar

1.  Abra o aplicativo executando `python codigos/gtfs_map_app.py`.
2.  No seletor de mapa base (canto superior direito), escolha **"Rio PGeo3"**.
3.  O mapa deve carregar o fundo cinza claro oficial da prefeitura.

> [!NOTE]
> Conforme discutido no plano de implementação, esta camada utiliza a projeção SIRGAS 2000. Embora funcione no aplicativo, você pode notar um leve desalinhamento (alguns metros) entre o desenho da rota do GTFS e as ruas do mapa de fundo.

---
**Walkthrough concluído.**
