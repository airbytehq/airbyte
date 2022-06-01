
      

  create  table "postgres"._airbyte_test_normalization."renamed_dedup_cdc_excluded_scd_new_data"
  as (
    
-- depends_on: ref('renamed_dedup_cdc_excluded_stg')

select * from "postgres"._airbyte_test_normalization."renamed_dedup_cdc_excluded_stg"


  );
  