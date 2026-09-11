FROM python:3.11-slim

RUN pip install --no-cache-dir dbt-duckdb==1.11.0

COPY dbt/ /app/dbt/
WORKDIR /app/dbt
ENV DBT_PROFILES_DIR=/app/dbt

ENTRYPOINT ["dbt"]
