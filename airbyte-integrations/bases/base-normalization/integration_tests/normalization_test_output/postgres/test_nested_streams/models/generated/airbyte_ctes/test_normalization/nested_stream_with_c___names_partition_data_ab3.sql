{{ config(
    indexes = [{'columns':['_airbyte_emitted_at'],'type':'btree'}],
    schema = "_airbyte_test_normalization",
    tags = [ "nested-intermediate" ]
) }}
-- SQL model to build a hash column based on the values of this record
-- depends_on: {{ ref('nested_stream_with_c___names_partition_data_ab2') }}
select
    {{ dbt_utils.surrogate_key([
        '_airbyte_partition_hashid',
        'currency',
    ]) }} as _airbyte_data_hashid,
    tmp.*
from {{ ref('nested_stream_with_c___names_partition_data_ab2') }} tmp
-- DATA at nested_stream_with_complex_columns_resulting_into_long_names/partition/DATA
where 1 = 1
{{ incremental_clause('_airbyte_emitted_at', this) }}

