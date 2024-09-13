from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.bash import BashOperator
from airflow.operators.empty import EmptyOperator
from conveyor.operators import ConveyorContainerOperatorV2


default_args = {
    "owner": "airflow",
    "description": "Use of the DockerOperator",
    "depend_on_past": False,
    "start_date": datetime(2021, 5, 1),
    "email_on_failure": False,
    "email_on_retry": False,
    "retries": 1,
    "retry_delay": timedelta(minutes=1),
}

with DAG(
    "reza_dag",
    default_args=default_args,
    schedule_interval="5 * * * *",
    catchup=False,
) as dag:
    start_dag = EmptyOperator(task_id="start_dag")

    end_dag = EmptyOperator(task_id="end_dag")

    t1 = BashOperator(task_id="print_current_date", bash_command="date")

    # t2 = DockerOperator(
    #     task_id="clean_data",
    #     image="clean:latest",
    #     container_name="cleaner",
    #     api_version="auto",
    #     auto_remove=True,
    #     environment={
    #     "AWS_ACCESS_KEY_ID": os.getenv("AWS_ACCESS_KEY_ID"),
    #     "AWS_SECRET_ACCESS_KEY": os.getenv("AWS_SECRET_ACCESS_KEY"),
    #     "AWS_SESSION_TOKEN": os.getenv("AWS_SESSION_TOKEN")
    #                 },
    #     command = "python3 -m capstonellm.tasks.clean --env prod",
    #     docker_url="unix://var/run/docker.sock",
    #     network_mode="bridge",
    # )
    t2 = ConveyorContainerOperatorV2(
        task_id="clean_data",
        aws_role="capstone_conveyor_llm",
        instance_type='mx.micro',
    )

    t4 = BashOperator(task_id="print_hello", bash_command='echo "hello world"')

    start_dag >> t1

    t1 >> t2 >> t4

    t4 >> end_dag
