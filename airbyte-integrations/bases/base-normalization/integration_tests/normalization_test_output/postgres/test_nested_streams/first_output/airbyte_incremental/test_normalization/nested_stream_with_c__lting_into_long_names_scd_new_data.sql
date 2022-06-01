
      

  create  table "postgres"._airbyte_test_normalization."nested_stream_with_c__lting_into_long_names_scd_new_data"
  as (
    
-- depends_on: ref('nested_stream_with_c__lting_into_long_names_stg')

select * from "postgres"._airbyte_test_normalization."nested_stream_with_c__lting_into_long_names_stg"


  );
  