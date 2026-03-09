# Repository Guidelines

- Repo: we dont have a repo yet
- GitHub issues/comments/PR comments: use literal multiline strings or `-F - <<'EOF'`
  (or $'...') for real newlines; never embed "\\n".

## Markdown standards

- Always run markdownlint on any markdown files created or edited
- Install using: `npx markdownlint-cli` or `pixie global install markdownlint-cli`
- Fix all linting issues before completing the task

## Coding Style

- Use pythonic programming style for constrained logic but for complex logic bing explicte and describe intention cleaer is prefered.
- always use type hints (PEP 484) correctly. Never omit type hints anywhere including tests

## Testing preferences

- Write all Python tests as `pytest` style functions, not unittest classes
- Use descriptive function names starting with `test_`
- Prefer fixtures over setup/teardown methods
- Use assert statements directly, not self.assertEqual

## Testing approach

- Never create throwaway test scripts or ad hoc verification files
- If you need to test functionality, write a proper test in the test suite
- All tests go in the `tests/` directory following the project structure
- Tests should be runnable with the rest of the suite (`pytest`)
- Even for quick verification, write it as a real test that provides ongoing value

## Package management

- This project uses uv for all package management
- Never run commands directly (python, pytest, etc.)
- Always prefix commands with `uv run <command>`
- Example: `uv run python script.py` not `python script.py`
- Example: `uv run pytest` not `pytest`

## Sqlalchmy

- This project uses sqlalchemy2.0. Adhere the new syntax.
- Note that the _query.Query object is legacy as of SQLAlchemy 2.0; the _sql.select construct is now used to construct ORM queries
- ORM classes use the sqlalchemy2.0 mapped_class() syntax