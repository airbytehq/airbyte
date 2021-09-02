{# lag end_at cdc ------------------------------------------------------------------------------     #}
{% macro lag_end_at(cursor_field, primary_key, emitted_at) -%}
  {{ adapter.dispatch('lag_end_at')(cursor_field, primary_key, emitted_at) }}
{%- endmacro %}

{% macro default__lag_end_at(cursor_field, primary_key, emitted_at) -%}
    lag({{ cursor_field }}) over (
        partition by {{ primary_key }}
        order by {{ cursor_field }} is null asc, {{ cursor_field }} desc, {{ emitted_at }} desc
    )
{%- endmacro %}

{% macro oracle__lag_end_at(cursor_field, primary_key, emitted_at) -%}
    lag({{ cursor_field }}) over (
        partition by {{ primary_key }}
        order by {{ cursor_field }} desc, {{ emitted_at }} desc
    )
{%- endmacro %}


{# lag active_row cdc --------------------------------------------------------------------------     #}
{% macro lag_active_row(cursor_field, primary_key, emitted_at, cdc_updated_at_order) -%}
  {{ adapter.dispatch('lag_active_row')(cursor_field, primary_key, emitted_at, cdc_updated_at_order) }}
{%- endmacro %}

{% macro default__lag_active_row(cursor_field, primary_key, emitted_at, cdc_updated_at_order) -%}
    lag({{ cursor_field }}) over (
      partition by {{ primary_key }}
      order by {{ cursor_field }} is null asc, {{ cursor_field }} desc, {{ emitted_at }} desc{{ cdc_updated_at_order }}
    ) is null {{ cdc_active_row }}
{%- endmacro %}

{% macro oracle__lag_active_row(cursor_field, primary_key, emitted_at, cdc_updated_at_order) -%}
    coalesce(cast(lag({{ cursor_field }}) over (
        partition by {{ primary_key }}
        order by {{ cursor_field }} desc, {{ col_emitted_at }} desc
    ) as varchar(200)), 'Latest')
{%- endmacro %}



