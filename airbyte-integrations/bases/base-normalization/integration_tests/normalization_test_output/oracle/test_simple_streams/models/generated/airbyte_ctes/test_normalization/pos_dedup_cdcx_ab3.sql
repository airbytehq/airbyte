{{ config(schema="test_normalization", tags=["top-level-intermediate"]) }}
-- SQL model to build a hash column based on the values of this record
select
    {{ dbt_utils.surrogate_key([
        'id',
        'name',
        quote('_AB_CDC_LSN'),
        quote('_AB_CDC_UPDATED_AT'),
        quote('_AB_CDC_DELETED_AT'),
        quote('_AB_CDC_LOG_POS'),
    ]) }} as {{ quote('_AIRBYTE_POS_DEDUP_CDCX_HASHID') }},
    tmp.*
from {{ ref('pos_dedup_cdcx_ab2') }} tmp
-- pos_dedup_cdcx

