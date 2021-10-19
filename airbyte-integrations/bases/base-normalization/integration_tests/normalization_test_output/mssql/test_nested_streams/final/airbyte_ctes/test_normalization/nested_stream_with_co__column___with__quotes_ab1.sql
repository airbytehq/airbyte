USE [test_normalization];
    execute('create view _airbyte_test_normalization."nested_stream_with_co__column___with__quotes_ab1__dbt_tmp" as
    
-- SQL model to parse JSON blob stored in a single column and extract into separated field columns as described by the JSON Schema

select
    _airbyte_partition_hashid,
    json_value(
    "column`_''with""_quotes".value, ''$."currency"'') as currency,
    _airbyte_emitted_at
from "test_normalization".test_normalization."nested_stream_with_co___long_names_partition" as table_alias

    CROSS APPLY (
	    SELECT [value] = CASE 
			WHEN [type] = 4 THEN (SELECT [value] FROM OPENJSON([value])) 
			WHEN [type] = 5 THEN [value]
			END
	    FROM OPENJSON("column`_''with""_quotes")
    ) AS "column`_''with""_quotes"
where "column`_''with""_quotes" is not null
-- column___with__quotes at nested_stream_with_complex_columns_resulting_into_long_names/partition/column`_''with"_quotes
    ');

