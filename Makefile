# Makefile

.PHONY: help setup format lint security

# Show help for each target
help:
	@echo ""
	@echo "Log Parser Makefile Commands:"
	@echo "---------------------------"
	@echo "setup           Install Python tools and Git pre-commit hooks"
	@echo "format          Format code using Black"
	@echo "lint            Run static code analysis using Ruff"
	@echo "security        Scan for security issues using Bandit"
	@echo "test            Run unit and integration tests using pytest"
	@echo "check           Run format, lint, and security checks (all-in-one)"
	@echo ""

# Setup Python tools and Git pre-commit hooks
setup:
	pip3 install --upgrade pip
	pip3 install -r requirements.txt
	python3 -m pre_commit install

# Format code using Black
format:
	python3 -m black parser.py

# Run lint checks
lint:
	python3 -m ruff check --fix parser.py
	python3 -m ruff check --show-files parser.py

# Run security scan
security:
	python3 -m bandit -r parser.py
	python3 -m bandit -r tests/ -s B101

# Run unit and integration tests
test:
	python3 -m pytest tests/unit
	python3 -m pytest tests/integration

# Run full check
check: format lint security test coverage
	@echo "All checks passed successfully!"
