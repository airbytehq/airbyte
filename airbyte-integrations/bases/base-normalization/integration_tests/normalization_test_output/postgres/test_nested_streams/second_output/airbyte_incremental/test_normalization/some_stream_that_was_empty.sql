
      
    delete from "postgres".test_normalization."some_stream_that_was_empty"
    where (_airbyte_unique_key) in (
        select (_airbyte_unique_key)
        from "some_stream_that_was_empty__dbt_tmp"
    );
    

    insert into "postgres".test_normalization."some_stream_that_was_empty" ("_airbyte_unique_key", "id", "date", "_airbyte_ab_id", "_airbyte_emitted_at", "_airbyte_normalized_at", "_airbyte_some_stream_that_was_empty_hashid")
    (
        select "_airbyte_unique_key", "id", "date", "_airbyte_ab_id", "_airbyte_emitted_at", "_airbyte_normalized_at", "_airbyte_some_stream_that_was_empty_hashid"
        from "some_stream_that_was_empty__dbt_tmp"
    )
  