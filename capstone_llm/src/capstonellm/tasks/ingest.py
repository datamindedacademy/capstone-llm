import argparse
from pyspark.sql import SparkSession
import logging
logger = logging.getLogger(__name__)

def ingest(tag: str):
    spark = SparkSession.builder.getOrCreate()
    qs_df = spark.read.json("/workspace/capstone-llm/questions.json")
    qs_l = qs_df.select("items").collect()[0][0]


def main():
    parser = argparse.ArgumentParser(description="stackoverflow ingest")
    parser.add_argument(
        "-t", "--tag", dest="tag", help="Tag of the question in stackoverflow to process",
        default="python-polars", required=False
    )
    args = parser.parse_args()
    logger.info("Starting the ingest job")

    ingest(args.tag)


if __name__ == "__main__":
    main()
