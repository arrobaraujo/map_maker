# GTFS Map Maker

[**English Version**](README.md)

Gerador de mapas de itinerários GTFS com interface gráfica moderna e suporte a SIG.

- Arquitetura: [ARCHITECTURE_PT.md](ARCHITECTURE_PT.md)
- Contribuição: [CONTRIBUTING_PT.md](CONTRIBUTING_PT.md)

## 📥 Download (Versão Pronta)

Se você quer apenas rodar o aplicativo sem precisar instalar o Python:
1. Acesse a aba [**Releases**](https://github.com/arrobaraujo/map_maker/releases) deste repositório.
2. Baixe o arquivo `.exe` mais recente ao fim da página na seção "Assets".
3. Execute o arquivo diretamente! (Se o Windows bloquear, veja [este guia](DISTRIBUTION_PT.md)).

## ✨ Funcionalidades
- **Zoom Granular (0.1)**: Ajuste de zoom preciso para enquadramentos perfeitos, com suavidade e sem saltos bruscos.
- **Seleção Múltipla Inteligente**: Selecione várias camadas com **Ctrl + Clique** ou uma linha completa (todas as direções) com **Shift + Clique**.
- **Estilização em Lote**: Altere cor e espessura de múltiplas camadas selecionadas simultaneamente.
- **Legenda Inteligente:** Unificação automática por cor para simplificar a visualização.
- Remoção Individual de Camadas com botão (✕).
- Capturas de tela limpas (oculta botões de zoom automaticamente).
- **Exportação de Alta Qualidade:** Controle de DPI para imagens e PDFs nítidos.
- **Exportação Profissional:** Salve suas rotas selecionadas em formatos **SVG (Vetorial)**, **KML (Google Earth)**, **GeoPackage (.gpkg)** e **Shapefile (.shp)**.

## Dependências
- Python 3.9+
- CustomTkinter
- TkinterMapView
## 🚀 Como Executar (Código Fonte)

1. Certifique-se de ter o Python 3.10+ instalado.
2. Instale as dependências:
   ```bash
   pip install -r requirements.txt
   ```
3. Execute a aplicação:
   ```bash
   python src/app.py
   ```

## 🐳 Como Executar com Docker

O projeto inclui container com GUI via Xvfb + VNC + noVNC.

1. Build e execução:
   ```bash
   docker compose up --build
   ```
2. Abra no navegador:
   - http://localhost:6080/vnc.html
3. Acesso VNC direto (opcional):
   - Host: `localhost`
   - Porta: `5901`

Observações:
- A pasta `map_tiles_cache` é montada como volume para preservar cache de tiles.
- O runtime Docker é voltado para desenvolvimento e demonstrações.

## 📦 Como Gerar o Executável (.exe)

Para criar um arquivo único `.exe` para Windows:

1. Instale o PyInstaller:
   ```bash
   pip install pyinstaller
   ```
2. Gere com o script fornecido:
   ```powershell
   .\scripts\build_exe.ps1 -Clean
   ```
   Ou rode o PyInstaller diretamente:
   ```bash
   pyinstaller app.spec
   ```
3. O arquivo final estará na pasta `dist/`.

## 📂 Estrutura do Projeto

- `src/`: Código fonte.
  - `app.py`: Interface principal (GUI).
  - `processor.py`: Lógica GTFS.
  - `utils/renderer.py`: Renderização de mapas.
- `tests/`: Testes automatizados (`pytest`).
- `map_tiles_cache/`: Cache de mapas offline.
