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

{#-- MSSQL surrogate_key  --#}
{%- macro sqlserver__surrogate_key(field_list) -%}
    {% set fields = [] %}
    {%- for field in field_list -%}
        {% set _ = fields.append("coalesce(cast(" ~ field ~ " as " ~ dbt_utils.type_string() ~ "), '')") %}
    {%- endfor -%}

    {#-- CONCAT() in SQL SERVER accepts from 2 to 254 arguments, we use batches for the main concat, to overcome the limit. --#}
    {% set concat_chunks = [] %}
    {% for chunk in fields|batch(253) -%}
        {% set _ = concat_chunks.append(dbt_utils.concat(chunk)) %}
    {% endfor %}

    {#-- Apply the main concat() to the chunked concats. --#}
    {{dbt_utils.hash(dbt_utils.concat(concat_chunks))}}
{%- endmacro -%}
