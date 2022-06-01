

  create view "integrationtests"._airbyte_test_normalization."dedup_exchange_rate_scd_new_data__dbt_tmp" as (
    
-- depends_on: ref('dedup_exchange_rate_stg')

select * from "integrationtests"._airbyte_test_normalization."dedup_exchange_rate_stg"


  ) ;
