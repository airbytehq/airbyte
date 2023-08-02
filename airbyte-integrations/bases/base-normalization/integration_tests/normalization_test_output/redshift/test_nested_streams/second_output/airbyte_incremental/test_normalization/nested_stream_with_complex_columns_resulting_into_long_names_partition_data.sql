
      

    insert into "integrationtests".test_normalization_xjvlg."nested_stream_with_complex_columns_resulting_into_long_names_partition_data" ("_airbyte_partition_hashid", "currency", "_airbyte_ab_id", "_airbyte_emitted_at", "_airbyte_normalized_at", "_airbyte_data_hashid")
    (
        select "_airbyte_partition_hashid", "currency", "_airbyte_ab_id", "_airbyte_emitted_at", "_airbyte_normalized_at", "_airbyte_data_hashid"
        from "nested_stream_with_complex_columns_resulti__dbt_tmp"
    )
  