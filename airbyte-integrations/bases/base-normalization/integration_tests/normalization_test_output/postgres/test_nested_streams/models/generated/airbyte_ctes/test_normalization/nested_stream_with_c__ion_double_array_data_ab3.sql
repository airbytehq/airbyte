{{ config(
    indexes = [{'columns':['_airbyte_emitted_at'],'type':'btree'}],
    schema = "_airbyte_test_normalization",
    tags = [ "nested-intermediate" ]
) }}
-- SQL model to build a hash column based on the values of this record
-- depends_on: {{ ref('nested_stream_with_c__ion_double_array_data_ab2') }}
select
    {{ dbt_utils.surrogate_key([
        '_airbyte_partition_hashid',
        adapter.quote('id'),
    ]) }} as _airbyte_double_array_data_hashid,
    tmp.*
from {{ ref('nested_stream_with_c__ion_double_array_data_ab2') }} tmp
-- double_array_data at nested_stream_with_complex_columns_resulting_into_long_names/partition/double_array_data
where 1 = 1
{{ incremental_clause('_airbyte_emitted_at', this) }}

