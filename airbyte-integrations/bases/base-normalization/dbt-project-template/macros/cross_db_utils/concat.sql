{#
    Overriding the following macro from dbt-utils:
        https://github.com/fishtown-analytics/dbt-utils/blob/0.6.2/macros/cross_db_utils/concat.sql
    To implement our own version of concat
    Because on postgres, we cannot pass more than 100 arguments to a function
    This is necessary until: https://github.com/fishtown-analytics/dbt-utils/blob/dev/0.7.0/macros/cross_db_utils/concat.sql
    is released.
#}

{% macro concat(fields) -%}
  {{ adapter.dispatch('concat', packages = ['airbyte_utils', 'dbt_utils'])(fields) }}
{%- endmacro %}

{% macro postgres__concat(fields) %}
    {{ dbt_utils.alternative_concat(fields) }}
{% endmacro %}

{% macro sqlserver__concat(fields) -%}
    {#-- CONCAT() in SQL SERVER accepts from 2 to 254 arguments, we use batches for the main concat, to overcome the limit. --#}
    {% set concat_chunks = [] %}
    {% for chunk in fields|batch(253) -%}
        {% set _ = concat_chunks.append( "concat(" ~ chunk|join(', ') ~ ",'')" ) %}
    {% endfor %}

    concat({{ concat_chunks|join(', ') }}, '')
{%- endmacro %}
