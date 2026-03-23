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

## Como gerar o novo release?
1. Clique em **Releases** no seu repositório GitHub.
2. Clique em **Draft a new release**.
3. Tag: `v1.1.0`
4. Título: `v1.1.0 - GTFS Professional Upgrade`
5. Cole as notas acima na descrição.
6. Anexe o seu arquivo `.exe` gerado.

---
*GTFS Map Maker - Tornando dados complexos em mapas bonitos.*
