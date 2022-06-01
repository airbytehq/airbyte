
      

  create  table "postgres"._airbyte_test_normalization."dedup_exchange_rate_scd_new_data"
  as (
    
-- depends_on: ref('dedup_exchange_rate_stg')

select * from "postgres"._airbyte_test_normalization."dedup_exchange_rate_stg"


  );
  