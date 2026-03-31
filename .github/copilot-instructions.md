# Copilot / Assistant instructions for this repository

Purpose:
- Provide canonical guidance for AI assistants (GitHub Copilot, Copilot-for-Business, or other automated agents) when generating or modifying code in this repository.

Important: This file is an advisory convention for AI assistants and humans. It does not change runtime behavior or engine logic.

---

## Editable by automated tools

- Allowed: repository root skill files (e.g., `gmail_send_skill.py`, `ldr_compat.py`), `tests/` (unit tests), and documentation files (README, Skill.md) in the repository root.
- Disallowed: creating new top-level directories (for automated changes). Do not create `skills/` or other new top-level folders without explicit human approval.
- Disallowed: `config/`, `workflow_params.yaml`, any files under `secrets/`, and any `*_config.yaml` or JSON files that contain credentials.

If an automated change would touch a disallowed file or would create new top-level directories, open an issue and request human review instead of making the change.

## Style & Quality
- Follow existing project style (PEP8 for Python). Prefer adding type hints for public APIs.
- Keep changes minimal and focused; avoid reformatting unrelated files.
- Add/update unit tests for any behavioral change (happy path + 1 edge case if possible).
- If public API changes, update its `mcp_config.json` / `*_config.json` and README.

### Python quality rules

- Code style: follow PEP8. Use an automatic formatter (Black) for consistent formatting where possible.
- Linting: use `ruff` or `flake8` to catch common issues. Autofix where safe (e.g., ruff --fix).
- Typing: prefer adding type annotations for public functions and methods. Run `mypy` (or `ruff --select RUF001` if configured) on changed modules if available.
- Docstrings: public modules, classes and functions should have a short docstring describing purpose, inputs and outputs.
- Tests: add or update unit tests when changing behavior. Aim for at least a minimal test for the changed code (happy path + one edge case).
- Coverage: there is no hard global requirement, but changes to core modules should include tests that exercise new behavior; maintainers may request additional coverage for critical paths.
- Pre-commit checks: if the repository uses pre-commit, ensure new commits pass the configured hooks.
- Commands to run locally before committing changes (recommended):
  - `pytest -q`
  - `ruff . --fix` (or `flake8 .` if ruff is not available)
  - `black . --check` (or `black .` to reformat)
  - `mypy .` (optional, if mypy is used in this repo)

If you prefer different tools (for example `prettier` for non-Python files, or `pyproject`-driven configuration, or stricter `mypy` settings), tell me which and I will add them to this file.

## Tests & Quality Gates
- Run tests (if available) after edits. Preferred commands:
  - `pytest -q` (unit tests)
  - `flake8` or `ruff` for linting (if configured)
- If CI is configured, ensure your change will pass CI before committing.

## Security
- Never write plaintext secrets, API keys, or credentials into the repository.
- Use `workflow_params.yaml` (local-only) for runtime secrets — this file must not be committed.
- If you need secrets for testing, mock them or use test fixtures.

## Commit & PR guidance
- Small, incremental PRs are preferred.
- Include a short description and the motivation for the change.
- If automated edits are produced by Copilot or other assistants, include a one-line note in the PR body: "Automated edits guided by .github/copilot-instructions.md".

## Assistant Hints (for code-generating agents)
- Before editing, read this file and prefer rules here over ad-hoc instructions.
- When modifying code, ensure you also update tests and configuration files that document the behavior.
- When in doubt, create an issue and tag `area:engine` or `area:skills` for human review.
- Avoid large-scale refactors in a single automated change.

---

## Example checklist for skill changes
- [ ] Modify or add code under `skills/<skill_name>/`
- [ ] Update `skills/<skill_name>/mcp_config.json` or `*_config.json` if inputs/outputs changed
- [ ] Add or update tests under `tests/`
- [ ] Run tests locally and ensure green
- [ ] Add entry to `MODIFICATION_SUMMARY.md` describing the intent and risk

---

## Example checklist for changes in this repository
- [ ] Modify or add code in repository root skill files (e.g., `gmail_check_skill.py` or `ldr_compat.py`)
- [ ] Update `mcp_config.json` / `*_config.json` in the repository root if inputs/outputs changed
- [ ] Add or update tests under the top-level `tests/` (or update existing repo-root tests)
- [ ] Run tests locally using the repository venv (`.venv/bin/python -m pytest -q`) and ensure green
- [ ] Add an entry to `MODIFICATION_SUMMARY.md` (repo root) describing the intent and risk


If you want stricter rules (for example: only allow automated changes in a `sandbox/` branch), say so and I can update this file accordingly.

## Using the project's virtual environment (recommended)

This repository includes a Python virtual environment under `.venv` (created by the project maintainer).
All contributors and automated tools should use that environment when running tests or installing Python dependencies to ensure a consistent runtime.

Recommended zsh commands:

```bash
# Activate the venv for the current shell
source .venv/bin/activate

# Install project dependencies (if needed)
pip install -r requirements.txt

# Run the test suite
python -m pytest -q
```

Automation notes for assistants:
- When running commands programmatically, use the venv Python executable directly: `.venv/bin/python -m pytest -q`.
- Avoid installing global packages; prefer `pip install --user` only when the venv is not available.
