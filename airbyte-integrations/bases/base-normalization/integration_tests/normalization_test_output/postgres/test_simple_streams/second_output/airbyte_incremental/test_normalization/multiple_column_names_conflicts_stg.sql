
      
    delete from "postgres"._airbyte_test_normalization."multiple_column_names_conflicts_stg"
    where (_airbyte_ab_id) in (
        select (_airbyte_ab_id)
        from "multiple_column_names_conflicts_stg__dbt_tmp"
    );
    

    insert into "postgres"._airbyte_test_normalization."multiple_column_names_conflicts_stg" ("_airbyte_multiple_co__ames_conflicts_hashid", "id", "User Id", "user_id", "User id", "user id", "User@Id", "userid", "_airbyte_ab_id", "_airbyte_emitted_at", "_airbyte_normalized_at")
    (
        select "_airbyte_multiple_co__ames_conflicts_hashid", "id", "User Id", "user_id", "User id", "user id", "User@Id", "userid", "_airbyte_ab_id", "_airbyte_emitted_at", "_airbyte_normalized_at"
        from "multiple_column_names_conflicts_stg__dbt_tmp"
    )
  