{#
    This macro controls how incremental models are updated in Airbyte's normalization step
#}

{%- macro incremental_clause(col_emitted_at) -%}
{% if is_incremental() %}
and {{ col_emitted_at }} >= (select max({{ col_emitted_at }}) from {{ this }})
{% endif %}
{%- endmacro -%}
