
      

  create  table "postgres"._airbyte_test_normalization."some_stream_that_was_empty_scd_new_data"
  as (
    
-- depends_on: ref('some_stream_that_was_empty_stg')

select * from "postgres"._airbyte_test_normalization."some_stream_that_was_empty_stg"


  );
  