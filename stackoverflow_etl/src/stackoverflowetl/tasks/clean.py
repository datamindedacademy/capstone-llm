import argparse

from pyspark.sql.dataframe import DataFrame
import pyspark.sql.functions as f
from pyspark.sql import SparkSession

from stackoverflowetl.common.catalog import llm_bucket
from stackoverflowetl.common.spark import ClosableSparkSession


def clean(spark: SparkSession, environment: str, tag: str):
    questions = spark.read.json(
        f"s3a://{llm_bucket}/input/{tag}/questions.json"
    )

    df = questions.withColumn("question", f.explode("items"))
    df = df.select("question.*")
    df = df.select("question_id", "body", "title", "link").withColumnRenamed(
        "body", "question"
    )
    df.show()

    answers = spark.read.json(
        f"s3a://{llm_bucket}/input/{tag}/answers.json"
    )

    dfa = answers.withColumn("answer", f.explode("items"))
    dfa = dfa.select("answer.*")
    dfa = dfa.select("question_id", "answer_id", "body").withColumnRenamed(
        "body", "answer"
    )

    joined = df.join(dfa, "question_id")
    joined = joined.withColumn("question_id", f.col("question_id").cast("string"))
    joined = joined.withColumn("answer_id", f.col("answer_id").cast("string"))

    count = joined.count()
    joined.repartition(count).write.mode("overwrite").json(
        f"s3a://{llm_bucket}/cleaned/{tag}/"
    )


def main():
    parser = argparse.ArgumentParser(description="stackoverflow_etl")
    parser.add_argument(
        "-e", "--env", dest="env", help="environment we are executing in", required=True
    )
    parser.add_argument(
        "-t", "--tag", dest="tag", help="the tag to process",
        default="python-polars", required=False
    )

    args = parser.parse_args()
    common_spark_config = {
        "spark.hadoop.fs.s3a.impl": "org.apache.hadoop.fs.s3a.S3AFileSystem",
        "spark.hadoop.fs.s3a.aws.credentials.provider": "com.amazonaws.auth.DefaultAWSCredentialsProviderChain",
    }
    if args.env == "local":
        session = (
            SparkSession.builder.appName("Spark S3 Integration")
            .config("spark.jars.packages", "org.apache.hadoop:hadoop-aws:3.3.4")
            .getOrCreate()
        )
        clean(session, args.env, args.tag)
    else:
        with ClosableSparkSession("stackoverflow_etl", spark_config=common_spark_config) as session:
            clean(session, args.env, args.tag)


if __name__ == "__main__":
    main()
