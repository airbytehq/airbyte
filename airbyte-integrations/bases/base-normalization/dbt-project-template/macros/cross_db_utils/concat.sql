{#
    concat in dbt 0.6.4 used to work fine for bigquery but the new implementaion in 0.7.3 is less scalable (can not handle too many columns)
    Therefore, we revert the implementation here and add versions for missing destinations
#}

{% macro concat(fields) -%}
  {{ adapter.dispatch('concat')(fields) }}
{%- endmacro %}

{% macro bigquery__concat(fields) -%}
    {#-- concat() in SQL bigquery scales better with number of columns than using the '||' operator --#}
    concat({{ fields|join(', ') }})
{%- endmacro %}

{% macro sqlserver__concat(fields) -%}
    {#-- CONCAT() in SQL SERVER accepts from 2 to 254 arguments, we use batches for the main concat, to overcome the limit. --#}
    {% set concat_chunks = [] %}
    {% for chunk in fields|batch(253) -%}
        {% set _ = concat_chunks.append( "concat(" ~ chunk|join(', ') ~ ",'')" ) %}
    {% endfor %}

    concat({{ concat_chunks|join(', ') }}, '')
{%- endmacro %}
