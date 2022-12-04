{#
    This overrides the behavior of the macro `should_full_refresh` so full refresh are triggered if:
    - the dbt cli is run with --full-refresh flag or the model is configured explicitly to full_refresh
    - the column _airbyte_ab_id does not exists in the normalized tables and make sure it is well populated.
#}

{%- macro need_full_refresh(col_ab_id, target_table=this) -%}
    {%- if not execute -%}
        {{ return(false) }}
    {%- endif -%}
    {%- set found_column = [] %}
    {%- set cols = adapter.get_columns_in_relation(target_table) -%}
    {%- for col in cols -%}
        {%- if col.column == col_ab_id -%}
            {% do found_column.append(col.column) %}
        {%- endif -%}
    {%- endfor -%}
    {%- if found_column -%}
        {{ return(false) }}
    {%- else -%}
        {{ dbt_utils.log_info(target_table ~ "." ~ col_ab_id ~ " does not exist yet. The table will be created or rebuilt with dbt.full_refresh") }}
        {{ return(true) }}
    {%- endif -%}
{%- endmacro -%}

{%- macro should_full_refresh() -%}
  {% set config_full_refresh = config.get('full_refresh') %}
  {%- if config_full_refresh is none -%}
    {% set config_full_refresh = flags.FULL_REFRESH %}
  {%- endif -%}
  {%- if not config_full_refresh -%}
    {% set config_full_refresh = need_full_refresh(get_col_ab_id(), this) %}
  {%- endif -%}
  {% do return(config_full_refresh) %}
{%- endmacro -%}

{%- macro get_col_ab_id() -%}
  {{ adapter.dispatch('get_col_ab_id')() }}
{%- endmacro -%}

{%- macro default__get_col_ab_id() -%}
    _airbyte_ab_id
{%- endmacro -%}

{%- macro oracle__get_col_ab_id() -%}
    "_AIRBYTE_AB_ID"
{%- endmacro -%}

{%- macro snowflake__get_col_ab_id() -%}
    _AIRBYTE_AB_ID
{%- endmacro -%}
