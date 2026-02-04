# Dataminded Capstone LLM

Welcome to the Capstone project! Everything you've learned over the past days will now be integrated in a realistic data pipeline.
The training wheels are off, but we're still at the sideline, cheering you on and supporting you when needed.

In a nutshell, here's what you will do:

Read, transform and load stackoverflow data from S3 with PySpark and cleaning it such that it can be used by a llm model.
We want to find out if we can improve an existing foundational model by providing it relevant data on specific topics in the form of stackoverflow questions and answers.
Since these foundational models don't always contain the most recent changes, they might provide outdated results.
Your task is thus to improve the llm by feeding it the right data.

You will start by building the code for the ingestion pipeline locally and scheduling it using Airflow.
If this is going well, we will run it on a cloud platform, called [Conveyor](https://conveyordata.com/).

To get started We've set up a GitHub Codespaces environment containing all the tools required to complete this exercise (awscli, python, vscode, ...).
You can access this environment by clicking the button below:

[![Open in GitHub Codespaces](https://github.com/codespaces/badge.svg)](https://codespaces.new/datamindedacademy/capstone-llm)

NOTE: When you fork the code repo to your own remote make sure to change the GitHub Codespaces URL to reflect your account in this README!

## GitHub Codespaces environment

This is an ubuntu-based environment pre-installed with:

- VSCode
- A Python3 virtual environment: we recommend you always work inside this environment.
- The AWS CLI

IMPORTANT: Create a new branch and periodically push your work to the remote.
After 30min of inactivity this environment shuts down and you will likely lose unsaved progress.
As stated before, change the GitHub Codespaces URL to reflect your remote.

## Project setup

In this repository we prepared the scaffolding for a basic python project.
Best is to use the scaffolding as is, as that will make sure you quickly get something up and running.

### Scaffolding structure

```bash
root/
   |-- dags/
   |-- src/
   |   |-- project/
   |   |-- |-- common/
   |   |-- |-- |-- spark.py
   |   |-- |-- tasks/
   |-- tests/
   |   |-- common/
   |   |-- | -- spark.py
   | Dockerfile
   | .codespaces.dockerfile
   | docker-compose.yaml
   | pyproject.toml
```

## AWS access
In order to access the necessary data on s3, you will need to configure your AWS credentials.
You can do this by running `aws configure` and filling in the necessary information.
We will provide you with individual `access_key_id` and `secret_access_key`.
Specify as default region `us-east-1`.

After this you should be able to successfully run the following command:
```bash
aws s3 ls s3://dataminded-academy-capstone-llm-data-us/input/
```

If this works, you are ready to start the project.

## Task 1: Transform and load the stackoverflow data

### Context

Our team already ingested questions and answers from StackOverflow for you to use.
We used the [stackoverflow API](https://api.stackexchange.com/docs).
We ingested different tags, pick one of them as a starting point for cleaning your data.

The input data is stored in the following s3 bucket: `dataminded-academy-capstone-llm-data-us` under path `input/{tag}/`
The S3 bucket resides in us-east-1 region.

### Your task

Investigate the data, you can download and inspect the json files. Download them as follows:

```
aws s3 ls s3://dataminded-academy-capstone-llm-data-us/input/
aws s3 cp s3://dataminded-academy-capstone-llm-data-us/input/dbt/questions.json ./
```

Start by writing your cleaning transformation by reading/writing local files and only afterwards interact directly with s3.

Given the input data for 1 tag, the goal is to create 1 json document per question containing the title, question body and the response body.
So your goal is to extract the relevant fields from both the questions and answers and join them together using the `question_id` field.

> **_NOTE:_** When reading from s3, make sure to use `s3a://` prefix.

> **_NOTE:_** In order for your job to access the s3 bucket, you will need to export the `AWS_ACCESS_KEY_ID` and `AWS_SECRET_ACCESS_KEY` environment variables.

Write the cleaned json documents per question again to s3 under path `cleaned/<user>/{tag}`

If you are confident in your code, the next step is scheduling it using Airflow

## How to run your project

The following commands are assumed to run in the root of your project.

- create a virtualenv: `uv venv`
- using dependencies:
  - add dependencies in pyproject.toml or use `uv add <pacakage>`
  - install the dependencies in your virtual environment using `uv sync`
- 2 places to write your transformation logic:
  - clean.py: your pyspark cleaning code
  - ingest.py: see task 3bis (only if you have time left)
- run the tasks
  - install the project in your venv directory as follows: `uv pip install -e .`
  - run a task: `uv run python3 -m capstonellm.tasks.clean` or `uv run python3 -m capstonellm.tasks.ingest`
  - you can check if your task ran correctly by running `pytest tests/test_clean.py`


## Task 2: schedule your task using Airflow

As you know have working python code. We now want to make sure this is triggered using Airflow.
We start with a local installation of Airflow, you can use the `docker-compose.yml` file, similar to the setup used in the Airflow session.

### Your task

- package the python code in a Dockerfile. If you used the provided scaffolding, this should be easy. Take a look at the Dockerfile and make sure you understand everything
- create an Airflow dag with one task (clean) that will run your clean job using the [DockerOperator](https://airflow.apache.org/docs/apache-airflow/1.10.9/_api/airflow/operators/docker_operator/index.html).
  In order to access s3, you will have to pass your credentials to the docker container.

## Task 3: Ingest the stackoverflow data

NOTE: This is an optional task, if you still have time.

The goal here is to create the input data yourself instead of relying on the data that we have provided.
In order to do this you will have to investigate the [Stackoverflow API](https://api.stackexchange.com/docs).
You should call the API and fetch the questions and answers separately, which can be done as follows:

- Query the questions given 1 or more specified tags
- Using the question ids from the previous step, look for the relevant answers

As a best practice this raw data is not pre-processed/cleaned but dumped as is in the S3 bucket under path `/input/{user}/{tag}`.
The processing and cleaning, you already did in the cleaning step. This way if you made a mistake while cleaning, you can start again from the raw data without calling the API again.

## Task 4: deploy to Conveyor

Now that we have verified all our code locally, it is now time to deploy it to production environment.
In our case this will be Conveyor.

- Login to Conveyor: `conveyor auth login`
- Create a Conveyor project with the following name: `capstone-llm-{user}` from the root directory.
- Tweak the `conveyor_example.py` to run your job using the [ConveyorContainerOperatorV2](https://docs.conveyordata.com/technical-reference/airflow/operators/conveyor-container-operator-v2).
- instead of using the AWS credentials directly, as we did locally, you now attach the `capstone_conveyor_llm` role.
- to test things out you can run: `conveyor run`
- build and deploy your project: `conveyor build && conveyor deploy --env test`

## Useful commands

Setup virtual environment:

- `source ./venv/bin/activate` to activate the virtual environment

Tasks:

- `uv sync` to install the dependencies in a virtual environment
- `uv pip install -e .` to install the current project in your virtual environment
- `docker compose up -d` to start the airflow server
- `uv export --format requirements-txt > equirements.txt` to export the dependencies to a requirements.txt file
- `uv run python3 -m capstonellm.tasks.clean` run clean task locally