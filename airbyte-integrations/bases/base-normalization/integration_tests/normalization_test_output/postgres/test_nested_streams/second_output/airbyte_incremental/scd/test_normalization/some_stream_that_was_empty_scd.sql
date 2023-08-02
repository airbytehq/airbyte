
      
    delete from "postgres".test_normalization."some_stream_that_was_empty_scd"
    where (_airbyte_unique_key_scd) in (
        select (_airbyte_unique_key_scd)
        from "some_stream_that_was_empty_scd__dbt_tmp"
    );
    

    insert into "postgres".test_normalization."some_stream_that_was_empty_scd" ("_airbyte_unique_key", "_airbyte_unique_key_scd", "id", "date", "_airbyte_start_at", "_airbyte_end_at", "_airbyte_active_row", "_airbyte_ab_id", "_airbyte_emitted_at", "_airbyte_normalized_at", "_airbyte_some_stream_that_was_empty_hashid")
    (
        select "_airbyte_unique_key", "_airbyte_unique_key_scd", "id", "date", "_airbyte_start_at", "_airbyte_end_at", "_airbyte_active_row", "_airbyte_ab_id", "_airbyte_emitted_at", "_airbyte_normalized_at", "_airbyte_some_stream_that_was_empty_hashid"
        from "some_stream_that_was_empty_scd__dbt_tmp"
    )
  