import argparse
import os
from typing import List

import requests
import json
import boto3
import logging
import uuid

from stackoverflowetl.common.catalog import llm_bucket

logger = logging.getLogger(__name__)


def ingest_tag(s3_client, tag: str):
    logger.info(f"Ingesting questions for tag: {tag}")
    url = f"http://api.stackexchange.com/2.3/questions?order=desc&sort=votes&site=stackoverflow&tagged={tag}&pagesize=100&filter=withbody"
    response = requests.request("GET", url)

    if response.status_code != 200:
        logger.error(f"failed to get questions for tag as we received status: {response.status_code}")

    response_json = response.json()

    question_key = f"input/{tag}/questions.json"
    upload_body_s3(response_json, s3_client, question_key)
    validate_enough_quota(response_json)

    question_ids = [
        str(question["question_id"]) for question in response.json()["items"]
    ]

    url = f"http://api.stackexchange.com/2.3/questions/{';'.join(question_ids)}/answers?order=desc&sort=votes&site=stackoverflow&pagesiz=100&filter=withbody"
    response = requests.request("GET", url)

    response_json = response.json()
    answers_key = f"input/{tag}/answers.json"
    upload_body_s3(response_json, s3_client, answers_key)

    validate_enough_quota(response_json)


def upload_body_s3(response_json, s3_client, s3_key):
    filename = f"{str(uuid.uuid4())}.json"

    with open(filename, "w") as f:
        f.write(json.dumps(response_json))
    s3_client.upload_file(
        filename,
        f"{llm_bucket}",
        s3_key,
    )


def validate_enough_quota(response_json):
    remaining_quota = int(response_json["quota_remaining"])
    if remaining_quota < 100:
        logger.error(f"reached the maximum quota limit for the api: {remaining_quota}")
        raise Exception(f"reached the maximum quota limit for the day")
    else:
        logger.info(f"Remaining quota: {remaining_quota}")
        print(f"Remaining quota: {remaining_quota}")


def ingest(tags: List[str]):
    os.environ["DEFAULT_AWS_REGION"] = "us-east-1"
    s3_client = boto3.client("s3", region_name="us-east-1")
    for tag in tags:
        ingest_tag(s3_client, tag)


def main():
    parser = argparse.ArgumentParser(description="stackoverflow ingest")
    parser.add_argument(
        "-t", "--tags", dest="tags", help="comma seperated list if stackoverflow tasks to process",
        default="python-polars,sql,dbt,airflow,apache-spark,docker,pyspark", required=False
    )
    args = parser.parse_args()

    tags_list = args.tags.replace(" ", "").split(",")

    ingest(tags_list)


if __name__ == "__main__":
    main()
