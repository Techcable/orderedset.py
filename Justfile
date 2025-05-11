test: mypy _check && check-format
    # Testing project
    @just _test

# Run test just on the current python version
test-single:
    # Test on current python version
    uv run pytest

check: mypy _check && check-format

# runs additional checks
_check:
    -ruff check src

fix: && format
    ruff check --fix src

build: mypy && _test check-format
    # Build project
    uv build

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

# Checks for formatting issues
check-format:
    @# Invoking ruff directly instead of through uv tool run saves ~12ms per command,
    @# reducing format --check src time from ~20ms to ~8ms.
    @# it reduces time for `ruff --version` from ~16ms to ~3ms.
    @# Running through `uv tool run` also frequently requires refresh of
    @# project dependencies, which can add an additional 100+ ms
    ruff format --check .
    ruff check --select I --output-format concise .

format:
    ruff format .
    ruff check --select 'I' --fix .
