from airflow import DAG
from datetime import datetime, timedelta
from conveyor.operators import ConveyorSparkSubmitOperatorV2, ConveyorContainerOperatorV2
from datetime import timedelta
from airflow.utils import dates


default_args = {
    "owner": "Conveyor",
    "depends_on_past": False,
    "start_date": datetime.now() - timedelta(days=2),
    "email": [],
    "email_on_failure": False,
    "email_on_retry": False,
    "retries": 0,
    "retry_delay": timedelta(minutes=5),
}


dag = DAG(
    "stackoverflow_etl",
    default_args=default_args,
    schedule="@daily",
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

clean_task = ConveyorContainerOperatorV2(
    dag=dag,
    task_id="clean",
    instance_type="mx.medium",
    aws_role="capstone_conveyor_llm",
    cmds=["python3", "-m", "stackoverflowetl.tasks.clean"],
    arguments=["-e", "{{ macros.conveyor.env() }}"]
)

ingest_task >> clean_task