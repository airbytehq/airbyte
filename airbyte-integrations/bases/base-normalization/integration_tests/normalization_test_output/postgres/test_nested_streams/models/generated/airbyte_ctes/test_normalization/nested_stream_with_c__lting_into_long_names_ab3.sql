{{ config(schema="_airbyte_test_normalization", tags=["top-level-intermediate"]) }}
-- SQL model to build a hash column based on the values of this record
select
    {{ dbt_utils.surrogate_key([
        adapter.quote('id'),
        adapter.quote('date'),
        adapter.quote('partition'),
    ]) }} as _airbyte_nested_stre__nto_long_names_hashid,
    tmp.*
from {{ ref('nested_stream_with_c__lting_into_long_names_ab2') }} tmp
-- nested_stream_with_c__lting_into_long_names

