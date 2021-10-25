{{ config(schema="_AIRBYTE_TEST_NORMALIZATION", tags=["top-level-intermediate"]) }}
-- SQL model to build a hash column based on the values of this record
select
    {{ dbt_utils.surrogate_key([
        'ID',
        'NAME',
        '_AB_CDC_LSN',
        '_AB_CDC_UPDATED_AT',
        '_AB_CDC_DELETED_AT',
        '_AB_CDC_LOG_POS',
    ]) }} as _AIRBYTE_POS_DEDUP_CDCX_HASHID,
    tmp.*
from {{ ref('POS_DEDUP_CDCX_AB2') }} tmp
-- POS_DEDUP_CDCX

