{% macro mysql__except() %}
    {% do exceptions.warn("MySQL does not support EXCEPT operator") %}
{% endmacro %}
