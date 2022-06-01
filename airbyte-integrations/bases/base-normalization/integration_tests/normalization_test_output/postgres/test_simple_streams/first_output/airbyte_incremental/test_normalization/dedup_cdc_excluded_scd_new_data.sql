
      

  create  table "postgres"._airbyte_test_normalization."dedup_cdc_excluded_scd_new_data"
  as (
    
-- depends_on: ref('dedup_cdc_excluded_stg')

select * from "postgres"._airbyte_test_normalization."dedup_cdc_excluded_stg"


  );
  