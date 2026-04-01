# Arquitetura – GTFS Map Maker

> Visão geral da estrutura interna, fluxo de dados e decisões de design do projeto.

---

## 📂 Estrutura do Projeto

```
map_maker/
├── src/                        # Código-fonte principal
│   ├── app.py                  # Interface gráfica (GUI) – ponto de entrada
│   ├── processor.py            # Processamento e indexação de dados GTFS
│   └── utils/
│       └── renderer.py         # Renderização de mapas (exportação transparente, simplificação)
├── tests/
│   └── test_processor.py       # Testes automatizados (pytest)
├── map_tiles_cache/            # Cache local de tiles do mapa (SQLite)
├── requirements.txt            # Dependências Python
├── app.spec                    # Configuração do PyInstaller para gerar .exe
├── LICENSE                     # Licença GPL-3.0
├── README.md / README_EN.md    # Documentação principal (PT / EN)
├── DISTRIBUTION_PT.md / DISTRIBUTION_EN.md  # Guia de distribuição
├── RELEASE_NOTES.md            # Histórico de versões
└── .gitignore
```

---

## 🧩 Módulos e Responsabilidades

### `src/app.py` — Interface Gráfica (GUI)

| Classe / Função       | Responsabilidade |
|------------------------|------------------|
| `GTFSMapApp`           | Classe principal da aplicação. Herda de `ctk.CTk` (CustomTkinter). |
| `setup_ui()`           | Monta toda a interface: sidebar, controles, mapa e legenda. |
| `load_gtfs()`          | Abre o diálogo de arquivo e dispara o carregamento assíncrono (thread). |
| `toggle_route()`       | Adiciona ou remove uma rota do mapa interativo. |
| `select_layer()`       | Gerencia seleção de camadas (simples, Ctrl+Click, Shift+Click). |
| `redraw_all_paths()`   | Redesenha todas as rotas no mapa respeitando ordem e estilos. |
| `save_map()`           | Exporta o mapa como PNG, PDF ou SVG (com controle de DPI). |
| `export_sig()`         | Exporta camadas como GeoPackage, Shapefile ou KML. |
| `update_legend()`      | Gera a legenda flutuante com agrupamento inteligente por cor. |

**Destaques de Design:**
- **Virtual Scrolling** na lista de rotas para suportar milhares de linhas sem travamento.
- **Seleção múltipla** com Ctrl/Shift para estilização em lote.
- **Zoom fracionário (0.1)** implementado via botões +/- e campo de entrada.
- **High DPI Awareness** via Windows `SetProcessDpiAwareness`.

---

### `src/processor.py` — Motor GTFS

| Classe / Função               | Responsabilidade |
|--------------------------------|------------------|
| `GTFSProcessor`                | Carrega e indexa dados GTFS de um arquivo ZIP. |
| `_setup_db()`                  | Cria tabela SQLite temporária para armazenar coordenadas. |
| `load_data()`                  | Lê `routes.txt`, `trips.txt` e `shapes.txt` do ZIP. |
| `get_route_list()`             | Retorna lista processada de rotas com metadados para a UI. |
| `get_shape_coordinates()`      | Busca coordenadas (lat, lon) de um `shape_id` no SQLite. |
| `close()`                      | Fecha a conexão e remove o banco temporário. |

**Destaques de Design:**
- **SQLite temporário** para geometrias: evita carregar milhões de pontos na RAM.
- **Chunk loading** (`chunksize=100000`) para processar `shapes.txt` de arquivos grandes.
- **`atexit` handler** para garantir limpeza do banco temporário.

---

### `src/utils/renderer.py` — Renderização e Utilidades

| Função                        | Responsabilidade |
|-------------------------------|------------------|
| `simplify_path()`             | Algoritmo Douglas-Peucker para decimação de coordenadas. |
| `render_transparent_map()`    | Renderiza mapa com fundo transparente via projeção manual. |
| `_draw_legend()`              | Desenha a legenda na imagem exportada. |

**Destaques de Design:**
- **Douglas-Peucker** aplicado tanto na exibição interativa (mapa) quanto na exportação.
- **Projeção manual** `decimal_to_osm` para converter lat/lon em pixels sem depender do widget.

---

## 🔀 Fluxo de Dados

