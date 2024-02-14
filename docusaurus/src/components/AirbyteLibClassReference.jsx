import React from 'react';

import duckdb_cache from "../../../airbyte-lib/docs/generated/airbyte_lib/classes/DuckDBCache.html";
import postgres_cache from "../../../airbyte-lib/docs/generated/airbyte_lib/classes/PostgresCache.html";
import snowflake_cache from "../../../airbyte-lib/docs/generated/airbyte_lib/classes/SnowflakeCache.html";

const classes = {
  "DuckDBCache": duckdb_cache,
  "PostgresCache": postgres_cache,
  "SnowflakeCache": snowflake_cache,
}
;

export default function AirbyteLibClassReference({ class_name }) {
  return <>
    <div dangerouslySetInnerHTML={{ __html: classes[class_name] }} />
  </>
}
;
