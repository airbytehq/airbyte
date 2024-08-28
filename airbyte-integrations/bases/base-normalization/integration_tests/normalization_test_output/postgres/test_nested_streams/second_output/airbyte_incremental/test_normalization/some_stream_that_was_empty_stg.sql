
      
    delete from "postgres"._airbyte_test_normalization."some_stream_that_was_empty_stg"
    where (_airbyte_ab_id) in (
        select (_airbyte_ab_id)
        from "some_stream_that_was_empty_stg__dbt_tmp"
    );
    

    insert into "postgres"._airbyte_test_normalization."some_stream_that_was_empty_stg" ("_airbyte_some_stream_that_was_empty_hashid", "id", "date", "_airbyte_ab_id", "_airbyte_emitted_at", "_airbyte_normalized_at")
    (
        select "_airbyte_some_stream_that_was_empty_hashid", "id", "date", "_airbyte_ab_id", "_airbyte_emitted_at", "_airbyte_normalized_at"
        from "some_stream_that_was_empty_stg__dbt_tmp"
    )
  