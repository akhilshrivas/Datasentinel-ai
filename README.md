# DataSentinel AI — Agentic Data Reliability & Analytics Platform

## Project Overview
DataSentinel AI is a production-grade data platform demonstrating a complete Bronze/Silver/Gold architecture, data quality enforcement, anomaly detection, and an AI Agent capable of querying data and investigating pipeline incidents. Designed around Azure for Students free-tier services, the core application can also run entirely locally with zero paid API dependencies.

## Business Problem
Modern data platforms suffer from silent data failures, schema drift, and unexplainable metrics. When dashboards break, data engineers spend hours manually querying raw tables, checking pipeline logs, and digging through runbooks. 

DataSentinel AI solves this by:
1. Guaranteeing data quality with explicit contracts.
2. Automatically detecting anomalies in metrics.
3. Providing an AI agent to investigate failures and answer business questions via a read-only SQL tool and local RAG over documentation.

## Architecture
See `docs/architecture/ADR-001-storage-architecture.md` and related documents.

## Local Setup
1. Clone the repository.
2. Copy `.env.example` to `.env`.
3. Run `make setup`.
4. Run `make demo` for a full end-to-end flow.

## Demo Scenario
The `make demo` command orchestrates the complete flow: generating sample data, ingesting it, applying quality checks, calculating metrics, and triggering the AI assistant to analyze a simulated failure.
