{# {schema}.{name} may not exists in the data store yet, check if it's there #}
{%- set source_relation = adapter.get_relation(
      database=source('{schema}', '{name}').database,
      schema=source('{schema}', '{name}').schema,
      identifier=source('{schema}', '{name}').name) -%}

{% set table_exists=source_relation is not none   %}

{% if table_exists %}

select
    *
from {{ source('{schema}', '{name}') }}

{% else %}

select
    *
from {{ ref('{alternative}') }}
where false
{% endif %}
