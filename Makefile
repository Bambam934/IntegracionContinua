.PHONY: install test lint format clean docker-up docker-down docker-test

# Instalación
install:
	pip install -r requirements.txt

# Tests
test:
	pytest tests/ -v --cov=. --cov-report=term-missing

test-coverage:
	pytest tests/ --cov=. --cov-report=xml --cov-report=html

# Linting y formateo
lint:
	flake8 .
	isort --check-only .
	black --check .

format:
	isort .
	black .

# Docker
docker-up:
	docker compose up -d

docker-down:
	docker compose down -v

docker-test:
	docker compose exec api pytest tests/ -v

# Limpieza
clean:
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	rm -rf .pytest_cache
	rm -rf .coverage
	rm -rf htmlcov
	rm -f coverage.xml
	rm -f junit.xml

# Desarrollo
dev:
	uvicorn main:app --reload --host 0.0.0.0 --port 5000