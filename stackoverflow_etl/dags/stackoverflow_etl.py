from airflow import DAG
from conveyor.operators import ConveyorSparkSubmitOperatorV2, ConveyorContainerOperatorV2
from datetime import timedelta
from airflow.utils import dates


default_args = {
    "owner": "Conveyor",
    "depends_on_past": False,
    "start_date": dates.days_ago(2),
    "email": [],
    "email_on_failure": False,
    "email_on_retry": False,
    "retries": 0,
    "retry_delay": timedelta(minutes=5),
}


dag = DAG(
    "stackoverflow_etl",
    default_args=default_args,
    schedule_interval="@daily",
    max_active_runs=1,
)

ingest_task = ConveyorContainerOperatorV2(
    dag=dag,
    task_id="ingest",
    instance_type="mx.small",
    aws_role="capstone_conveyor_llm",
    cmds=["python3", "-m", "stackoverflowetl.tasks.ingest"],
    arguments=[],
)

clean_task = ConveyorSparkSubmitOperatorV2(
    dag=dag,
    task_id="clean",
    num_executors="1",
    driver_instance_type="mx.small",
    executor_instance_type="mx.small",
    aws_role="capstone_conveyor_llm",
    spark_main_version=3,
    application="local:///opt/spark/work-dir/src/stackoverflowetl/tasks/clean.py",
    application_args=["--env", "{{ macros.conveyor.env() }}"],
)

ingest_task >> clean_task