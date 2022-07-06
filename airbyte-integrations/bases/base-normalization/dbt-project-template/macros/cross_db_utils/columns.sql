{% macro redshift__alter_column_type(relation, column_name, new_column_type) -%}

  {%- set tmp_column = column_name + "__dbt_alter" -%}

  {% call statement('alter_column_type') %}
    alter table {{ relation }} add column {{ adapter.quote(tmp_column) }} {{ new_column_type }};
    {% if new_column_type.lower() == "super" %}
        update {{ relation }} set {{ adapter.quote(tmp_column) }} = JSON_PARSE({{ adapter.quote(column_name) }});
    {% else %}
        update {{ relation }} set {{ adapter.quote(tmp_column) }} = {{ adapter.quote(column_name) }};
    {% endif %}
    alter table {{ relation }} drop column {{ adapter.quote(column_name) }} cascade;
    alter table {{ relation }} rename column {{ adapter.quote(tmp_column) }} to {{ adapter.quote(column_name) }}
  {% endcall %}

{% endmacro %}

{#
  This changes the behaviour of the default adapter macro, since DBT defaults to 256 when there are no explicit varchar limits
  (cf : https://github.com/dbt-labs/dbt-core/blob/3996a69861d5ba9a460092c93b7e08d8e2a63f88/core/dbt/adapters/base/column.py#L91)
  Since normalization code uses varchar for string type (and not text) on postgres, we need to set the max length possible when using unlimited varchars
  (cf : https://dba.stackexchange.com/questions/189876/size-limit-of-character-varying-postgresql)
#}

{% macro postgres__get_columns_in_relation(relation) -%}
  {% call statement('get_columns_in_relation', fetch_result=True) %}
      select
          column_name,
          data_type,
          COALESCE(character_maximum_length, 10485760),
          numeric_precision,
          numeric_scale

      from {{ relation.information_schema('columns') }}
      where table_name = '{{ relation.identifier }}'
        {% if relation.schema %}
        and table_schema = '{{ relation.schema }}'
        {% endif %}
      order by ordinal_position

  {% endcall %}
  {% set table = load_result('get_columns_in_relation').table %}
  {{ return(sql_convert_columns_in_relation(table)) }}
{% endmacro %}