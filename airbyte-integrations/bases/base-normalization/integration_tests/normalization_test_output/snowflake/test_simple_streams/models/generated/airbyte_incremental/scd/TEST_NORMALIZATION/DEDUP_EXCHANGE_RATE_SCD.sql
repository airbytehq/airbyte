{{ config(
    cluster_by = ["_AIRBYTE_ACTIVE_ROW", "_AIRBYTE_UNIQUE_KEY_SCD", "_AIRBYTE_EMITTED_AT"],
    unique_key = "_AIRBYTE_UNIQUE_KEY_SCD",
    schema = "TEST_NORMALIZATION",
    post_hook = ["
                        {%
                        set final_table_relation = adapter.get_relation(
                                database=this.database,
                                schema=this.schema,
                                identifier='DEDUP_EXCHANGE_RATE'
                            )
                        %}
                        {#
                        If the final table doesn't exist, then obviously we can't delete anything from it.
                        Also, after a reset, the final table is created without the _airbyte_unique_key column (this column is created during the first sync)
                        So skip this deletion if the column doesn't exist. (in this case, the table is guaranteed to be empty anyway)
                        #}
                        {%
                        if final_table_relation is not none and '_AIRBYTE_UNIQUE_KEY' in adapter.get_columns_in_relation(final_table_relation)|map(attribute='name')
                        %}
                        -- Delete records which are no longer active:
                        -- 1. Find the records which are being updated by querying the _scd_new_data model
                        -- 2. Then join that against the SCD model to find the records which have no row with _airbyte_active_row = 1
                        -- We can't just delete all the modified_ids from final_table because those records might still be active, but not included
                        -- in the most recent increment (i.e. the final table model would not re-insert them, so the data would be incorrectly lost).
                        -- In fact, there's no guarantee that the active record is included in the previous_active_scd_data CTE either,
                        -- so we _must_ join against the entire SCD table to find the active row for each record.
                        -- We're using a subquery because not all destinations support CTEs in DELETE statements (c.f. Snowflake).
                        delete from {{ final_table_relation }} where {{ final_table_relation }}._AIRBYTE_UNIQUE_KEY in (
                            with modified_ids as (
                                select
                                    {{ dbt_utils.surrogate_key([
                                            'ID',
                                            'CURRENCY',
                                            'NZD',
                                    ]) }} as _AIRBYTE_UNIQUE_KEY
                                from {{ ref('DEDUP_EXCHANGE_RATE_SCD_NEW_DATA') }}
                                where 1=1
                                    {{ incremental_clause('_AIRBYTE_EMITTED_AT', this.schema + '.' + adapter.quote('DEDUP_EXCHANGE_RATE')) }}
                            ),
                            scd_active_rows as (
                                select scd_table.* from {{ this }} scd_table
                                inner join modified_ids on scd_table._AIRBYTE_UNIQUE_KEY = modified_ids._AIRBYTE_UNIQUE_KEY
                                where _AIRBYTE_ACTIVE_ROW =  1
                            )
                            select modified_ids._AIRBYTE_UNIQUE_KEY from scd_active_rows
                            right outer join modified_ids on modified_ids._AIRBYTE_UNIQUE_KEY = scd_active_rows._AIRBYTE_UNIQUE_KEY
                            group by modified_ids._AIRBYTE_UNIQUE_KEY
                            having count(scd_active_rows._AIRBYTE_UNIQUE_KEY) = 0
                        )
                        {% else %}
                        -- We have to have a non-empty query, so just do a noop delete
                        delete from {{ this }} where 1=0
                        {% endif %}
                        ","drop view {{ ref('DEDUP_EXCHANGE_RATE_SCD_NEW_DATA') }}","drop view _AIRBYTE_TEST_NORMALIZATION.DEDUP_EXCHANGE_RATE_STG"],
    tags = [ "top-level" ]
) }}
-- depends on: {{ ref('DEDUP_EXCHANGE_RATE_SCD_NEW_DATA') }}
with
{% if is_incremental() %}
new_data_ids as (
    -- build a subset of _AIRBYTE_UNIQUE_KEY from rows that are new
    select distinct
        {{ dbt_utils.surrogate_key([
            'ID',
            'CURRENCY',
            'NZD',
        ]) }} as _AIRBYTE_UNIQUE_KEY
    from {{ ref('DEDUP_EXCHANGE_RATE_SCD_NEW_DATA') }}
),
empty_new_data as (
    -- build an empty table to only keep the table's column types
    select * from {{ ref('DEDUP_EXCHANGE_RATE_SCD_NEW_DATA') }} where 1 = 0
),
previous_active_scd_data as (
    -- retrieve "incomplete old" data that needs to be updated with an end date because of new changes
    select
        {{ star_intersect(ref('DEDUP_EXCHANGE_RATE_STG'), this, from_alias='inc_data', intersect_alias='this_data') }}
    from {{ this }} as this_data
    -- make a join with new_data using primary key to filter active data that need to be updated only
    join new_data_ids on this_data._AIRBYTE_UNIQUE_KEY = new_data_ids._AIRBYTE_UNIQUE_KEY
    -- force left join to NULL values (we just need to transfer column types only for the star_intersect macro on schema changes)
    left join empty_new_data as inc_data on this_data._AIRBYTE_AB_ID = inc_data._AIRBYTE_AB_ID
    where _AIRBYTE_ACTIVE_ROW = 1
),
input_data as (
    select {{ dbt_utils.star(ref('DEDUP_EXCHANGE_RATE_STG')) }} from {{ ref('DEDUP_EXCHANGE_RATE_SCD_NEW_DATA') }}
    union all
    select {{ dbt_utils.star(ref('DEDUP_EXCHANGE_RATE_STG')) }} from previous_active_scd_data
),
{% else %}
input_data as (
    select *
    from {{ ref('DEDUP_EXCHANGE_RATE_STG')  }}
    -- DEDUP_EXCHANGE_RATE from {{ source('TEST_NORMALIZATION', '_AIRBYTE_RAW_DEDUP_EXCHANGE_RATE') }}
),
{% endif %}
scd_data as (
    -- SQL model to build a Type 2 Slowly Changing Dimension (SCD) table for each record identified by their primary key
    select
      {{ dbt_utils.surrogate_key([
      'ID',
      'CURRENCY',
      'NZD',
      ]) }} as _AIRBYTE_UNIQUE_KEY,
      ID,
      CURRENCY,
      DATE,
      TIMESTAMP_COL,
      {{ adapter.quote('HKD@spéçiäl & characters') }},
      HKD_SPECIAL___CHARACTERS,
      NZD,
      USD,
      DATE as _AIRBYTE_START_AT,
      lag(DATE) over (
        partition by ID, CURRENCY, cast(NZD as {{ dbt_utils.type_string() }})
        order by
            DATE is null asc,
            DATE desc,
            _AIRBYTE_EMITTED_AT desc
      ) as _AIRBYTE_END_AT,
      case when row_number() over (
        partition by ID, CURRENCY, cast(NZD as {{ dbt_utils.type_string() }})
        order by
            DATE is null asc,
            DATE desc,
            _AIRBYTE_EMITTED_AT desc
      ) = 1 then 1 else 0 end as _AIRBYTE_ACTIVE_ROW,
      _AIRBYTE_AB_ID,
      _AIRBYTE_EMITTED_AT,
      _AIRBYTE_DEDUP_EXCHANGE_RATE_HASHID
    from input_data
),
dedup_data as (
    select
        -- we need to ensure de-duplicated rows for merge/update queries
        -- additionally, we generate a unique key for the scd table
        row_number() over (
            partition by
                _AIRBYTE_UNIQUE_KEY,
                _AIRBYTE_START_AT,
                _AIRBYTE_EMITTED_AT
            order by _AIRBYTE_ACTIVE_ROW desc, _AIRBYTE_AB_ID
        ) as _AIRBYTE_ROW_NUM,
        {{ dbt_utils.surrogate_key([
          '_AIRBYTE_UNIQUE_KEY',
          '_AIRBYTE_START_AT',
          '_AIRBYTE_EMITTED_AT'
        ]) }} as _AIRBYTE_UNIQUE_KEY_SCD,
        scd_data.*
    from scd_data
)
select
    _AIRBYTE_UNIQUE_KEY,
    _AIRBYTE_UNIQUE_KEY_SCD,
    ID,
    CURRENCY,
    DATE,
    TIMESTAMP_COL,
    {{ adapter.quote('HKD@spéçiäl & characters') }},
    HKD_SPECIAL___CHARACTERS,
    NZD,
    USD,
    _AIRBYTE_START_AT,
    _AIRBYTE_END_AT,
    _AIRBYTE_ACTIVE_ROW,
    _AIRBYTE_AB_ID,
    _AIRBYTE_EMITTED_AT,
    {{ current_timestamp() }} as _AIRBYTE_NORMALIZED_AT,
    _AIRBYTE_DEDUP_EXCHANGE_RATE_HASHID
from dedup_data where _AIRBYTE_ROW_NUM = 1