```
┌──────────────┐      ┌───────────────────┐      ┌──────────────────┐
│  Arquivo ZIP │ ───▶ │  GTFSProcessor    │ ───▶ │  GTFSMapApp      │
│  (GTFS)      │      │  (processor.py)   │      │  (app.py)        │
│              │      │                   │      │                  │
│ routes.txt   │      │ routes → DataFrame│      │ Lista de rotas   │
│ trips.txt    │      │ trips  → DataFrame│      │ (virtual scroll) │
│ shapes.txt   │      │ shapes → SQLite   │      │                  │
└──────────────┘      └───────────────────┘      └────────┬─────────┘
                                                          │
                                                          ▼
                                              ┌──────────────────────┐
                                              │  TkinterMapView      │
                                              │  (mapa interativo)   │
                                              │                      │
                                              │  ┌──────────────┐    │
                                              │  │ renderer.py  │    │
                                              │  │ (exportação) │    │
                                              │  └──────────────┘    │
                                              └──────────────────────┘
```

### Pipeline detalhado:

1. **Carregamento** → Usuário abre um `.zip` GTFS. O `GTFSProcessor` lê metadados (`routes`, `trips`) para DataFrames Pandas e insere coordenadas (`shapes`) no SQLite temporário.
2. **Listagem** → `get_route_list()` faz merge de `routes` + `trips`, gera nomes de exibição (incluindo headsign e direção), e retorna para a UI.
3. **Visualização** → Ao clicar numa rota, `get_shape_coordinates()` busca coordenadas no SQLite. O `simplify_path()` aplica Douglas-Peucker se há >500 pontos. As coordenadas simplificadas são passadas ao `TkinterMapView.set_path()`.
4. **Exportação** → O `renderer.py` faz projeção manual (lat/lon → pixel) e renderiza via `PIL.ImageDraw`. Suporta PNG transparente, PDF, SVG e formatos SIG (GeoPackage, Shapefile, KML).

---

## 🛠️ Stack Tecnológica

| Camada          | Tecnologia                     | Justificativa |
|-----------------|--------------------------------|---------------|
| GUI Framework   | CustomTkinter                  | Desktop nativo, visual moderno, sem dependência web. |
| Mapa Interativo | TkinterMapView                 | Widget de mapa com tiles, paths e markers integrados ao Tkinter. |
| Dados Tabulares | Pandas                         | Leitura eficiente de CSVs GTFS com tipagem e filtragem. |
| Geometria       | GeoPandas + Shapely            | Exportação SIG (GeoPackage, Shapefile). |
| Armazenamento   | SQLite (temporário)            | Banco leve para indexar milhões de coordenadas sem consumir RAM. |
| Renderização    | Pillow (PIL)                   | Geração de imagens (PNG/PDF) com desenho vetorial programático. |
| Distribuição    | PyInstaller                    | Gera executável `.exe` standalone para Windows. |
| I/O Geoespacial | pyogrio                        | Backend rápido para leitura/escrita de formatos SIG. |

---

## 🏗️ Decisões de Design

### Por que SQLite para shapes?
Arquivos GTFS grandes (ex: São Paulo, Rio de Janeiro) possuem milhões de pontos em `shapes.txt`. Carregar tudo na RAM com Pandas consumiria ~2 GB. O SQLite temporário com índice em `shape_id` permite consultas rápidas com ~50 MB de uso.

### Por que Virtual Scrolling na lista de rotas?
Criar centenas de widgets CustomTkinter simultaneamente causa lag significativo. O sistema de "button pool" renderiza apenas os itens visíveis e reusa os widgets ao rolar, mantendo a interface fluida mesmo com 5.000+ rotas.

### Por que Douglas-Peucker?
Rotas com 10.000+ coordenadas são comuns. Sem simplificação, o desenho no canvas Tkinter fica lento. O algoritmo reduz para ~500–1.000 pontos com perda visual imperceptível (epsilon=0.0001 para lat/lon).

### Por que exportação SVG manual?
Não existe biblioteca Python simples que projete coordenadas geográficas para SVG de forma integrada ao TkinterMapView. A projeção manual `decimal_to_osm` garante que o SVG gerado corresponda exatamente ao enquadramento do mapa na tela.

---

## 📦 Distribuição

O executável standalone é gerado com PyInstaller:

```
python -m PyInstaller --noconsole --onefile \
    --add-data ".venv/Lib/site-packages/customtkinter;customtkinter/" \
    src/app.py
```

O arquivo `app.spec` contém a configuração completa. O `.exe` gerado inclui todas as dependências e pode ser distribuído diretamente (sem instalação de Python).

---

## 🧪 Testes

- Framework: **pytest**
- Localização: `tests/test_processor.py`
- Escopo atual: Validação de inicialização do `GTFSProcessor` (falha em arquivo inexistente).
- Expansão futura: Testes com arquivos GTFS de amostra para validar parsing, merge e coordenadas.

```bash
pytest tests/ -v
```
