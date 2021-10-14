
   
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
    
-- SQL model to build a Type 2 Slowly Changing Dimension (SCD) table for each record identified by their primary key
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
from "test_normalization"._airbyte_test_normalization."dedup_exchange_rate_ab4"
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

   

