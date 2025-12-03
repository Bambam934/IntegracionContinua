.PHONY: install test lint format clean docker-up docker-down

# Instalación
install:
	cd backend && pip install -r requirements.txt

# Tests
test:
	cd backend && pytest tests/ -v --cov=. --cov-report=term-missing

test-coverage:
	cd backend && pytest tests/ --cov=. --cov-report=xml --cov-report=html

# Docker
docker-up:
	docker compose up -d

docker-down:
	docker compose down -v

docker-test:
	docker compose exec api pytest tests/ -v

# CI/CD
ci-local:
	docker compose up -d db
	sleep 5
	cd backend && pytest tests/ --cov=. --cov-report=xml --cov-report=html

# Limpieza
clean:
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	rm -rf backend/.pytest_cache
	rm -rf backend/.coverage
	rm -rf backend/htmlcov
	rm -f backend/coverage.xml
	rm -f backend/junit.xml

# Desarrollo
dev:
	cd backend && uvicorn main:app --reload --host 0.0.0.0 --port 5000