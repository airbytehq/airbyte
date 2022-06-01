
      

  create  table "postgres"._airbyte_test_normalization."1_prefix_startwith_number_scd_new_data"
  as (
    
-- depends_on: ref('1_prefix_startwith_number_stg')

select * from "postgres"._airbyte_test_normalization."1_prefix_startwith_number_stg"


  );
  