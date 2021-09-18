{{ config(schema="_airbyte_test_normalization_namespace", tags=["top-level-intermediate"]) }}
-- SQL model to build a hash column based on the values of this record
select
    {{ dbt_utils.surrogate_key([
        'id',
        adapter.quote('date'),
    ]) }} as _airbyte_simple_strea__nto_long_names_hashid,
    tmp.*
from {{ ref('simple_stream_with_na_1g_into_long_names_ab2') }} tmp
-- simple_stream_with_na__lting_into_long_names

