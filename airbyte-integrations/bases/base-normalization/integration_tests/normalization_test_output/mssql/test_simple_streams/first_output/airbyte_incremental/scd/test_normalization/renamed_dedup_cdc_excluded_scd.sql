
      
   
  USE [test_normalization];
  if object_id ('test_normalization."renamed_dedup_cdc_excluded_scd_temp_view"','V') is not null
      begin
      drop view test_normalization."renamed_dedup_cdc_excluded_scd_temp_view"
      end


   
   
  USE [test_normalization];
  if object_id ('test_normalization."renamed_dedup_cdc_excluded_scd"','U') is not null
      begin
      drop table test_normalization."renamed_dedup_cdc_excluded_scd"
      end


   USE [test_normalization];
   EXEC('create view test_normalization."renamed_dedup_cdc_excluded_scd_temp_view" as
    
with

input_data as (
    select *
    from "test_normalization"._airbyte_test_normalization."renamed_dedup_cdc_excluded_ab3"
    -- renamed_dedup_cdc_excluded from "test_normalization".test_normalization._airbyte_raw_renamed_dedup_cdc_excluded
),

scd_data as (
    -- SQL model to build a Type 2 Slowly Changing Dimension (SCD) table for each record identified by their primary key
    select
      convert(varchar(32), HashBytes(''md5'',  coalesce(cast(
    
    

    concat(concat(coalesce(cast(id as 
    VARCHAR(max)), ''''),''''), '''') as 
    VARCHAR(max)), '''')), 2) as _airbyte_unique_key,
        id,
      _airbyte_emitted_at as _airbyte_start_at,
      lag(_airbyte_emitted_at) over (
        partition by id
        order by
            _airbyte_emitted_at desc,
            _airbyte_emitted_at desc,
            _airbyte_emitted_at desc
      ) as _airbyte_end_at,
      case when lag(_airbyte_emitted_at) over (
        partition by id
        order by
            _airbyte_emitted_at desc,
            _airbyte_emitted_at desc,
            _airbyte_emitted_at desc
      ) is null  then 1 else 0 end as _airbyte_active_row,
      _airbyte_ab_id,
      _airbyte_emitted_at,
      _airbyte_renamed_dedup_cdc_excluded_hashid
    from input_data
),
dedup_data as (
    select
        -- we need to ensure de-duplicated rows for merge/update queries
        -- additionally, we generate a unique key for the scd table
        row_number() over (
            partition by _airbyte_unique_key, _airbyte_start_at, _airbyte_emitted_at
            order by _airbyte_ab_id
        ) as _airbyte_row_num,
        convert(varchar(32), HashBytes(''md5'',  coalesce(cast(
    
    

    concat(concat(coalesce(cast(_airbyte_unique_key as 
    VARCHAR(max)), ''''), ''-'', coalesce(cast(_airbyte_start_at as 
    VARCHAR(max)), ''''), ''-'', coalesce(cast(_airbyte_emitted_at as 
    VARCHAR(max)), ''''),''''), '''') as 
    VARCHAR(max)), '''')), 2) as _airbyte_unique_key_scd,
        scd_data.*
    from scd_data
)
select
    _airbyte_unique_key,
    _airbyte_unique_key_scd,
        id,
    _airbyte_start_at,
    _airbyte_end_at,
    _airbyte_active_row,
    _airbyte_ab_id,
    _airbyte_emitted_at,
    SYSDATETIME() as _airbyte_normalized_at,
    _airbyte_renamed_dedup_cdc_excluded_hashid
from dedup_data where _airbyte_row_num = 1
    ');

   SELECT * INTO "test_normalization".test_normalization."renamed_dedup_cdc_excluded_scd" FROM
    "test_normalization".test_normalization."renamed_dedup_cdc_excluded_scd_temp_view"

   
   
  USE [test_normalization];
  if object_id ('test_normalization."renamed_dedup_cdc_excluded_scd_temp_view"','V') is not null
      begin
      drop view test_normalization."renamed_dedup_cdc_excluded_scd_temp_view"
      end

    
   use [test_normalization];
  if EXISTS (
        SELECT * FROM
        sys.indexes WHERE name = 'test_normalization_renamed_dedup_cdc_excluded_scd_cci'
        AND object_id=object_id('test_normalization_renamed_dedup_cdc_excluded_scd')
    )
  DROP index test_normalization.renamed_dedup_cdc_excluded_scd.test_normalization_renamed_dedup_cdc_excluded_scd_cci
  CREATE CLUSTERED COLUMNSTORE INDEX test_normalization_renamed_dedup_cdc_excluded_scd_cci
    ON test_normalization.renamed_dedup_cdc_excluded_scd

   


  