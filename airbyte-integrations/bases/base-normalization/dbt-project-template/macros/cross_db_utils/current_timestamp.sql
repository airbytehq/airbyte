{% macro mysql__current_timestamp() %}
    NULL
{% endmacro %}

{% macro oracle__current_timestamp() %}
    CURRENT_TIMESTAMP
{% endmacro %}
