
      
   
  USE [test_normalization];
  if object_id ('test_normalization."renamed_dedup_cdc_excluded_temp_view"','V') is not null
      begin
      drop view test_normalization."renamed_dedup_cdc_excluded_temp_view"
      end


   
   
  USE [test_normalization];
  if object_id ('test_normalization."renamed_dedup_cdc_excluded"','U') is not null
      begin
      drop table test_normalization."renamed_dedup_cdc_excluded"
      end


   USE [test_normalization];
   EXEC('create view test_normalization."renamed_dedup_cdc_excluded_temp_view" as
    
-- Final base SQL model
select
    _airbyte_unique_key,
    id,
    _airbyte_ab_id,
    _airbyte_emitted_at,
    SYSDATETIME() as _airbyte_normalized_at,
    _airbyte_renamed_dedup_cdc_excluded_hashid
from "test_normalization".test_normalization."renamed_dedup_cdc_excluded_scd"
-- renamed_dedup_cdc_excluded from "test_normalization".test_normalization._airbyte_raw_renamed_dedup_cdc_excluded
where 1 = 1
and _airbyte_active_row = 1

    ');

   SELECT * INTO "test_normalization".test_normalization."renamed_dedup_cdc_excluded" FROM
    "test_normalization".test_normalization."renamed_dedup_cdc_excluded_temp_view"

   
   
  USE [test_normalization];
  if object_id ('test_normalization."renamed_dedup_cdc_excluded_temp_view"','V') is not null
      begin
      drop view test_normalization."renamed_dedup_cdc_excluded_temp_view"
      end

    
   use [test_normalization];
  if EXISTS (
        SELECT * FROM
        sys.indexes WHERE name = 'test_normalization_renamed_dedup_cdc_excluded_cci'
        AND object_id=object_id('test_normalization_renamed_dedup_cdc_excluded')
    )
  DROP index test_normalization.renamed_dedup_cdc_excluded.test_normalization_renamed_dedup_cdc_excluded_cci
  CREATE CLUSTERED COLUMNSTORE INDEX test_normalization_renamed_dedup_cdc_excluded_cci
    ON test_normalization.renamed_dedup_cdc_excluded

   


  