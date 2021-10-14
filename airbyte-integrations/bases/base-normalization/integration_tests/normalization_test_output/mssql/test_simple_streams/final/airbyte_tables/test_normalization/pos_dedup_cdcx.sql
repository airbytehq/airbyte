
   
  USE [test_normalization];
  if object_id ('test_normalization."pos_dedup_cdcx__dbt_tmp_temp_view"','V') is not null
      begin
      drop view test_normalization."pos_dedup_cdcx__dbt_tmp_temp_view"
      end


   
   
  USE [test_normalization];
  if object_id ('test_normalization."pos_dedup_cdcx__dbt_tmp"','U') is not null
      begin
      drop table test_normalization."pos_dedup_cdcx__dbt_tmp"
      end


   USE [test_normalization];
   EXEC('create view test_normalization."pos_dedup_cdcx__dbt_tmp_temp_view" as
    
-- Final base SQL model
select
    id,
    name,
    _ab_cdc_lsn,
    _ab_cdc_updated_at,
    _ab_cdc_deleted_at,
    _ab_cdc_log_pos,
    _airbyte_emitted_at,
    _airbyte_pos_dedup_cdcx_hashid
from "test_normalization".test_normalization."pos_dedup_cdcx_scd"
-- pos_dedup_cdcx from "test_normalization".test_normalization._airbyte_raw_pos_dedup_cdcx
where _airbyte_active_row = 1
    ');

   SELECT * INTO "test_normalization".test_normalization."pos_dedup_cdcx__dbt_tmp" FROM
    "test_normalization".test_normalization."pos_dedup_cdcx__dbt_tmp_temp_view"

   
   
  USE [test_normalization];
  if object_id ('test_normalization."pos_dedup_cdcx__dbt_tmp_temp_view"','V') is not null
      begin
      drop view test_normalization."pos_dedup_cdcx__dbt_tmp_temp_view"
      end

    
   use [test_normalization];
  if EXISTS (
        SELECT * FROM
        sys.indexes WHERE name = 'test_normalization_pos_dedup_cdcx__dbt_tmp_cci'
        AND object_id=object_id('test_normalization_pos_dedup_cdcx__dbt_tmp')
    )
  DROP index test_normalization.pos_dedup_cdcx__dbt_tmp.test_normalization_pos_dedup_cdcx__dbt_tmp_cci
  CREATE CLUSTERED COLUMNSTORE INDEX test_normalization_pos_dedup_cdcx__dbt_tmp_cci
    ON test_normalization.pos_dedup_cdcx__dbt_tmp

   

