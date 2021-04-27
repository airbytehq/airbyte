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
