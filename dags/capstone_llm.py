import os
from datetime import datetime

from airflow import DAG
from airflow.providers.docker.operators.docker import DockerOperator

# build the image first: docker build -t capstone-llm-dbt:latest .
IMAGE = os.environ.get("CAPSTONE_IMAGE", "capstone-llm-dbt:latest")
USER = os.environ.get("CAPSTONE_USER", "change-me")
BUCKET = "dataminded-academy-capstone-llm-data"

with DAG(
    "capstone_llm",
    description="clean the stackoverflow data for one tag with dbt + duckdb",
    start_date=datetime(2026, 1, 1),
    schedule=None,
    catchup=False,
    params={"tag": "python-polars"},
) as dag:
    DockerOperator(
        task_id="clean",
        image=IMAGE,
        command=[
            "run",
            "--vars",
            "{tag: {{ params.tag }}, destination: 's3://" + BUCKET + "/cleaned/" + USER + "/{{ params.tag }}'}",
        ],
        environment={
            "AWS_ACCESS_KEY_ID": os.environ.get("AWS_ACCESS_KEY_ID", ""),
            "AWS_SECRET_ACCESS_KEY": os.environ.get("AWS_SECRET_ACCESS_KEY", ""),
            "AWS_SESSION_TOKEN": os.environ.get("AWS_SESSION_TOKEN", ""),
            "AWS_REGION": os.environ.get("AWS_REGION", "eu-west-1"),
        },
        docker_url="unix://var/run/docker.sock",
        network_mode="bridge",
        api_version="auto",
        auto_remove="force",
        mount_tmp_dir=False,
    )
