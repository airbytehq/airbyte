{{ config(schema="TEST_NORMALIZATION", tags=["top-level-intermediate"]) }}
-- SQL model to build a hash column based on the values of this record
select
    ora_hash(
        'ID' || '~' ||
        {{array_to_string('CHILDREN')}}
    ) as {{ QUOTE('_AIRBYTE_UNNEST_ALIAS_HASHID') }},
    tmp.*
from {{ ref('UNNEST_ALIAS_AB2') }} tmp
-- UNNEST_ALIAS

