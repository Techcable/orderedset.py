test: mypy _lint && check-format
    # Testing project
    @just _test

# Run test just on the current python version
test-single:
    # Test on current python version
    uv run pytest

check: mypy lint

# runs lints, but not type checking or tests
#
# Avoids performance penalty of `mypy`
lint: _lint && check-format

_lint:
    -ruff check src

fix: && _format fix-spelling
    @# Failure to fix should not prevent formatting
    -ruff check --fix src

build: mypy && doc _test check-format
    # Build project
    uv build

# build project documentation with `pdoc`
#
# See website: https://pdoc.dev/
doc:
    @mkdir -p docs
    PYTHONPATH=src ./pdoc/.venv/bin/pdoc --docformat=markdown -o docs techcable.orderedset

mypy:
    uv run mypy src

# runs tests without anything else
_test: test-single
    @just _test_ver 3.13
    @just _test_ver 3.12
    @just _test_ver 3.11
    @just _test_ver 3.10
    @just _test_ver 3.9


# runs python tests for a specific version
_test_ver pyver:
    # running tests for python {{pyver}}
    @# NOTE: Using `uv` is vastly faster than using `tox`
    @# Using --isolated avoids clobbering dev environment
    @uv run --isolated --python {{pyver}} --only-group test pytest --quiet

# Check for spelling issues
spellcheck:
    # Check for obvious spelling issues
    typos

# Fix obvious spelling issues
fix-spelling:
    # Fix obvious spelling issues
    typos --write-changes

# taplo logging is excessively verbose (prints 'file detection' but not files changed)
export RUST_LOG := "taplo=warn"

# Checks for formatting issues
check-format: && spellcheck
    @# Invoking ruff directly instead of through uv tool run saves ~12ms per command,
    @# reducing format --check src time from ~20ms to ~8ms.
    @# it reduces time for `ruff --version` from ~16ms to ~3ms.
    @# Running through `uv tool run` also frequently requires refresh of
    @# project dependencies, which can add an additional 100+ ms
    ruff format --check .
    ruff check --select I --output-format concise .
    # check toml formatting
    uvx taplo format --check

format: _format && spellcheck

_format:
    ruff format .
    ruff check --select 'I' --fix .
    # format toml
    uvx taplo format
