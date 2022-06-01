
      

  create  table "postgres"._airbyte_test_normalization."multiple_column_names_conflicts_scd_new_data"
  as (
    
-- depends_on: ref('multiple_column_names_conflicts_stg')

select * from "postgres"._airbyte_test_normalization."multiple_column_names_conflicts_stg"


  );
  