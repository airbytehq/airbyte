
      
  

    insert into "test_normalization".test_normalization."nested_stream_with_co__ion_double_array_data" ("_airbyte_partition_hashid", "id", "_airbyte_ab_id", "_airbyte_emitted_at", "_airbyte_normalized_at", "_airbyte_double_array_data_hashid")
    (
        select "_airbyte_partition_hashid", "id", "_airbyte_ab_id", "_airbyte_emitted_at", "_airbyte_normalized_at", "_airbyte_double_array_data_hashid"
        from "test_normalization".test_normalization."#nested_stream_with_co__ion_double_array_data__dbt_tmp"
    );

  