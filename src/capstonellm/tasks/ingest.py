import argparse
import json
import logging
from typing import List

import boto3
import requests

from capstonellm.common.catalog import llm_bucket

logger = logging.getLogger(__name__)

STACKEXCHANGE_API = "http://api.stackexchange.com/2.3"


def fetch_from_stackexchange(path: str, **extra_params) -> dict:
    response = requests.get(
        f"{STACKEXCHANGE_API}/{path}",
        params={
            "order": "desc",
            "sort": "votes",
            "site": "stackoverflow",
            "pagesize": 100,
            "filter": "withbody",
            **extra_params,
        },
    )
    response.raise_for_status()
    data = response.json()
    validate_quota(data)
    return data


def ingest_tag(s3_client, tag: str):
    logger.info(f"Ingesting questions for tag: {tag}")

    questions = fetch_from_stackexchange("questions", tagged=tag)
    question_ids = ";".join(str(q["question_id"]) for q in questions["items"])

    endpoints = {
        "questions": questions,
        "answers": fetch_from_stackexchange(f"questions/{question_ids}/answers"),
    }

    for name, data in endpoints.items():
        upload_json_to_s3(data, s3_client, f"input/{tag}/{name}.json")


def upload_json_to_s3(data: dict, s3_client, s3_key: str):
    s3_client.put_object(
        Bucket=llm_bucket,
        Key=s3_key,
        Body=json.dumps(data),
    )


def validate_quota(response_json: dict):
    remaining = int(response_json["quota_remaining"])
    if remaining < 100:
        raise Exception(f"StackExchange API quota nearly exhausted: {remaining} remaining")
    logger.info(f"Remaining quota: {remaining}")


def ingest(tags: List[str]):
    s3_client = boto3.client("s3", region_name="us-east-1")
    for tag in tags:
        ingest_tag(s3_client, tag)


def main():
    parser = argparse.ArgumentParser(description="stackoverflow ingest")
    parser.add_argument(
        "-t", "--tags", dest="tags",
        help="comma-separated list of stackoverflow tags to process",
        default="python-polars,sql,dbt,airflow,apache-spark,docker,pyspark",
        required=False,
    )
    args = parser.parse_args()
    ingest(args.tags.replace(" ", "").split(","))


if __name__ == "__main__":
    main()
