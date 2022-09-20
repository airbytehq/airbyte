
      
    delete from "postgres"._airbyte_test_normalization."types_testing_stg"
    where (_airbyte_ab_id) in (
        select (_airbyte_ab_id)
        from "types_testing_stg__dbt_tmp"
    );
    

    insert into "postgres"._airbyte_test_normalization."types_testing_stg" ("_airbyte_types_testing_hashid", "id", "airbyte_integer_column", "nullable_airbyte_integer_column", "_airbyte_ab_id", "_airbyte_emitted_at", "_airbyte_normalized_at")
    (
        select "_airbyte_types_testing_hashid", "id", "airbyte_integer_column", "nullable_airbyte_integer_column", "_airbyte_ab_id", "_airbyte_emitted_at", "_airbyte_normalized_at"
        from "types_testing_stg__dbt_tmp"
    )
  