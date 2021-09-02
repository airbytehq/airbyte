{{ config(schema="_airbyte_test_normalization", tags=["top-level-intermediate"]) }}
-- SQL model to build a hash column based on the values of this record
select
    *,
    {{ dbt_utils.surrogate_key([
        'id',
        adapter.quote('date'),
    ]) }} as _airbyte_non_nested_s__nto_long_names_hashid
from {{ ref('non_nested_stream_wit_1g_into_long_names_ab2') }}
-- non_nested_stream_wit__lting_into_long_names

