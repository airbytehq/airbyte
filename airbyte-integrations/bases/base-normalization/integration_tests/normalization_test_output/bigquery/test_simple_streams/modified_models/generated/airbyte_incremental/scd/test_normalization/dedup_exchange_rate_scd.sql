{{ config(
    cluster_by = ["_airbyte_unique_key_scd","_airbyte_emitted_at"],
    partition_by = {"field": "_airbyte_active_row", "data_type": "int64", "range": {"start": 0, "end": 1, "interval": 1}},
    unique_key = "_airbyte_unique_key_scd",
    schema = "test_normalization",
    post_hook = ["
                        {%
                        set final_table_relation = adapter.get_relation(
                                database=this.database,
                                schema=this.schema,
                                identifier='dedup_exchange_rate'
                            )
                        %}
                        {#
                        If the final table doesn't exist, then obviously we can't delete anything from it.
                        Also, after a reset, the final table is created without the _airbyte_unique_key column (this column is created during the first sync)
                        So skip this deletion if the column doesn't exist. (in this case, the table is guaranteed to be empty anyway)
                        #}
                        {%
                        if final_table_relation is not none and '_airbyte_unique_key' in adapter.get_columns_in_relation(final_table_relation)|map(attribute='name')
                        %}
                        -- Delete records which are no longer active:
                        -- 1. Find the records which are being updated by querying the _scd_new_data model
                        -- 2. Then join that against the SCD model to find the records which have no row with _airbyte_active_row = 1
                        -- We can't just delete all the modified_ids from final_table because those records might still be active, but not included
                        -- in the most recent increment (i.e. the final table model would not re-insert them, so the data would be incorrectly lost).
                        -- In fact, there's no guarantee that the active record is included in the previous_active_scd_data CTE either,
                        -- so we _must_ join against the entire SCD table to find the active row for each record.
                        -- We're using a subquery because not all destinations support CTEs in DELETE statements (c.f. Snowflake).
                        -- Similarly, the subquery doesn't use CTEs because Clickhouse doesn't support CTEs inside delete conditions.
                        delete from {{ final_table_relation }} final_table where final_table._airbyte_unique_key in (
                            select modified_ids._airbyte_unique_key
                            from
                                (
                                    select nullif(scd_table._airbyte_unique_key, '') as _airbyte_unique_key from {{ this }} scd_table
-- TODO is this even necessary?
--                              inner join modified_ids on scd_table._airbyte_unique_key = modified_ids._airbyte_unique_key
                                    where _airbyte_active_row =  1
                                ) scd_active_rows
                                right outer join (
                                    select
                                        {{ dbt_utils.surrogate_key([
                                                'id',
                                                'currency',
                                                'NZD',
                                        ]) }} as _airbyte_unique_key
                                    from {{ ref('dedup_exchange_rate_scd_new_data') }}
                                    where 1=1
                                        {{ incremental_clause('_airbyte_emitted_at', this.schema + '.' + adapter.quote('dedup_exchange_rate')) }}
                                ) modified_ids
                                on modified_ids._airbyte_unique_key = scd_active_rows._airbyte_unique_key
                            group by modified_ids._airbyte_unique_key
                            having count(scd_active_rows._airbyte_unique_key) = 0
                        )
                        {% else %}
                        -- We have to have a non-empty query, so just do a noop delete
                        delete from {{ this }} where 1=0
                        {% endif %}
                        ","drop view {{ ref('dedup_exchange_rate_scd_new_data') }}","drop view _airbyte_test_normalization.dedup_exchange_rate_stg"],
    tags = [ "top-level" ]
) }}
-- depends on: {{ ref('dedup_exchange_rate_scd_new_data') }}
with
{% if is_incremental() %}
new_data_ids as (
    -- build a subset of _airbyte_unique_key from rows that are new
    select distinct
        {{ dbt_utils.surrogate_key([
            'id',
            'currency',
            'NZD',
        ]) }} as _airbyte_unique_key
    from {{ ref('dedup_exchange_rate_scd_new_data') }}
),
empty_new_data as (
    -- build an empty table to only keep the table's column types
    select * from {{ ref('dedup_exchange_rate_scd_new_data') }} where 1 = 0
),
previous_active_scd_data as (
    -- retrieve "incomplete old" data that needs to be updated with an end date because of new changes
    select
        {{ star_intersect(ref('dedup_exchange_rate_stg'), this, from_alias='inc_data', intersect_alias='this_data') }}
    from {{ this }} as this_data
    -- make a join with new_data using primary key to filter active data that need to be updated only
    join new_data_ids on this_data._airbyte_unique_key = new_data_ids._airbyte_unique_key
    -- force left join to NULL values (we just need to transfer column types only for the star_intersect macro on schema changes)
    left join empty_new_data as inc_data on this_data._airbyte_ab_id = inc_data._airbyte_ab_id
    where _airbyte_active_row = 1
),
input_data as (
    select {{ dbt_utils.star(ref('dedup_exchange_rate_stg')) }} from {{ ref('dedup_exchange_rate_scd_new_data') }}
    union all
    select {{ dbt_utils.star(ref('dedup_exchange_rate_stg')) }} from previous_active_scd_data
),
{% else %}
input_data as (
    select *
    from {{ ref('dedup_exchange_rate_stg')  }}
    -- dedup_exchange_rate from {{ source('test_normalization', '_airbyte_raw_dedup_exchange_rate') }}
),
{% endif %}
scd_data as (
    -- SQL model to build a Type 2 Slowly Changing Dimension (SCD) table for each record identified by their primary key
    select
      {{ dbt_utils.surrogate_key([
      'id',
      'currency',
      'NZD',
      ]) }} as _airbyte_unique_key,
      id,
      currency,
      new_column,
      date,
      timestamp_col,
      HKD_special___characters,
      NZD,
      USD,
      date as _airbyte_start_at,
      lag(date) over (
        partition by cast(id as {{ dbt_utils.type_string() }}), currency, cast(NZD as {{ dbt_utils.type_string() }})
        order by
            date is null asc,
            date desc,
            _airbyte_emitted_at desc
      ) as _airbyte_end_at,
      case when row_number() over (
        partition by cast(id as {{ dbt_utils.type_string() }}), currency, cast(NZD as {{ dbt_utils.type_string() }})
        order by
            date is null asc,
            date desc,
            _airbyte_emitted_at desc
      ) = 1 then 1 else 0 end as _airbyte_active_row,
      _airbyte_ab_id,
      _airbyte_emitted_at,
      _airbyte_dedup_exchange_rate_hashid
    from input_data
),
dedup_data as (
    select
        -- we need to ensure de-duplicated rows for merge/update queries
        -- additionally, we generate a unique key for the scd table
        row_number() over (
            partition by
                _airbyte_unique_key,
                _airbyte_start_at,
                _airbyte_emitted_at
            order by _airbyte_active_row desc, _airbyte_ab_id
        ) as _airbyte_row_num,
        {{ dbt_utils.surrogate_key([
          '_airbyte_unique_key',
          '_airbyte_start_at',
          '_airbyte_emitted_at'
        ]) }} as _airbyte_unique_key_scd,
        scd_data.*
    from scd_data
)
select
    _airbyte_unique_key,
    _airbyte_unique_key_scd,
    id,
    currency,
    new_column,
    date,
    timestamp_col,
    HKD_special___characters,
    NZD,
    USD,
    _airbyte_start_at,
    _airbyte_end_at,
    _airbyte_active_row,
    _airbyte_ab_id,
    _airbyte_emitted_at,
    {{ current_timestamp() }} as _airbyte_normalized_at,
    _airbyte_dedup_exchange_rate_hashid
from dedup_data where _airbyte_row_num = 1

