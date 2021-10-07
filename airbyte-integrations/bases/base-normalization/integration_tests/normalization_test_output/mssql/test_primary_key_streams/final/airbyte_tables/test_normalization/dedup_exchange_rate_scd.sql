
   
  USE [test_normalization];
  if object_id ('test_normalization."dedup_exchange_rate_scd__dbt_tmp_temp_view"','V') is not null
      begin
      drop view test_normalization."dedup_exchange_rate_scd__dbt_tmp_temp_view"
      end


   
   
  USE [test_normalization];
  if object_id ('test_normalization."dedup_exchange_rate_scd__dbt_tmp"','U') is not null
      begin
      drop table test_normalization."dedup_exchange_rate_scd__dbt_tmp"
      end


   USE [test_normalization];
   EXEC('create view test_normalization."dedup_exchange_rate_scd__dbt_tmp_temp_view" as
    
with __dbt__CTE__dedup_exchange_rate_ab1 as (

-- SQL model to parse JSON blob stored in a single column and extract into separated field columns as described by the JSON Schema
select
    json_value(_airbyte_data, ''$."id"'') as id,
    json_value(_airbyte_data, ''$."currency"'') as currency,
    json_value(_airbyte_data, ''$."date"'') as "date",
    json_value(_airbyte_data, ''$."timestamp_col"'') as timestamp_col,
    json_value(_airbyte_data, ''$."HKD@spéçiäl & characters"'') as "HKD@spéçiäl & characters",
    json_value(_airbyte_data, ''$."HKD_special___characters"'') as hkd_special___characters,
    json_value(_airbyte_data, ''$."NZD"'') as nzd,
    json_value(_airbyte_data, ''$."USD"'') as usd,
    _airbyte_emitted_at
from "test_normalization".test_normalization._airbyte_raw_dedup_exchange_rate as table_alias
-- dedup_exchange_rate
),  __dbt__CTE__dedup_exchange_rate_ab2 as (

-- SQL model to cast each column to its adequate SQL type converted from the JSON schema type
select
    cast(id as 
    bigint
) as id,
    cast(currency as 
    VARCHAR(max)) as currency,
    try_parse("date" as date) as "date",
    try_parse(timestamp_col as datetime) as timestamp_col,
    cast("HKD@spéçiäl & characters" as 
    float
) as "HKD@spéçiäl & characters",
    cast(hkd_special___characters as 
    VARCHAR(max)) as hkd_special___characters,
    cast(nzd as 
    float
) as nzd,
    cast(usd as 
    float
) as usd,
    _airbyte_emitted_at
from __dbt__CTE__dedup_exchange_rate_ab1
-- dedup_exchange_rate
),  __dbt__CTE__dedup_exchange_rate_ab3 as (

-- SQL model to build a hash column based on the values of this record
select
    convert(varchar(32), HashBytes(''md5'',  coalesce(cast(
    
    

    concat(concat(coalesce(cast(id as 
    VARCHAR(max)), ''''), ''-'', coalesce(cast(currency as 
    VARCHAR(max)), ''''), ''-'', coalesce(cast("date" as 
    VARCHAR(max)), ''''), ''-'', coalesce(cast(timestamp_col as 
    VARCHAR(max)), ''''), ''-'', coalesce(cast("HKD@spéçiäl & characters" as 
    VARCHAR(max)), ''''), ''-'', coalesce(cast(hkd_special___characters as 
    VARCHAR(max)), ''''), ''-'', coalesce(cast(nzd as 
    VARCHAR(max)), ''''), ''-'', coalesce(cast(usd as 
    VARCHAR(max)), ''''),''''), '''') as 
    VARCHAR(max)), '''')), 2) as _airbyte_dedup_exchange_rate_hashid,
    tmp.*
from __dbt__CTE__dedup_exchange_rate_ab2 tmp
-- dedup_exchange_rate
),  __dbt__CTE__dedup_exchange_rate_ab4 as (

-- SQL model to prepare for deduplicating records based on the hash record column
select
  row_number() over (
    partition by _airbyte_dedup_exchange_rate_hashid
    order by _airbyte_emitted_at asc
  ) as _airbyte_row_num,
  tmp.*
from __dbt__CTE__dedup_exchange_rate_ab3 tmp
-- dedup_exchange_rate from "test_normalization".test_normalization._airbyte_raw_dedup_exchange_rate
)-- SQL model to build a Type 2 Slowly Changing Dimension (SCD) table for each record identified by their primary key
select
    id,
    currency,
    "date",
    timestamp_col,
    "HKD@spéçiäl & characters",
    hkd_special___characters,
    nzd,
    usd,
  "date" as _airbyte_start_at,
  lag("date") over (
    partition by id, currency, cast(nzd as 
    VARCHAR(max))
    order by "date" desc, "date" desc, _airbyte_emitted_at desc
  ) as _airbyte_end_at,
  case when lag("date") over (
    partition by id, currency, cast(nzd as 
    VARCHAR(max))
    order by "date" desc, "date" desc, _airbyte_emitted_at desc
  ) is null  then 1 else 0 end as _airbyte_active_row,
  _airbyte_emitted_at,
  _airbyte_dedup_exchange_rate_hashid
from __dbt__CTE__dedup_exchange_rate_ab4
-- dedup_exchange_rate from "test_normalization".test_normalization._airbyte_raw_dedup_exchange_rate
where _airbyte_row_num = 1
    ');

   SELECT * INTO "test_normalization".test_normalization."dedup_exchange_rate_scd__dbt_tmp" FROM
    "test_normalization".test_normalization."dedup_exchange_rate_scd__dbt_tmp_temp_view"

   
   
  USE [test_normalization];
  if object_id ('test_normalization."dedup_exchange_rate_scd__dbt_tmp_temp_view"','V') is not null
      begin
      drop view test_normalization."dedup_exchange_rate_scd__dbt_tmp_temp_view"
      end

    
   use [test_normalization];
  if EXISTS (
        SELECT * FROM
        sys.indexes WHERE name = 'test_normalization_dedup_exchange_rate_scd__dbt_tmp_cci'
        AND object_id=object_id('test_normalization_dedup_exchange_rate_scd__dbt_tmp')
    )
  DROP index test_normalization.dedup_exchange_rate_scd__dbt_tmp.test_normalization_dedup_exchange_rate_scd__dbt_tmp_cci
  CREATE CLUSTERED COLUMNSTORE INDEX test_normalization_dedup_exchange_rate_scd__dbt_tmp_cci
    ON test_normalization.dedup_exchange_rate_scd__dbt_tmp

   

