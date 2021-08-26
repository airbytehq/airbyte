{{ config(schema="_AIRBYTE_TEST_NORMALIZATION", tags=["nested-intermediate"]) }}
-- SQL model to build a hash column based on the values of this record
select
    *,
    {{ dbt_utils.surrogate_key([
        '_AIRBYTE_UNNEST_ALIAS_HASHID',
        'AB_ID',
        'OWNER',
    ]) }} as _AIRBYTE_CHILDREN_HASHID
from {{ ref('UNNEST_ALIAS_CHILDREN_AB2') }}
-- CHILDREN at unnest_alias/children

