
      

  create  table "postgres"._airbyte_test_normalization."pos_dedup_cdcx_scd_new_data"
  as (
    
-- depends_on: ref('pos_dedup_cdcx_stg')

select * from "postgres"._airbyte_test_normalization."pos_dedup_cdcx_stg"


  );
  