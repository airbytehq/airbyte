
      
   
  USE [test_normalization];
  if object_id ('test_normalization."nested_stream_with_co___long_names_partition_temp_view"','V') is not null
      begin
      drop view test_normalization."nested_stream_with_co___long_names_partition_temp_view"
      end


   
   
  USE [test_normalization];
  if object_id ('test_normalization."nested_stream_with_co___long_names_partition"','U') is not null
      begin
      drop table test_normalization."nested_stream_with_co___long_names_partition"
      end


   USE [test_normalization];
   EXEC('create view test_normalization."nested_stream_with_co___long_names_partition_temp_view" as
    
with __dbt__cte__nested_stream_with_co___long_names_partition_ab1 as (

-- SQL model to parse JSON blob stored in a single column and extract into separated field columns as described by the JSON Schema
-- depends_on: "test_normalization".test_normalization."nested_stream_with_co__lting_into_long_names_scd"
select
    _airbyte_nested_strea__nto_long_names_hashid,
    json_query("partition", ''$."double_array_data"'') as double_array_data,
    json_query("partition", ''$."DATA"'') as "DATA",
    _airbyte_ab_id,
    _airbyte_emitted_at,
    SYSDATETIME() as _airbyte_normalized_at
from "test_normalization".test_normalization."nested_stream_with_co__lting_into_long_names_scd" as table_alias
-- partition at nested_stream_with_complex_columns_resulting_into_long_names/partition
where 1 = 1
and "partition" is not null

),  __dbt__cte__nested_stream_with_co___long_names_partition_ab2 as (

-- SQL model to cast each column to its adequate SQL type converted from the JSON schema type
-- depends_on: __dbt__cte__nested_stream_with_co___long_names_partition_ab1
select
    _airbyte_nested_strea__nto_long_names_hashid,
    double_array_data,
    "DATA",
    _airbyte_ab_id,
    _airbyte_emitted_at,
    SYSDATETIME() as _airbyte_normalized_at
from __dbt__cte__nested_stream_with_co___long_names_partition_ab1
-- partition at nested_stream_with_complex_columns_resulting_into_long_names/partition
where 1 = 1

),  __dbt__cte__nested_stream_with_co___long_names_partition_ab3 as (

-- SQL model to build a hash column based on the values of this record
-- depends_on: __dbt__cte__nested_stream_with_co___long_names_partition_ab2
select
    convert(varchar(32), HashBytes(''md5'',  coalesce(cast(
    
    

    concat(concat(coalesce(cast(_airbyte_nested_strea__nto_long_names_hashid as 
    NVARCHAR(max)), ''''), ''-'', coalesce(cast(cast(double_array_data as 
    NVARCHAR(max)) as 
    NVARCHAR(max)), ''''), ''-'', coalesce(cast(cast("DATA" as 
    NVARCHAR(max)) as 
    NVARCHAR(max)), ''''),''''), '''') as 
    NVARCHAR(max)), '''')), 2) as _airbyte_partition_hashid,
    tmp.*
from __dbt__cte__nested_stream_with_co___long_names_partition_ab2 tmp
-- partition at nested_stream_with_complex_columns_resulting_into_long_names/partition
where 1 = 1

)-- Final base SQL model
-- depends_on: __dbt__cte__nested_stream_with_co___long_names_partition_ab3
select
    _airbyte_nested_strea__nto_long_names_hashid,
    double_array_data,
    "DATA",
    _airbyte_ab_id,
    _airbyte_emitted_at,
    SYSDATETIME() as _airbyte_normalized_at,
    _airbyte_partition_hashid
from __dbt__cte__nested_stream_with_co___long_names_partition_ab3
-- partition at nested_stream_with_complex_columns_resulting_into_long_names/partition from "test_normalization".test_normalization."nested_stream_with_co__lting_into_long_names_scd"
where 1 = 1

    ');

   SELECT * INTO "test_normalization".test_normalization."nested_stream_with_co___long_names_partition" FROM
    "test_normalization".test_normalization."nested_stream_with_co___long_names_partition_temp_view"

   
   
  USE [test_normalization];
  if object_id ('test_normalization."nested_stream_with_co___long_names_partition_temp_view"','V') is not null
      begin
      drop view test_normalization."nested_stream_with_co___long_names_partition_temp_view"
      end

    
   use [test_normalization];
  if EXISTS (
        SELECT * FROM
        sys.indexes WHERE name = 'test_normalization_nested_stream_with_co___long_names_partition_cci'
        AND object_id=object_id('test_normalization_nested_stream_with_co___long_names_partition')
    )
  DROP index test_normalization.nested_stream_with_co___long_names_partition.test_normalization_nested_stream_with_co___long_names_partition_cci
  CREATE CLUSTERED COLUMNSTORE INDEX test_normalization_nested_stream_with_co___long_names_partition_cci
    ON test_normalization.nested_stream_with_co___long_names_partition

   


  