# Contribuindo – GTFS Map Maker

Obrigado pelo interesse em contribuir! Este documento descreve as diretrizes e o fluxo de trabalho para contribuições ao projeto.

---

## 📋 Pré-requisitos

- **Python**: 3.10 ou superior
- **Git**: Controle de versão
- **Sistema Operacional**: Windows (recomendado para testes completos com GUI e PyInstaller)

---

## 🚀 Configuração do Ambiente

1. **Clone o repositório:**
   ```bash
   git clone https://github.com/arrobaraujo/map_maker.git
   cd map_maker
   ```

2. **Crie e ative um ambiente virtual:**
   ```bash
   python -m venv .venv
   .venv\Scripts\activate     # Windows
   # source .venv/bin/activate  # Linux/macOS
   ```

3. **Instale as dependências:**
   ```bash
   pip install -r requirements.txt
   pip install -r requirements-dev.txt
   ```

4. **Execute a aplicação:**
   ```bash
   python src/app.py
   ```

---

## 📂 Estrutura do Projeto

Antes de contribuir, familiarize-se com a arquitetura do projeto lendo o [ARCHITECTURE_PT.md](ARCHITECTURE_PT.md).

```
src/
├── app.py              # Interface gráfica (GUI) – CustomTkinter
├── processor.py        # Motor de processamento GTFS (Pandas + SQLite)
└── utils/
    └── renderer.py     # Renderização de mapas e utilidades geométricas
tests/
└── test_processor.py   # Testes automatizados (pytest)
```

---

## 🔄 Fluxo de Contribuição

### 1. Crie uma branch

Crie uma branch a partir de `main` com um nome descritivo:

```bash
git checkout -b feature/nome-da-feature
git checkout -b fix/descricao-do-bug
git checkout -b docs/descricao-da-mudanca
```

**Convenção de nomes:**
| Prefixo     | Uso                          |
|-------------|------------------------------|
| `feature/`  | Nova funcionalidade          |
| `fix/`      | Correção de bug              |
| `refactor/` | Refatoração (sem mudar comportamento) |
| `docs/`     | Apenas documentação          |
| `test/`     | Adição ou melhoria de testes |

### 2. Desenvolva e teste

- Faça suas alterações seguindo as [diretrizes de código](#-diretrizes-de-código).
- Adicione ou atualize testes quando aplicável.
- Rode os testes antes de enviar:
  ```bash
  pytest tests/ -v
  ```

### 3. Commit e Push

Use mensagens de commit descritivas:

```bash
git add .
git commit -m "feat: adiciona exportação em formato GeoJSON"
git push origin feature/exportacao-geojson
```

**Formato de commits (Conventional Commits):**
| Prefixo     | Uso                                            |
|-------------|------------------------------------------------|
| `feat:`     | Nova funcionalidade                            |
| `fix:`      | Correção de bug                                |
| `refactor:` | Refatoração de código                          |
| `docs:`     | Mudanças na documentação                       |
| `test:`     | Adição ou correção de testes                   |
| `style:`    | Formatação, espaçamento (sem mudança de lógica)|
| `chore:`    | Tarefas de manutenção (deps, configs, CI)      |

### 4. Abra um Pull Request

- Abra um PR para a branch `main`.
- Descreva claramente as mudanças realizadas.
- Inclua capturas de tela se a alteração afetar a interface.
- Referencie issues relacionadas (ex: `Closes #12`).

---

## 📝 Diretrizes de Código

### Estilo

- **PEP 8**: Siga o guia de estilo Python padrão.
- **Type Hints**: Use anotações de tipo em funções e métodos (ex: `def foo(x: int) -> str:`).
- **Docstrings**: Todas as classes e funções públicas devem ter docstrings descritivas.
- **Logging**: Use o módulo `logging` — nunca `print()` para debug.

### Organização

- **GUI** (`app.py`): Toda lógica de interface e interação do usuário.
- **Dados** (`processor.py`): Processamento GTFS, I/O de dados, SQLite.
- **Utilidades** (`utils/`): Funções auxiliares reutilizáveis (renderização, algoritmos).
- **Testes** (`tests/`): Espelham a estrutura de `src/`.

### Boas práticas

- Mantenha funções pequenas e focadas (responsabilidade única).
- Evite dependências globais; passe estado via parâmetros.
- Operações pesadas (I/O, processamento) devem ser executadas em threads separadas para não bloquear a GUI.
- Ao adicionar widgets na UI, mantenha a consistência visual com o tema Dark existente.

---

## 🧪 Testes

### Executando os testes

```bash
pytest tests/ -v
```

### Diretrizes para testes

- Nomeie testes com o padrão `test_<modulo>_<comportamento>`.
- Teste cenários de sucesso **e** de falha.
- Para testes que precisem de dados GTFS, crie arquivos `.zip` mínimos de amostra em `tests/fixtures/`.
- A GUI não deve ser testada diretamente via pytest; foque nos módulos `processor` e `utils`.

---

## 📦 Gerando o Executável

Para verificar se suas alterações funcionam no formato distribuível:

```bash
pip install pyinstaller
python -m PyInstaller --noconsole --onefile \
    --add-data ".venv/Lib/site-packages/customtkinter;customtkinter/" \
    src/app.py
```

O executável será gerado em `dist/app.exe`.

---

## 🐛 Reportando Bugs

Ao abrir uma issue de bug, inclua:

1. **Versão do Python** e **sistema operacional**.
2. **Passos para reproduzir** o problema.
3. **Comportamento esperado** vs **comportamento observado**.
4. **Logs de erro** (se disponíveis).
5. **Arquivo GTFS usado** (se possível e não confidencial).

---

## 💡 Sugerindo Funcionalidades

Abra uma issue com a tag `enhancement` e descreva:

1. **O problema** que a funcionalidade resolve.
2. **A solução proposta** (com detalhes técnicos, se possível).
3. **Alternativas consideradas**.

---

## 📜 Licença

Ao contribuir, você concorda que suas contribuições serão licenciadas sob a [GNU GPL v3](LICENSE), a mesma licença do projeto.

---

Agradecemos sua contribuição! 🎉
