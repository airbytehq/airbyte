
  create view _airbyte_test_normalization.`conflict_stream_name__2flict_stream_name_ab1__dbt_tmp` as (
    
-- SQL model to parse JSON blob stored in a single column and extract into separated field columns as described by the JSON Schema
select
    _airbyte_conflict_stream_name_hashid,
    
        json_extract(table_alias.conflict_stream_name, 
    '$."conflict_stream_name"')
     as conflict_stream_name,
    _airbyte_emitted_at
from test_normalization.`conflict_stream_name` as table_alias
where conflict_stream_name is not null
-- conflict_stream_name at conflict_stream_name/conflict_stream_name
  );
