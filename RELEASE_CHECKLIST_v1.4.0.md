# Release Checklist - v1.4.0

## Pre-release

- [x] Atualizar `VERSION` para `1.4.0`
- [x] Atualizar `APP_VERSION` em `src/app.py`
- [x] Atualizar `RELEASE_NOTES.md` com secao v1.4.0
- [x] Atualizar documentacao (`README`, `CONTRIBUTING`, `ARCHITECTURE` em PT/EN)
- [x] Rodar testes automatizados
- [x] Gerar executavel final (`dist/app.exe`)

## Git

1. Commit da versao:
   ```bash
   git add .
   git commit -m "refactor: modularize architecture and prepare v1.4.0 release"
   ```
2. Criar tag:
   ```bash
   git tag -a v1.4.0 -m "Release v1.4.0"
   ```
3. Push branch e tag:
   ```bash
   git push origin main
   git push origin v1.4.0
   ```

## GitHub Release

1. Criar release para tag `v1.4.0`
2. Titulo: `v1.4.0`
3. Notas: usar `RELEASE_BODY_v1.4.0.md`
4. Asset: anexar `dist/app.exe`
5. Publicar release
