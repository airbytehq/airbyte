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
