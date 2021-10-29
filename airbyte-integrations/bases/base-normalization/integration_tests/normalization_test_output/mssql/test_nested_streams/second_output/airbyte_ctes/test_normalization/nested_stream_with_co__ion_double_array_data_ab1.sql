USE [test_normalization];
    execute('create view _airbyte_test_normalization."nested_stream_with_co__ion_double_array_data_ab1__dbt_tmp" as
    
-- SQL model to parse JSON blob stored in a single column and extract into separated field columns as described by the JSON Schema

select
    _airbyte_partition_hashid,
    json_value(
    double_array_data.value, ''$."id"'') as id,
    _airbyte_ab_id,
    _airbyte_emitted_at,
    SYSDATETIME() as _airbyte_normalized_at
from "test_normalization".test_normalization."nested_stream_with_co___long_names_partition" as table_alias
-- double_array_data at nested_stream_with_complex_columns_resulting_into_long_names/partition/double_array_data

    CROSS APPLY (
	    SELECT [value] = CASE 
			WHEN [type] = 4 THEN (SELECT [value] FROM OPENJSON([value])) 
			WHEN [type] = 5 THEN [value]
			END
	    FROM OPENJSON(double_array_data)
    ) AS double_array_data
where 1 = 1
and double_array_data is not null
    ');

