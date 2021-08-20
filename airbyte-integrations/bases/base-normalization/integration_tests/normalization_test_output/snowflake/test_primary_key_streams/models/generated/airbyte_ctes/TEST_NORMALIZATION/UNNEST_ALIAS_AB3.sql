{{ config(schema="_AIRBYTE_TEST_NORMALIZATION", tags=["top-level-intermediate"]) }}
-- SQL model to build a hash column based on the values of this record
select
    *,
    {{ dbt_utils.surrogate_key([
        'ID',
        array_to_string('CHILDREN'),
    ]) }} as _AIRBYTE_UNNEST_ALIAS_HASHID
from {{ ref('UNNEST_ALIAS_AB2') }}
-- UNNEST_ALIAS

