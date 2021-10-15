{{ config(schema="test_normalization", tags=["top-level"]) }}
-- SQL model to build a Type 2 Slowly Changing Dimension (SCD) table for each record identified by their primary key
select
    {{ adapter.quote('id') }},
    {{ adapter.quote('date') }},
    {{ adapter.quote('partition') }},
  {{ adapter.quote('date') }} as _airbyte_start_at,
  lag({{ adapter.quote('date') }}) over (
    partition by {{ adapter.quote('id') }}
    order by {{ adapter.quote('date') }} is null asc, {{ adapter.quote('date') }} desc, _airbyte_emitted_at desc
  ) as _airbyte_end_at,
  case when lag({{ adapter.quote('date') }}) over (
    partition by {{ adapter.quote('id') }}
    order by {{ adapter.quote('date') }} is null asc, {{ adapter.quote('date') }} desc, _airbyte_emitted_at desc
  ) is null  then 1 else 0 end as _airbyte_active_row,
  _airbyte_emitted_at,
  _airbyte_nested_stre__nto_long_names_hashid
from {{ ref('nested_stream_with_c__lting_into_long_names_ab4') }}
-- nested_stream_with_c__lting_into_long_names from {{ source('test_normalization', '_airbyte_raw_nested_stream_with_complex_columns_resulting_into_long_names') }}
where _airbyte_row_num = 1

