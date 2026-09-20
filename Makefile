.PHONY: setup test lint format ingest transform quality anomalies index api frontend demo clean

setup:
	pip install -r requirements.txt || true
	# Setup script placeholder

test:
	pytest tests/

lint:
	flake8 .
	black --check .

format:
	black .

ingest:
	python scripts/ingest.py

transform:
	python pipelines/process_bronze_silver.py
	python pipelines/process_silver_gold.py

quality:
	python quality/run_checks.py

anomalies:
	python anomaly/detect.py

index:
	python rag/index_knowledge.py

api:
	uvicorn apps.api.main:app --reload

frontend:
	cd apps/web && npm start

demo:
	python scripts/demo.py

clean:
	rm -rf data/raw/* data/bronze/* data/silver/* data/gold/*
