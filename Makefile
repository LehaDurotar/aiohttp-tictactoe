start:
	poetry run python server/main.py

refactor:
	poetry run black ./
	poetry run isort ./

lint:
	poetry run black --check ./
	poetry run isort --check-only ./

tests:
	poetry run python -m pytest -v --disable-warnings