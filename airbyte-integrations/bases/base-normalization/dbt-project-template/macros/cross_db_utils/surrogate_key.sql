{# surrogate_key  ----------------------------------     #}

{% macro oracle__surrogate_key(field_list) -%}
    ora_hash(
        {%- for field in field_list %}
            {% if not loop.last %}
                {{ field }} || '~' ||
            {% else %}
                {{ field }}
            {% endif %}
        {%- endfor %}
    )
{%- endmacro %}

{# MSSQL surrogate_key #}
{%- macro sqlserver__surrogate_key(field_list) -%}
    {% set fields = [] %}
    {%- for field in field_list -%}
        {% set _ = fields.append("coalesce(cast(" ~ field ~ " as " ~ dbt_utils.type_string() ~ "), '')") %}
    {%- endfor -%}
    {{dbt_utils.hash(dbt_utils.concat(fields))}}
{%- endmacro -%}
