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
