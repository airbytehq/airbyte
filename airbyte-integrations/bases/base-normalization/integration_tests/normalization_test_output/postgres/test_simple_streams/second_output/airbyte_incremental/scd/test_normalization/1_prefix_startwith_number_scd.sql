
      
    delete from "postgres".test_normalization."1_prefix_startwith_number_scd"
    where (_airbyte_unique_key_scd) in (
        select (_airbyte_unique_key_scd)
        from "1_prefix_startwith_number_scd__dbt_tmp"
    );
    

    insert into "postgres".test_normalization."1_prefix_startwith_number_scd" ("_airbyte_unique_key", "_airbyte_unique_key_scd", "id", "date", "text", "_airbyte_start_at", "_airbyte_end_at", "_airbyte_active_row", "_airbyte_ab_id", "_airbyte_emitted_at", "_airbyte_normalized_at", "_airbyte_1_prefix_startwith_number_hashid")
    (
        select "_airbyte_unique_key", "_airbyte_unique_key_scd", "id", "date", "text", "_airbyte_start_at", "_airbyte_end_at", "_airbyte_active_row", "_airbyte_ab_id", "_airbyte_emitted_at", "_airbyte_normalized_at", "_airbyte_1_prefix_startwith_number_hashid"
        from "1_prefix_startwith_number_scd__dbt_tmp"
    )
  