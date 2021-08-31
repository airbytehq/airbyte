{{ config(schema="test_normalization", tags=["top-level-intermediate"]) }}
-- SQL model to build a hash column based on the values of this record
select
    ora_hash(
            'id' || '~' ||
            {{ array_to_string('children') }}
    ) as {{ quote('_AIRBYTE_UNNEST_ALIAS_HASHID') }},
    tmp.*
from {{ ref('unnest_alias_ab2') }} tmp
-- unnest_alias

