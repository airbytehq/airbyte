

  create or replace view `dataline-integration-testing`._airbyte_test_normalization.`non_nested_stream_without_namespace_resulting_into_long_names_ab3`
  OPTIONS()
  as 
-- SQL model to build a hash column based on the values of this record
select
    to_hex(md5(cast(concat(coalesce(cast(id as 
    string
), ''), '-', coalesce(cast(date as 
    string
), '')) as 
    string
))) as _airbyte_non_nested_stream_without_namespace_resulting_into_long_names_hashid,
    tmp.*
from `dataline-integration-testing`._airbyte_test_normalization.`non_nested_stream_without_namespace_resulting_into_long_names_ab2` tmp
-- non_nested_stream_without_namespace_resulting_into_long_names;

