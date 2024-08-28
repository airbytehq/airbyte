
      
    delete from "postgres".test_normalization."types_testing"
    where (_airbyte_unique_key) in (
        select (_airbyte_unique_key)
        from "types_testing__dbt_tmp"
    );
    

    insert into "postgres".test_normalization."types_testing" ("_airbyte_unique_key", "id", "airbyte_integer_column", "nullable_airbyte_integer_column", "_airbyte_ab_id", "_airbyte_emitted_at", "_airbyte_normalized_at", "_airbyte_types_testing_hashid")
    (
        select "_airbyte_unique_key", "id", "airbyte_integer_column", "nullable_airbyte_integer_column", "_airbyte_ab_id", "_airbyte_emitted_at", "_airbyte_normalized_at", "_airbyte_types_testing_hashid"
        from "types_testing__dbt_tmp"
    )
  