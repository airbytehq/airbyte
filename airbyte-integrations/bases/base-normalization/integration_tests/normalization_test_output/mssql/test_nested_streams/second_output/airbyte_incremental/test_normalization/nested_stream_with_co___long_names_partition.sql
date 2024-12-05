
      
  

    insert into "test_normalization".test_normalization."nested_stream_with_co___long_names_partition" ("_airbyte_nested_strea__nto_long_names_hashid", "double_array_data", "DATA", "_airbyte_ab_id", "_airbyte_emitted_at", "_airbyte_normalized_at", "_airbyte_partition_hashid")
    (
        select "_airbyte_nested_strea__nto_long_names_hashid", "double_array_data", "DATA", "_airbyte_ab_id", "_airbyte_emitted_at", "_airbyte_normalized_at", "_airbyte_partition_hashid"
        from "test_normalization".test_normalization."#nested_stream_with_co___long_names_partition__dbt_tmp"
    );

  