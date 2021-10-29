{{ config(
    unique_key = env_var('AIRBYTE_DEFAULT_UNIQUE_KEY', quote('_AIRBYTE_AB_ID')),
    schema = "test_normalization",
    tags = [ "top-level-intermediate" ]
) }}
-- SQL model to build a hash column based on the values of this record
select
    {{ dbt_utils.surrogate_key([
        'id',
    ]) }} as {{ quote('_AIRBYTE_RENAMED_DEDUP_CDC_EXCLUDED_HASHID') }},
    tmp.*
from {{ ref('renamed_dedup_cdc_excluded_ab2') }} tmp
-- renamed_dedup_cdc_excluded
where 1 = 1
{{ incremental_clause(quote('_AIRBYTE_EMITTED_AT')) }}

