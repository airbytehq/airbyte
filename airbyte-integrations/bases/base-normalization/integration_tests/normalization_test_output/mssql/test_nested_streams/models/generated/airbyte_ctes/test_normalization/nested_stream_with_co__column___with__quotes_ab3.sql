{{ config(
    unique_key = env_var('AIRBYTE_DEFAULT_UNIQUE_KEY', '_airbyte_ab_id'),
    schema = "_airbyte_test_normalization",
    tags = [ "nested-intermediate" ]
) }}
-- SQL model to build a hash column based on the values of this record
select
    {{ dbt_utils.surrogate_key([
        '_airbyte_partition_hashid',
        'currency',
    ]) }} as _airbyte_column___with__quotes_hashid,
    tmp.*
from {{ ref('nested_stream_with_co__column___with__quotes_ab2') }} tmp
-- column___with__quotes at nested_stream_with_complex_columns_resulting_into_long_names/partition/column`_'with"_quotes
where 1 = 1

