
      

    insert into "postgres".test_normalization."nested_stream_with_c___names_partition_data" ("_airbyte_partition_hashid", "currency", "_airbyte_ab_id", "_airbyte_emitted_at", "_airbyte_normalized_at", "_airbyte_data_hashid")
    (
        select "_airbyte_partition_hashid", "currency", "_airbyte_ab_id", "_airbyte_emitted_at", "_airbyte_normalized_at", "_airbyte_data_hashid"
        from "nested_stream_with_c___names_partition_dat__dbt_tmp"
    )
  