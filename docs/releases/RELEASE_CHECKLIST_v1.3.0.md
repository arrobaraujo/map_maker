# Release Checklist - v1.3.0

## Scope

- Docker support for GUI (Xvfb + VNC + noVNC)
- Stability fixes in app and processor
- New English docs: architecture and contributing
- Updated executable build flow

## Pre-release validation

- [x] Install dependencies and run tests
- [x] Build Windows executable (`dist/app.exe`)
- [x] Validate Docker build (`docker compose up --build`)
- [x] Validate noVNC endpoint (`/vnc.html` HTTP 200)
- [x] Confirm release notes updated to v1.3.0

## Artifacts

- [x] Windows executable: `dist/app.exe`
- [x] Changelog: `RELEASE_NOTES.md`
- [x] Docker files: `Dockerfile`, `docker-compose.yml`, `docker/entrypoint.sh`

## Git steps

1. Commit all release changes
   ```bash
   git add .
   git commit -m "chore(release): prepare v1.3.0"
   ```
2. Create annotated tag
   ```bash
   git tag -a v1.3.0 -m "Release v1.3.0"
   ```
3. Push branch and tag
   ```bash
   git push origin main
   git push origin v1.3.0
   ```

## GitHub Release steps

1. Open `Releases` > `Draft new release`
2. Select tag `v1.3.0`
3. Title: `v1.3.0`
4. Description: use `RELEASE_NOTES.md` entry for v1.3.0
5. Upload asset: `dist/app.exe`
6. Publish release

## Post-release checks

- [ ] Download `app.exe` from GitHub and execute smoke test
- [ ] Validate README links in public repo
- [ ] Announce release
