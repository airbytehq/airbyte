{{ config(schema="TEST_NORMALIZATION", tags=["nested-intermediate"]) }}
-- SQL model to build a hash column based on the values of this record
select
    ora_hash(
        '{{ QUOTE('_AIRBYTE_CHILDREN_HASHID') }}' || '~' ||
        'OWNER_ID'
    ) as {{ QUOTE('_AIRBYTE_OWNER_HASHID') }},
    tmp.*
from {{ ref('UNNEST_ALIAS_CHILDREN_OWNER_AB2') }} tmp
-- OWNER at unnest_alias/children/owner

