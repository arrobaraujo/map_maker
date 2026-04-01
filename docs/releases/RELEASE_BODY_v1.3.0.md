# GTFS Map Maker v1.3.0

Esta versao adiciona suporte a Docker com GUI no navegador, melhorias de estabilidade e documentacao em ingles.

## Novidades

### Docker e execucao
- Runtime de GUI com Xvfb + x11vnc + noVNC
- `docker-compose.yml` para subir com um comando
- Interface acessivel via `http://localhost:6080/vnc.html`
- Persistencia de cache em `map_tiles_cache`

### Melhorias no app
- Correcao de remocao de camada com estado residual
- Limpeza de duplicacao no ajuste de zoom
- Encerramento mais seguro com liberacao do processor

### Melhorias no processamento
- Validacao de arquivos obrigatorios no ZIP GTFS
- Fechamento idempotente do `GTFSProcessor`

### Documentacao e build
- Novo `CONTRIBUTING.md` em ingles
- Novo `ARCHITECTURE.md` em ingles
- READMEs PT/EN com instrucoes de Docker
- Script `scripts/build_exe.ps1` para gerar o executavel
