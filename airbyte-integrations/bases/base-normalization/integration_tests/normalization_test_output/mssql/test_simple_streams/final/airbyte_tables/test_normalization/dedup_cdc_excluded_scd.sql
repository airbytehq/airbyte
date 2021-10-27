
   
  USE [test_normalization];
  if object_id ('test_normalization."dedup_cdc_excluded_scd__dbt_tmp_temp_view"','V') is not null
      begin
      drop view test_normalization."dedup_cdc_excluded_scd__dbt_tmp_temp_view"
      end


   
   
  USE [test_normalization];
  if object_id ('test_normalization."dedup_cdc_excluded_scd__dbt_tmp"','U') is not null
      begin
      drop table test_normalization."dedup_cdc_excluded_scd__dbt_tmp"
      end


   USE [test_normalization];
   EXEC('create view test_normalization."dedup_cdc_excluded_scd__dbt_tmp_temp_view" as
    
-- SQL model to build a Type 2 Slowly Changing Dimension (SCD) table for each record identified by their primary key
select
    id,
    name,
    "column`_''with""_quotes",
    _ab_cdc_lsn,
    _ab_cdc_updated_at,
    _ab_cdc_deleted_at,
  _airbyte_emitted_at as _airbyte_start_at,
  lag(_airbyte_emitted_at) over (
    partition by id
    order by _airbyte_emitted_at desc, _airbyte_emitted_at desc, _airbyte_emitted_at desc
  ) as _airbyte_end_at,
  case when lag(_airbyte_emitted_at) over (
    partition by id
    order by _airbyte_emitted_at desc, _airbyte_emitted_at desc, _airbyte_emitted_at desc, _ab_cdc_updated_at desc
  ) is null and _ab_cdc_deleted_at is null  then 1 else 0 end as _airbyte_active_row,
  _airbyte_emitted_at,
  _airbyte_dedup_cdc_excluded_hashid
from "test_normalization"._airbyte_test_normalization."dedup_cdc_excluded_ab4"
-- dedup_cdc_excluded from "test_normalization".test_normalization._airbyte_raw_dedup_cdc_excluded
where _airbyte_row_num = 1
    ');

   SELECT * INTO "test_normalization".test_normalization."dedup_cdc_excluded_scd__dbt_tmp" FROM
    "test_normalization".test_normalization."dedup_cdc_excluded_scd__dbt_tmp_temp_view"

   
   
  USE [test_normalization];
  if object_id ('test_normalization."dedup_cdc_excluded_scd__dbt_tmp_temp_view"','V') is not null
      begin
      drop view test_normalization."dedup_cdc_excluded_scd__dbt_tmp_temp_view"
      end

    
   use [test_normalization];
  if EXISTS (
        SELECT * FROM
        sys.indexes WHERE name = 'test_normalization_dedup_cdc_excluded_scd__dbt_tmp_cci'
        AND object_id=object_id('test_normalization_dedup_cdc_excluded_scd__dbt_tmp')
    )
  DROP index test_normalization.dedup_cdc_excluded_scd__dbt_tmp.test_normalization_dedup_cdc_excluded_scd__dbt_tmp_cci
  CREATE CLUSTERED COLUMNSTORE INDEX test_normalization_dedup_cdc_excluded_scd__dbt_tmp_cci
    ON test_normalization.dedup_cdc_excluded_scd__dbt_tmp

   

