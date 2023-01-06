
      
    delete from "normalization_tests".test_normalization_iprwf."nested_stream_with_complex_columns_resulting_into_long_names"
    where (_airbyte_unique_key) in (
        select (_airbyte_unique_key)
        from "nested_stream_with_complex_columns_resulti__dbt_tmp"
    );
    

    insert into "normalization_tests".test_normalization_iprwf."nested_stream_with_complex_columns_resulting_into_long_names" ("_airbyte_unique_key", "id", "date", "partition", "_airbyte_ab_id", "_airbyte_emitted_at", "_airbyte_normalized_at", "_airbyte_nested_stream_with_complex_columns_resulting_into_long_names_hashid")
    (
        select "_airbyte_unique_key", "id", "date", "partition", "_airbyte_ab_id", "_airbyte_emitted_at", "_airbyte_normalized_at", "_airbyte_nested_stream_with_complex_columns_resulting_into_long_names_hashid"
        from "nested_stream_with_complex_columns_resulti__dbt_tmp"
    )
  