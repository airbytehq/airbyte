
      
    delete from "postgres".test_normalization."multiple_column_names_conflicts_scd"
    where (_airbyte_unique_key_scd) in (
        select (_airbyte_unique_key_scd)
        from "multiple_column_names_conflicts_scd__dbt_tmp"
    );
    

    insert into "postgres".test_normalization."multiple_column_names_conflicts_scd" ("_airbyte_unique_key", "_airbyte_unique_key_scd", "id", "User Id", "user_id", "User id", "user id", "User@Id", "userid", "_airbyte_start_at", "_airbyte_end_at", "_airbyte_active_row", "_airbyte_ab_id", "_airbyte_emitted_at", "_airbyte_normalized_at", "_airbyte_multiple_co__ames_conflicts_hashid")
    (
        select "_airbyte_unique_key", "_airbyte_unique_key_scd", "id", "User Id", "user_id", "User id", "user id", "User@Id", "userid", "_airbyte_start_at", "_airbyte_end_at", "_airbyte_active_row", "_airbyte_ab_id", "_airbyte_emitted_at", "_airbyte_normalized_at", "_airbyte_multiple_co__ames_conflicts_hashid"
        from "multiple_column_names_conflicts_scd__dbt_tmp"
    )
  