# Contributing - GTFS Map Maker

Thank you for your interest in contributing. This document describes guidelines and workflow for project contributions.

---

## Prerequisites

- Python: 3.10+
- Git
- Operating System: Windows recommended for full GUI + PyInstaller validation

---

## Environment Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/arrobaraujo/map_maker.git
   cd map_maker
   ```

2. Create and activate a virtual environment:
   ```bash
   python -m venv .venv
   .venv\Scripts\activate     # Windows
   # source .venv/bin/activate  # Linux/macOS
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   pip install -r requirements-dev.txt
   ```

4. Run the app:
   ```bash
   python src/app.py
   ```

---

## Project Structure

Before contributing, review architecture details in [ARCHITECTURE.md](ARCHITECTURE.md).

```text
src/
├── app.py              # GUI (CustomTkinter)
├── processor.py        # GTFS processing engine (Pandas + SQLite)
└── utils/
    └── renderer.py     # Map rendering and geometry utilities
tests/
└── test_processor.py   # Automated tests (pytest)
```

---

## Contribution Workflow

### 1. Create a branch

Create a descriptive branch from main:

```bash
git checkout -b feature/your-feature
git checkout -b fix/bug-description
git checkout -b docs/doc-change
```

Branch naming convention:

| Prefix     | Usage                                   |
|------------|------------------------------------------|
| feature/   | New feature                              |
| fix/       | Bug fix                                  |
| refactor/  | Refactor (no behavior change)            |
| docs/      | Documentation only                       |
| test/      | New or improved tests                    |

### 2. Develop and test

- Follow coding guidelines.
- Add or update tests when applicable.
- Run tests before opening your PR:
  ```bash
  pytest tests/ -v
  ```

### 3. Commit and push

Use descriptive commit messages:

```bash
git add .
git commit -m "feat: add GeoJSON export"
git push origin feature/geojson-export
```

Conventional Commits quick reference:

| Prefix     | Usage                                           |
|------------|--------------------------------------------------|
| feat:      | New feature                                     |
| fix:       | Bug fix                                         |
| refactor:  | Code refactor                                   |
| docs:      | Documentation changes                           |
| test:      | New or updated tests                            |
| style:     | Formatting changes (no logic changes)           |
| chore:     | Maintenance tasks (deps, config, CI, etc.)      |

### 4. Open a Pull Request

- Open a PR against main.
- Clearly explain what changed and why.
- Include screenshots for UI changes.
- Reference issues when applicable (for example: Closes #12).

---

## Coding Guidelines

### Style

- Follow PEP 8.
- Use type hints for functions and methods.
- Public classes/functions should include clear docstrings.
- Use logging for diagnostics instead of print().

### Organization

- app.py: UI and user interaction.
- processor.py: GTFS processing, data I/O, SQLite access.
- utils/: reusable utilities.
- tests/: mirrors src modules where possible.

### Best practices

- Keep functions small and focused.
- Avoid hidden global state.
- Run expensive operations (I/O, processing) off the UI thread.
- Keep UI visual consistency.

---

## Tests

Run:

```bash
pytest tests/ -v
```

Test guidelines:

- Use names in the format test_<module>_<behavior>.
- Cover success and failure scenarios.
- For GTFS-dependent tests, add minimal fixtures under tests/fixtures/.
- Avoid direct GUI testing in pytest. Focus on processor and utils.

---

## Build the Executable

To validate your changes in distributable format:

```bash
pip install pyinstaller
pyinstaller app.spec
```

The generated executable will be available in dist/.

---

## Reporting Bugs

When opening a bug issue, include:

1. Python version and OS.
2. Steps to reproduce.
3. Expected behavior versus observed behavior.
4. Error logs, if available.
5. GTFS sample file used, if shareable.

---

## Feature Requests

Open an issue tagged enhancement and include:

1. The problem to solve.
2. Proposed solution.
3. Alternatives considered.

---

## License

By contributing, you agree that your contributions are licensed under [GNU GPL v3](LICENSE), the same project license.

Thank you for contributing.
