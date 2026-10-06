
      
    delete from "postgres".test_normalization."multiple_column_names_conflicts"
    where (_airbyte_unique_key) in (
        select (_airbyte_unique_key)
        from "multiple_column_names_conflicts__dbt_tmp"
    );
    

    insert into "postgres".test_normalization."multiple_column_names_conflicts" ("_airbyte_unique_key", "id", "User Id", "user_id", "User id", "user id", "User@Id", "userid", "_airbyte_ab_id", "_airbyte_emitted_at", "_airbyte_normalized_at", "_airbyte_multiple_co__ames_conflicts_hashid")
    (
        select "_airbyte_unique_key", "id", "User Id", "user_id", "User id", "user id", "User@Id", "userid", "_airbyte_ab_id", "_airbyte_emitted_at", "_airbyte_normalized_at", "_airbyte_multiple_co__ames_conflicts_hashid"
        from "multiple_column_names_conflicts__dbt_tmp"
    )
  