# Release Notes - v1.3.0

Esta versão adiciona suporte a Docker com GUI no navegador, melhorias de estabilidade e documentação em inglês para arquitetura e contribuição.

## O que ha de novo?

### Docker e Execucao
- Adicionado `Dockerfile` com runtime de GUI baseado em Xvfb + x11vnc + noVNC.
- Adicionado `docker-compose.yml` para subir o app com um comando.
- Acesso web da interface em `http://localhost:6080/vnc.html`.
- Volume para persistir cache de tiles (`map_tiles_cache`).

### Melhorias no App
- Corrigido bug de remocao de camada que mantinha estado residual em memoria.
- Removida duplicacao no ajuste de zoom.
- Melhorado encerramento do app para liberar recursos do processador GTFS.

### Melhorias no Processamento
- Validacao explicita de arquivos obrigatorios no GTFS (`routes.txt`, `trips.txt`, `shapes.txt`).
- Fechamento idempotente do `GTFSProcessor` para evitar erros em chamadas repetidas.

### Documentacao
- Criado `CONTRIBUTING.md` em ingles.
- Criado `ARCHITECTURE.md` em ingles.
- README em PT e EN atualizados com instrucoes de Docker e build do executavel.
- Adicionado script `scripts/build_exe.ps1` para gerar o `.exe` com `app.spec`.

---

# Release Notes - v1.2.0 🎯

Esta versão traz o **Zoom Fracionário Estabilizado** e melhorias significativas na **Interface de Camadas**.

## O que há de novo?

### 🗺️ Mapa e Navegação (Foco em Precisão)
- **Zoom Granular (0.1)**: Agora você pode ajustar o zoom em passos de 0.1 (ex: 14.5). O mapa não "pula" mais apenas nos inteiros, permitindo o enquadramento perfeito.
- **Correção de Alinhamento**: Resolvemos o problema de tiles desalinhados ou "misturados" durante o zoom fracionário. Marcadores e rotas permanecem perfeitamente posicionados.
- **Performance de Renderização**: Implementamos um sistema de cache de redimensionamento de tiles. O mapa agora é muito mais fluido ao navegar e aproximar.

### 🍱 Gestão de Camadas (Sidebar)
- **Seleção Múltipla**: Agora é possível selecionar várias camadas simultaneamente na lista lateral.
    - **Ctrl + Clique**: Seleciona/deseleciona camadas individuais.
    - **Shift + Clique**: Seleciona automaticamente **todas as direções da mesma linha** (ex: Ida e Volta).
- **Estilização em Lote**: Altere a cor ou a espessura de todas as camadas selecionadas de uma só vez, economizando tempo no design do mapa.

### 🧹 Limpeza e Estabilidade
- **Console Limpo**: Removemos todos os logs de diagnóstico redundantes (`DEBUG LIB`, `DEBUG UTIL`), deixando o terminal livre de poluição visual.

---

# Release Notes - v1.1.0 🚀

Esta versão foca em **estilização automática**, **interoperabilidade** e **performance extrema**.

## O que há de novo?

### 🎨 Estilização e Cores
- **Cores Oficiais GTFS**: O app agora lê o campo `route_color` do seu arquivo GTFS. Ao selecionar uma linha, ela aparece automaticamente com a cor oficial da agência.
- **Suporte a SVG (Vetorial)**: Novo formato de exportação! Perfeito para designers que precisam editar o mapa no Adobe Illustrator ou Inkscape sem perda de qualidade.
- **Suporte a KML**: Agora você pode exportar suas rotas para o Google Earth ou outras ferramentas de GIS que utilizam o formato KML.

### ⚡ Performance e Estabilidade (Upgrade Massivo)
- **Carregamento Assíncrono**: O processamento do GTFS agora acontece em segundo plano, mantendo a interface sempre responsiva.
- **Otimização de Memória (SQLite)**: Reduzimos drasticamente o uso de RAM ao armazenar as coordenadas em um banco de dados temporário ultra-rápido.
- **Lista de Rotas Virtual**: Rolar e filtrar milhares de linhas agora é instantâneo, graças ao novo sistema de virtualização de interface.
- **Decimação de Coordenadas**: Implementamos o algoritmo de *Douglas-Peucker* para simplificar rotas complexas sem perder a precisão, resultando em um mapa muito mais fluido.