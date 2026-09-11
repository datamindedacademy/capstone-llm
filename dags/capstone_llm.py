import os
from datetime import datetime

from airflow import DAG
from airflow.providers.docker.operators.docker import DockerOperator

# build the image first: docker build -t capstone-llm:latest .
IMAGE = os.environ.get("CAPSTONE_IMAGE", "capstone-llm:latest")
USER = os.environ.get("CAPSTONE_USER", "change-me")

with DAG(
    "capstone_llm",
    description="clean the stackoverflow data for one tag",
    start_date=datetime(2026, 1, 1),
    schedule=None,
    catchup=False,
    params={"tag": "python-polars"},
) as dag:
    DockerOperator(
        task_id="clean",
        image=IMAGE,
        command=[
            "python3", "-m", "capstonellm.tasks.clean",
            "-e", "docker",
            "-t", "{{ params.tag }}",
            "-u", USER,
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
