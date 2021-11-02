USE [test_normalization];
    execute('create view _airbyte_test_normalization."nested_stream_with_co___names_partition_data_ab1__dbt_tmp" as
    
-- SQL model to parse JSON blob stored in a single column and extract into separated field columns as described by the JSON Schema

select
    _airbyte_partition_hashid,
    json_value(
    "DATA".value, ''$."currency"'') as currency,
    _airbyte_ab_id,
    _airbyte_emitted_at,
    SYSDATETIME() as _airbyte_normalized_at
from "test_normalization".test_normalization."nested_stream_with_co___long_names_partition" as table_alias
-- DATA at nested_stream_with_complex_columns_resulting_into_long_names/partition/DATA

    CROSS APPLY (
	    SELECT [value] = CASE 
			WHEN [type] = 4 THEN (SELECT [value] FROM OPENJSON([value])) 
			WHEN [type] = 5 THEN [value]
			END
	    FROM OPENJSON("DATA")
    ) AS "DATA"
where 1 = 1
and "DATA" is not null
    ');

