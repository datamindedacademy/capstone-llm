import argparse
import logging
from pyspark.sql import SparkSession
from pyspark.sql.functions import explode, col

from capstonellm.common.spark import ClosableSparkSession

logger = logging.getLogger(__name__)

def clean(spark: SparkSession, environment: str, tag: str):

    qs_df = spark.read.json("/workspace/capstone-llm/questions.json")
    qs_df = qs_df.withColumn("items", explode("items"))
    qs_df = qs_df.select(col("items.question_id").alias("question_id")\
    ,col("items.body").alias("qusetion_body")\
        ,col("items.tags").alias("tags")\
            ,col("items.accepted_answer_id").alias("accepted_answer_id")).filter(col("tag") == tag)
    ans_df = spark.read.json("/workspace/capstone-llm/answers.json")
    ans_df = ans_df.withColumn("items", explode("items"))
    ans_df = ans_df.select(col("items.answer_id").alias("answer_id")\
    ,col("items.body").alias("answer_body")\
        ,col("items.question_id").alias("question_id"))
    final_df = qs_df.join(ans_df, on = "answer_id", how = "left")\
        .select(["question_id","answer_id","tags","qusetion_body","answer_body"])
    

def main():
    parser = argparse.ArgumentParser(description="capstone_llm")
    parser.add_argument(
        "-e", "--env", dest="env", help="environment we are executing in", required=True
    )
    parser.add_argument(
        "-t", "--tag", dest="tag", help="the tag to process",
        default="python-polars", required=False
    )
    logger.info("starting the cleaning job")

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
        with ClosableSparkSession("capstone_llm", spark_config=common_spark_config) as session:
            clean(session, args.env, args.tag)


if __name__ == "__main__":
    main()
