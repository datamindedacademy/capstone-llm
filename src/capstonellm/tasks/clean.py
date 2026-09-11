import argparse
import logging

import pyspark.sql.functions as f
from pyspark.sql import SparkSession, Window

from capstonellm.common.catalog import llm_bucket
from capstonellm.common.spark import ClosableSparkSession

logger = logging.getLogger(__name__)


def clean(spark: SparkSession, tag: str, user: str):
    questions = (
        spark.read.json(f"s3a://{llm_bucket}/input/{tag}/questions.json")
        .select(f.explode("items").alias("q"))
        .select(
            "q.question_id",
            f.col("q.body").alias("question"),
            "q.title",
            "q.link",
        )
    )

    answers = (
        spark.read.json(f"s3a://{llm_bucket}/input/{tag}/answers.json")
        .select(f.explode("items").alias("a"))
        .select(
            "a.question_id",
            "a.answer_id",
            f.col("a.body").alias("answer"),
            "a.is_accepted",
            "a.score",
        )
    )

    # one answer per question: accepted first, then score, then oldest
    best_answer = (
        answers.withColumn(
            "rank",
            f.row_number().over(
                Window.partitionBy("question_id").orderBy(
                    f.col("is_accepted").desc(),
                    f.col("score").desc(),
                    f.col("answer_id").asc(),
                )
            ),
        )
        .filter(f.col("rank") == 1)
        .select("question_id", "answer_id", "answer")
    )

    destination = f"s3a://{llm_bucket}/cleaned/{user}/{tag}"
    logger.info(f"writing cleaned questions to {destination}")

    (
        questions.join(best_answer, "question_id")
        .repartition("question_id")
        .write.mode("overwrite")
        .option("maxRecordsPerFile", 1)  # one json document per question
        .json(destination)
    )


def main():
    parser = argparse.ArgumentParser(description="capstone_llm")
    parser.add_argument(
        "-e", "--env", dest="env", help="environment we are executing in", required=False, default="local"
    )
    parser.add_argument(
        "-t", "--tag", dest="tag", help="the tag to process",
        default="python-polars", required=False
    )
    parser.add_argument(
        "-u", "--user", dest="user", help="your name, used as the output prefix",
        required=True
    )
    logger.info("starting the cleaning job")

    args = parser.parse_args()
    common_spark_config = {
        "spark.hadoop.fs.s3a.impl": "org.apache.hadoop.fs.s3a.S3AFileSystem",
        "spark.hadoop.fs.s3a.aws.credentials.provider": "software.amazon.awssdk.auth.credentials.DefaultCredentialsProvider",
    }
    if args.env == "local":
        print("This is a local execution of the capestonellm project")
        builder = SparkSession.builder.appName("Spark S3 Integration").config(
            "spark.jars.packages", "org.apache.hadoop:hadoop-aws:3.4.2"
        )
        for key, value in common_spark_config.items():
            builder = builder.config(key, value)
        session = builder.getOrCreate()
        clean(session, args.tag, args.user)
    else:
        with ClosableSparkSession("capstone_llm", spark_config=common_spark_config) as session:
            clean(session, args.tag, args.user)


if __name__ == "__main__":
    main()
