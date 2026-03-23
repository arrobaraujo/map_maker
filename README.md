# GTFS Map Maker

Gerador de mapas de itinerários GTFS com interface gráfica moderna e suporte a SIG.

## Funcionalidades
- Leitura de arquivos GTFS (.zip) com robustez a erros de codificação.
- Seleção de rotas específicas com sistema de **Cache de Geometrias** (carregamento instantâneo).
- **Cache de Mapa (Tiles):** Armazenamento local de blocos de mapa visitados.
- **Exportação Transparente de Alta Fidelidade:** Opção de mapa "Transparent" que gera PNGs com fundo invisível (Alpha) via **renderização digital direta**. Isso garante cores 100% sólidas sem efeito de fade nas bordas e **elimina marcas d'água do sistema (como "Ativar Windows")**.
- **Controle de Legenda:** Habilite ou desabilite a legenda. No modo transparente, ela também é renderizada digitalmente.
- Customização de cor e espessura das linhas.
- Controle de ordem de camadas (z-index).
- Diferentes opções de mapas de fundo (Basemaps) de alta performance.
- **Legenda Inteligente:** Unificação automática por cor para simplificar a visualização.
- Remoção Individual de Camadas com botão (✕).
- Capturas de tela limpas (oculta botões de zoom automaticamente).
- **Exportação de Alta Qualidade:** Controle de DPI para imagens e PDFs nítidos.
- **Exportação Geográfica (SIG):** Salve suas rotas selecionadas em formatos profissionais **GeoPackage (.gpkg)** e **Shapefile (.shp)**.

## Dependências
- Python 3.9+
- CustomTkinter
- TkinterMapView
## GTFS Map Maker 🌐🚌

Ferramenta visual para gerar mapas de itinerários a partir de arquivos GTFS.

## 🚀 Como Executar

1. Certifique-se de ter o Python 3.10+ instalado.
2. Instale as dependências:
   ```bash
   pip install -r requirements.txt
   ```
3. Execute a aplicação:
   ```bash
   python src/app.py
   ```

## 📂 Estrutura do Projeto

- `src/`: Código fonte da aplicação.
  - `app.py`: Interface principal e controle.
  - `processor.py`: Lógica de processamento de dados GTFS.
  - `utils/`: Utilitários e renderizadores.
- `tests/`: Testes automatizados.
- `map_tiles_cache/`: Cache local de mapas para uso offline.

## 🧪 Testes

Para rodar os testes unitários:
```bash
pytest tests/
```

## ✨ Funcionalidades

- Carregamento de GTFS (.zip)
- Visualização interativa com múltiplos provedores de mapas (Google, OSM, Esri, Carto).
- Customização de cores e espessura das linhas.
- Exportação para PNG transparente (Alta Qualidade/DPI).
- Exportação para SIG (GeoPackage e Shapefile).
- Sistema de cache de mapas para performance e uso offline.
