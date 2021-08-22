{{ config(schema="TEST_NORMALIZATION", tags=["top-level-intermediate"]) }}
-- SQL model to build a hash column based on the values of this record
select
    ora_hash(
        'ID' || '~' ||
        'NAME' || '~' ||
        {{QUOTE('_AB_CDC_LSN')}} || '~' ||
        {{QUOTE('_AB_CDC_UPDATED_AT')}} || '~' ||
        {{QUOTE('_AB_CDC_DELETED_AT')}}
    ) as {{ QUOTE('_AIRBYTE_DEDUP_CDC_EXCLUDED_HASHID') }},
    tmp.*
from {{ ref('DEDUP_CDC_EXCLUDED_AB2') }} tmp
-- DEDUP_CDC_EXCLUDED

