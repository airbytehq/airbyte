import React from 'react';

import get_default_cache from "../../../airbyte-lib/docs/generated/airbyte_lib/functions/get_default_cache.html";
import new_local_cache from "../../../airbyte-lib/docs/generated/airbyte_lib/functions/new_local_cache.html";
import get_secret from "../../../airbyte-lib/docs/generated/airbyte_lib/functions/get_secret.html";

const functions = {
  "get_default_cache": duckdb_cache,
  "new_local_cache": postgres_cache,
  "get_secret": snowflake_cache,
}
;

export default function AirbyteLibClassReference({ function_name }) {
  return <>
    <div dangerouslySetInnerHTML={{ __html: functions[function_name] }} />
  </>
}
;
