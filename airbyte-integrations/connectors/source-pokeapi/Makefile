all: check

format-ruff:
	poetry run ruff --fix .

format-black:
	poetry run black .

lint-black:
	poetry run black . --check

lint-ruff:
	poetry run ruff .

lint-mypy:
	poetry run mypy src tests || true

format: format-ruff format-black

lint: lint-mypy lint-ruff lint-black

test:
	poetry run pytest

check: lint test
