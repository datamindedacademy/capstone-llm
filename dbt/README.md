# Spike: duckdb + dbt

Does the Task 1 cleaning job work without PySpark, and in a shape a Bedrock
knowledge base actually wants? Yes.

Run it:

```bash
uv sync
cd dbt
DBT_PROFILES_DIR=. dbt run --vars '{tag: airflow, destination: "s3://dataminded-academy-capstone-llm-data/cleaned/<user>/airflow"}'
```

DuckDB reads the input straight from S3 with `httpfs` and picks up your
credentials through `credential_chain`, so no `AWS_ACCESS_KEY_ID` export and
no S3A jar juggling.

## What it writes

One `qa.csv` per topic, plus a `qa.csv.metadata.json` sidecar. The model
unnests `items` from questions.json and answers.json, joins on `question_id`,
keeps one answer per question (accepted first, then score, then answer_id),
and concatenates title, question and answer into a single `content` column.
96 questions in the airflow tag, 70 after the join, the other 26 have no
answers.

## Why CSV and not one json per question

Bedrock parses a CSV row by row when the sidecar declares
`RECORD_BASED_STRUCTURE_METADATA`, so each row becomes its own document with
`question_id`, `link` and `answer_id` as filterable metadata. Tested against
the capstone knowledge base (QMYKW2Q5PH, eu-west-1), both shapes retrieve the
same Q&A at about the same score, but:

- the CSV chunk is clean text, the json chunk carries its own `{"question_id":
  ...}` envelope into the vector
- the CSV chunk returns `question_id` and `link` as attributes you can filter
  and cite, the json chunk returns none
- writing is one COPY (0.95s) instead of one COPY per question (13s for 70
  files, and about 7 minutes for the 1000-question apache-spark tag), because
  DuckDB cannot combine `PARTITION_BY` with `FORMAT JSON`

The sidecar is what buys the row-based treatment. Without it the CSV still
ingests, but as a single document chunked by size, so question boundaries and
metadata are lost.

`tests/test_clean.py` asserts one .json per question with six keys, so this
branch fails that test by design. That is a course-material decision, not a
code one.

The knowledge base crawls the whole bucket with no inclusion prefix and syncs
about every 10 minutes, so it indexes the raw `input/**` files alongside
anything under `cleaned/`.
