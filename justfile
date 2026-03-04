# Default recipe
default: sync

# Show available recipes
help:
    @just --list

# Sync dependencies for all workspace packages
sync:
    uv sync

# Auto-format all packages
format:
    @echo "==> Formatting all packages"
    uv run ruff check --fix
    uv run ruff format

# Run linting and type checks for all packages
check:
    @echo "==> Checking all packages (ruff + pyright)"
    uv run ruff check
    uv run ruff format --check
    uv run pyright

# Run all tests
test:
    @echo "==> Running all tests"
    uv run pytest

# Format a specific package
format-pkg pkg:
    @echo "==> Formatting {{pkg}}"
    uv run --project packages/{{pkg}} --directory packages/{{pkg}} ruff check --fix
    uv run --project packages/{{pkg}} --directory packages/{{pkg}} ruff format

# Check a specific package
check-pkg pkg:
    @echo "==> Checking {{pkg}} (ruff + pyright)"
    uv run --project packages/{{pkg}} --directory packages/{{pkg}} ruff check
    uv run --project packages/{{pkg}} --directory packages/{{pkg}} ruff format --check
    uv run --project packages/{{pkg}} --directory packages/{{pkg}} pyright

# Test a specific package
test-pkg pkg:
    @echo "==> Testing {{pkg}}"
    uv run --project packages/{{pkg}} --directory packages/{{pkg}} pytest tests -vv

# Build all packages
build:
    @echo "==> Building all packages"
    uv build --package kai --no-sources --out-dir dist/kai
    uv build --package kagent --no-sources --out-dir dist/kagent
    uv build --package kcastle --no-sources --out-dir dist/kcastle
    uv build --package kcode --no-sources --out-dir dist/kcode

# Clean build artifacts
clean:
    rm -rf dist .ruff_cache .pytest_cache
    find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true

# Find unused code with vulture
vulture:
    @echo "==> Running vulture"
    prek run vulture --all-files --hook-stage manual
