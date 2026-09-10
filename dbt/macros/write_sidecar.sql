{% macro write_sidecar(csv_path, tag) %}
  {#- Tells Bedrock to treat each CSV row as its own document. -#}
  {% if execute %}
    {% do run_query(
      "COPY (select json_object('tag', '" ~ tag ~ "') as metadataAttributes,"
      ~ " json_object("
      ~ "   'type', 'RECORD_BASED_STRUCTURE_METADATA',"
      ~ "   'recordBasedStructureMetadata', json_object("
      ~ "     'contentFields', json_array(json_object('fieldName', 'content')),"
      ~ "     'metadataFieldsSpecification', json_object("
      ~ "       'fieldsToInclude', json_array("
      ~ "         json_object('fieldName', 'question_id'),"
      ~ "         json_object('fieldName', 'link'),"
      ~ "         json_object('fieldName', 'answer_id')))))"
      ~ " as documentStructureConfiguration"
      ~ ") TO '" ~ csv_path ~ ".metadata.json' (FORMAT JSON, ARRAY false)"
    ) %}
    {{ log("wrote " ~ csv_path ~ ".metadata.json", info=True) }}
  {% endif %}
{% endmacro %}
