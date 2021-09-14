{{ config(schema="test_normalization", tags=["top-level-intermediate"]) }}
-- SQL model to build a hash column based on the values of this record
select
    {{ dbt_utils.surrogate_key([
        'id',
        'name',
        quote('_AB_CDC_LSN'),
        quote('_AB_CDC_UPDATED_AT'),
        quote('_AB_CDC_DELETED_AT'),
    ]) }} as {{ quote('_AIRBYTE_DEDUP_CDC_EXCLUDED_HASHID') }},
    tmp.*
from {{ ref('dedup_cdc_excluded_ab2') }} tmp
-- dedup_cdc_excluded

