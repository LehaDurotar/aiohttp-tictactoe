start:
	PYTHONPATH=$(shell pwd):${PYTHONPATH} poetry run python server/main.py

refactor:
	poetry run black ./
	poetry run isort ./

migrate:
	PYTHONPATH=$(shell pwd):${PYTHONPATH} poetry run alembic upgrade head

lint:
	poetry run black --check ./
	poetry run isort --check-only ./

tests:
	PYTHONPATH=$(shell pwd):${PYTHONPATH} poetry run python -m pytest -v --disable-warnings