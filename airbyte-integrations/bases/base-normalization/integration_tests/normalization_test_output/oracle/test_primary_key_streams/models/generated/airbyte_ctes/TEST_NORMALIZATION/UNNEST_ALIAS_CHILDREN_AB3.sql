{{ config(schema="TEST_NORMALIZATION", tags=["nested-intermediate"]) }}
-- SQL model to build a hash column based on the values of this record
select
    ora_hash(
        '{{ QUOTE('_AIRBYTE_UNNEST_ALIAS_HASHID') }}' || '~' ||
        'AB_ID' || '~' ||
        'OWNER'
    ) as {{ QUOTE('_AIRBYTE_CHILDREN_HASHID') }},
    tmp.*
from {{ ref('UNNEST_ALIAS_CHILDREN_AB2') }} tmp
-- CHILDREN at unnest_alias/children

