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

To get started We've set up a Gitpod environment containing all the tools required to complete this exercise (awscli, python, vscode, ...). 
You can access this environment by clicking the button below:

[![Open in Gitpod](https://gitpod.io/button/open-in-gitpod.svg)](https://gitpod.io/#https://github.com/SamrtCookie/capstone-llm)

NOTE: When you fork the code repo to your own remote make sure to change the Gitpod URL to reflect your account in this README!

## Gitpod environment
This is an ubuntu-based environment pre-installed with:

- VSCode
- A Python3 virtual environment: we recommend you always work inside this environment.
- The AWS CLI

IMPORTANT: Create a new branch and periodically push your work to the remote. 
After 30min of inactivity this environment shuts down and you will likely lose unsaved progress. 
As stated before, change the Gitpod URL to reflect your remote.

## Project setup

In this repository we prepared the scaffolding for a basic python project.
Best is to use the scaffolding as is, as that will make sure you quickly get something up and running.

### Scaffolding structure

```bash
root/
   | capstone_llm
      |-- src/
      |   |-- project/
      |   |-- |-- common/
      |   |-- |-- |-- spark.py
      |   |-- |-- tasks/
      |-- tests/
      |   |-- common/
      |   |-- | -- spark.py
      |   Dockerfile
      |   setup.py
   | .gitpod.yml
   | .gitpod.dockerfile
   | docker-compose.yaml
```

## Task 1: Transform and load the stackoverflow data

### Context
Our team already ingested questions and answers from StackOverflow for you to use. 
We used the [stackoverflow API](https://api.stackexchange.com/docs).
We ingested different tags, pick one of them with your table (3-4 peopla) as a starting point for cleaning your data.
This helps to distribute who is working on which data.

The input data is stored in the following s3 bucket: `dataminded-academy-capstone-llm-data-us` under path `input/{tag}/`
The S3 bucket resides in us-east-1 region.

### Your task

Start from the input data for 1 tag, the goal is to create 1 text document per question containing the title, question body and the response body.
So your goal is to extract the relevant fields from both the questions and answers and join them together using the `question_id` field.

Write the json documents per question again to s3 under path `cleaned/{tag}`

If you are confident in your code, the next step is scheduling it using Airflow

## How to run your project

The following commands are assumed to run in the `capstone_llm` subdirectory.
- create a virtualenv: `python3 -m venv venv`
- using dependencies: 
  - add the dependencies to the requirements.in
  - generate correct versions + transitive dependencies using: `pip-compile requirements.in`
  - install the dependencies in your virtual environment using `pip install -r requirements.txt`
  - note: the provided dockerfile already packages pyspark 3.5.1, so you only need to specify this in your dev-requirements.in. 
    This way you have spark available when running locally, but it is not packaged twice when running in Docker.
- 2 places to write your transformation logic:
  - clean.py: your pyspark cleaning code
  - ingest.py: see task 3bis (only if you have time left)
- run the tasks
  - install the project in your venv directory as follows: `pip install -e .`
  - run a task: `python3 -m capstonellm.tasks.clean` or `python3 -m capstonellm.tasks.ingest`

## Task 2: schedule your task using Airflow

As you know have working python code. We now want to make sure this is triggered using Airflow.
We start with a local installation of Airflow, you can use the `docker-compose.yml` file, similar to the setup used in the Airflow session.

### Your task
- package the python code in a Dockerfile. If you used the provided scaffolding, this should be easy. Take a look at the Dockerfile and make sure you understand everything
- create an Airflow dag with one task (clean) that will run your clean job using the [DockerOperator](https://airflow.apache.org/docs/apache-airflow/1.10.9/_api/airflow/operators/docker_operator/index.html).
  In order to access s3, you will have to pass your credentials to the docker container.

## Task 3: Test out the basic llm

The next step is to start using your prepared data in the llm.
Before feeding the data, let's test the performance of the current model by asking it some questions:

```
curl --location 'https://kfkjc4ha7crhz6s3uat54wtj6m0bgtdf.lambda-url.eu-west-1.on.aws' \
--header 'Content-Type: application/json' \
--data '{
    "query":"What is the equivalent of `DataFrame.drop_duplicates()` from pandas in polars?"
}'
```

### Your task

Go to the knowledge base and reprocess the input data again.
See if now the model returns more accurate results. Try for example the exact question that fits in your input data?

## Task 3bis: Ingest the stackoverflow data
NOTE: This is an optional task, if you still have time.

The goal here is to create the input data yourself instead of relying on the data that we have provided.
In order to do this you will have to investigate the [Stackoverflow API](https://api.stackexchange.com/docs).
You should call the API and fetch the questions and answers separately, which can be done as follows:
- Query the questions given 1 or more specified tags
- Using the question ids from the previous step, look for the relevant answers

As a best practice this raw data is not preprocessed/cleaned but dumped as is in the s3 bucket under path `/input/{user}/{tag}`.
The processing and cleaning, you already did in the cleaning step. This way if you made a mistake while cleaning, you can start again from the raw data without calling the API again.

## Task 4: deploy to Conveyor
Now that we have verified all our code locally, it is now time to deploy it to production environment. 
In our case this will be Conveyor.

- login to Conveyor
- create a Conveyor project with the following name: `capstone-llm-{user}` from the `capstone_llm` subfolder.
- create a dags folder in `capstone_llm` subfolder and migrate your local dags to Conveyor by using the [ConveyorContainerOperatorV2](https://docs.conveyordata.com/technical-reference/airflow/operators/conveyor-container-operator-v2) and the [ConveyorSparkSubmitOperatorV2](https://docs.conveyordata.com/technical-reference/airflow/operators/conveyor-spark-submit-operator-v2)
  - instead of using the AWS credentials directly, you should attach the `capstone_conveyor_llm` role when running your tasks.  
- build and deploy your project

## Useful commands
Setup virtual environment:
- `pyenv local` to use a correct python version
- `python -m venv venv` to create a virtual environment
- `source ./venv/bin/activate` to activate the virtual environment
- `pip install pip-tools` to install pip tools

Tasks:
- `pip install -r requirements.txt` to install dependencies
- `pip install -r dev-requirements.txt` to install development dependencies
- `pip install -e .` to install the project in editable mode
- `python -m pytest --cov=src tests` runs all the tests and check coverage
- `python -m black dags src tests --check` checks PEP8 compliance issues
- `python -m black dags src tests` fixes PEP8 compliance issues
- `pip-compile requirements.in` if you add new requirements this regenerates a new requirements.txt
- `pip-compile dev-requirements.in` if you add new requirements this regenerates a new dev-requirements.txt, you should also do this when have updated your requirements.in
