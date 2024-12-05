
      
   
  USE [test_normalization];
  if object_id ('test_normalization."nested_stream_with_co__ion_double_array_data_temp_view"','V') is not null
      begin
      drop view test_normalization."nested_stream_with_co__ion_double_array_data_temp_view"
      end


   
   
  USE [test_normalization];
  if object_id ('test_normalization."nested_stream_with_co__ion_double_array_data"','U') is not null
      begin
      drop table test_normalization."nested_stream_with_co__ion_double_array_data"
      end


   USE [test_normalization];
   EXEC('create view test_normalization."nested_stream_with_co__ion_double_array_data_temp_view" as
    
with __dbt__cte__nested_stream_with_co__ion_double_array_data_ab1 as (

-- SQL model to parse JSON blob stored in a single column and extract into separated field columns as described by the JSON Schema
-- depends_on: "test_normalization".test_normalization."nested_stream_with_co___long_names_partition"

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

),  __dbt__cte__nested_stream_with_co__ion_double_array_data_ab2 as (

-- SQL model to cast each column to its adequate SQL type converted from the JSON schema type
-- depends_on: __dbt__cte__nested_stream_with_co__ion_double_array_data_ab1
select
    _airbyte_partition_hashid,
    cast(id as 
    NVARCHAR(max)) as id,
    _airbyte_ab_id,
    _airbyte_emitted_at,
    SYSDATETIME() as _airbyte_normalized_at
from __dbt__cte__nested_stream_with_co__ion_double_array_data_ab1
-- double_array_data at nested_stream_with_complex_columns_resulting_into_long_names/partition/double_array_data
where 1 = 1

),  __dbt__cte__nested_stream_with_co__ion_double_array_data_ab3 as (

-- SQL model to build a hash column based on the values of this record
-- depends_on: __dbt__cte__nested_stream_with_co__ion_double_array_data_ab2
select
    convert(varchar(32), HashBytes(''md5'',  coalesce(cast(
    
    

    concat(concat(coalesce(cast(_airbyte_partition_hashid as 
    NVARCHAR(max)), ''''), ''-'', coalesce(cast(id as 
    NVARCHAR(max)), ''''),''''), '''') as 
    NVARCHAR(max)), '''')), 2) as _airbyte_double_array_data_hashid,
    tmp.*
from __dbt__cte__nested_stream_with_co__ion_double_array_data_ab2 tmp
-- double_array_data at nested_stream_with_complex_columns_resulting_into_long_names/partition/double_array_data
where 1 = 1

)-- Final base SQL model
-- depends_on: __dbt__cte__nested_stream_with_co__ion_double_array_data_ab3
select
    _airbyte_partition_hashid,
    id,
    _airbyte_ab_id,
    _airbyte_emitted_at,
    SYSDATETIME() as _airbyte_normalized_at,
    _airbyte_double_array_data_hashid
from __dbt__cte__nested_stream_with_co__ion_double_array_data_ab3
-- double_array_data at nested_stream_with_complex_columns_resulting_into_long_names/partition/double_array_data from "test_normalization".test_normalization."nested_stream_with_co___long_names_partition"
where 1 = 1

    ');

   SELECT * INTO "test_normalization".test_normalization."nested_stream_with_co__ion_double_array_data" FROM
    "test_normalization".test_normalization."nested_stream_with_co__ion_double_array_data_temp_view"

   
   
  USE [test_normalization];
  if object_id ('test_normalization."nested_stream_with_co__ion_double_array_data_temp_view"','V') is not null
      begin
      drop view test_normalization."nested_stream_with_co__ion_double_array_data_temp_view"
      end

    
   use [test_normalization];
  if EXISTS (
        SELECT * FROM
        sys.indexes WHERE name = 'test_normalization_nested_stream_with_co__ion_double_array_data_cci'
        AND object_id=object_id('test_normalization_nested_stream_with_co__ion_double_array_data')
    )
  DROP index test_normalization.nested_stream_with_co__ion_double_array_data.test_normalization_nested_stream_with_co__ion_double_array_data_cci
  CREATE CLUSTERED COLUMNSTORE INDEX test_normalization_nested_stream_with_co__ion_double_array_data_cci
    ON test_normalization.nested_stream_with_co__ion_double_array_data

   


  