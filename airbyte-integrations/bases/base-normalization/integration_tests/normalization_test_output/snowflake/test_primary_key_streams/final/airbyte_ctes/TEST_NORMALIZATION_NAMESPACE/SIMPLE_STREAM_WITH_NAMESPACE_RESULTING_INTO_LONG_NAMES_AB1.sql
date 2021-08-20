
  create or replace  view "AIRBYTE_DATABASE"._AIRBYTE_TEST_NORMALIZATION_NAMESPACE."SIMPLE_STREAM_WITH_NAMESPACE_RESULTING_INTO_LONG_NAMES_AB1"  as (
    
-- SQL model to parse JSON blob stored in a single column and extract into separated field columns as described by the JSON Schema
select
    to_varchar(get_path(parse_json(_airbyte_data), '"id"')) as ID,
    to_varchar(get_path(parse_json(_airbyte_data), '"date"')) as DATE,
    _airbyte_emitted_at
from "AIRBYTE_DATABASE".TEST_NORMALIZATION_NAMESPACE._AIRBYTE_RAW_SIMPLE_STREAM_WITH_NAMESPACE_RESULTING_INTO_LONG_NAMES as table_alias
-- SIMPLE_STREAM_WITH_NAMESPACE_RESULTING_INTO_LONG_NAMES
  );
