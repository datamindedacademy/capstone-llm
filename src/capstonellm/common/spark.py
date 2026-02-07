import logging

from pyspark.sql import SparkSession


class ClosableSparkSession:
    def __init__(
        self,
        app_name: str,
        master: str = None,
        spark_config: dict = None,
    ):
        self._app_name = app_name
        self._master = master
        self._spark_config = spark_config or {}
        self._spark_session = None

    def __enter__(self):
        spark_builder = SparkSession.builder.appName(self._app_name)

        if self._master:
            spark_builder = spark_builder.master(self._master)

        spark_builder.config("spark.sql.sources.partitionOverwriteMode", "dynamic")

        for key, val in self._spark_config.items():
            spark_builder.config(key, val)

        self._spark_session = spark_builder.getOrCreate()
        return self._spark_session

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_tb:
            logging.error(exc_tb)
        if self._spark_session:
            self._spark_session.stop()
