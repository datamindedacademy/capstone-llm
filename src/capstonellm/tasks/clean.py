import argparse

import pyspark.sql.functions as f
from pyspark.sql import SparkSession

from capstonellm.common.catalog import llm_bucket
from capstonellm.common.spark import ClosableSparkSession


def clean(spark: SparkSession, tag: str):
    questions = (
        spark.read.json(f"s3a://{llm_bucket}/input/{tag}/questions.json")
        .select(f.explode("items").alias("question"))
        .select("question.*")
        .select(
            "question_id",
            f.col("body").alias("question"),
            "title",
            "link",
        )
    )

    answers = (
        spark.read.json(f"s3a://{llm_bucket}/input/{tag}/answers.json")
        .select(f.explode("items").alias("answer"))
        .select("answer.*")
        .select(
            "question_id",
            "answer_id",
            f.col("body").alias("answer"),
        )
    )

    joined = (
        questions.join(answers, "question_id")
        .withColumn("question_id", f.col("question_id").cast("string"))
        .withColumn("answer_id", f.col("answer_id").cast("string"))
    )

    joined.write.mode("overwrite").json(f"s3a://{llm_bucket}/cleaned/{tag}/")


def main():
    parser = argparse.ArgumentParser(description="stackoverflow_etl")
    parser.add_argument(
        "-e", "--env", dest="env", help="environment we are executing in", default="local"
    )
    parser.add_argument(
        "-t", "--tag", dest="tag", help="the tag to process",
        default="python-polars", required=False
    )

    args = parser.parse_args()
    common_spark_config = {
        "spark.hadoop.fs.s3a.impl": "org.apache.hadoop.fs.s3a.S3AFileSystem",
        "spark.hadoop.fs.s3a.aws.credentials.provider": "software.amazon.awssdk.auth.credentials.DefaultCredentialsProvider",
    }
    if args.env == "local":
        builder = SparkSession.builder.appName("Spark S3 Integration").config(
            "spark.jars.packages", "org.apache.hadoop:hadoop-aws:3.4.2"
        )
        for key, value in common_spark_config.items():
            builder = builder.config(key, value)
        session = builder.getOrCreate()
        clean(session, args.tag)
    else:
        with ClosableSparkSession("stackoverflow_etl", spark_config=common_spark_config) as session:
            clean(session, args.tag)


if __name__ == "__main__":
    main()
