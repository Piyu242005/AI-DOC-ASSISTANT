.PHONY: format lint test run

format:
	black .
	isort .

lint:
	flake8 .

test:
	pytest

run:
	streamlit run app.py
