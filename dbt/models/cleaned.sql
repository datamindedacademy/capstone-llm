{{ config(
    materialized='external',
    location=var('destination') ~ '/qa.csv',
    format='csv',
    options={'header': true},
    post_hook="{{ write_sidecar(var('destination') ~ '/qa.csv', var('tag')) }}"
) }}

with questions as (
    select unnest(items) as q
    from read_json('s3://{{ var("bucket") }}/input/{{ var("tag") }}/questions.json')
),
answers as (
    select unnest(items) as a
    from read_json('s3://{{ var("bucket") }}/input/{{ var("tag") }}/answers.json')
)
select
    q.title || chr(10) || chr(10) || q.body || chr(10) || chr(10) || a.body as content,
    q.question_id,
    q.link,
    a.answer_id
from questions
join answers on q.question_id = a.question_id
qualify row_number() over (
    partition by q.question_id
    order by a.is_accepted desc, a.score desc, a.answer_id
) = 1
