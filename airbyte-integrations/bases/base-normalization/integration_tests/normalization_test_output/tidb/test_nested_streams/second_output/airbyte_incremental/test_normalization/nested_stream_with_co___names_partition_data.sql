
      insert into test_normalization.`nested_stream_with_co___names_partition_data` (`_airbyte_partition_hashid`, `currency`, `_airbyte_ab_id`, `_airbyte_emitted_at`, `_airbyte_normalized_at`, `_airbyte_data_hashid`)
    (
       select `_airbyte_partition_hashid`, `currency`, `_airbyte_ab_id`, `_airbyte_emitted_at`, `_airbyte_normalized_at`, `_airbyte_data_hashid`
       from test_normalization.`nested_stream_with_co___names_partition_data__dbt_tmp`
    )
  