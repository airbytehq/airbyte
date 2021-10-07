{{ config(schema="_airbyte_test_normalization", tags=["top-level-intermediate"]) }}
-- SQL model to build a hash column based on the values of this record
select
    {{ dbt_utils.surrogate_key([
        'id',
        array_to_string('children'),
    ]) }} as _airbyte_unnest_alias_hashid,
    tmp.*
from {{ ref('unnest_alias_ab2') }} tmp
-- unnest_alias

