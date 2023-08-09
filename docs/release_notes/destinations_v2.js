import React from 'react';

function concatenateRawTableName(namespace, name) {
  let plainConcat = namespace + name;
  // Pretend we always have at least one underscore, so that we never generate `_raw_stream_`
  let longestUnderscoreRun = 1;
  for (let i = 0; i < plainConcat.length; i++) {
    // If we've found an underscore, count the number of consecutive underscores
    let underscoreRun = 0;
    while (i < plainConcat.length && plainConcat.charAt(i) === '_') {
        underscoreRun++;
        i++;
    }
    longestUnderscoreRun = Math.max(longestUnderscoreRun, underscoreRun);
  }
  return namespace + "_raw" + "_".repeat(longestUnderscoreRun + 1) + "stream_" + name;
}

function setSql(namespace, name, destination, sql, defaultMessage) {
  var output;
  if (namespace != "" && name != "") {
    output = sql;
  } else {
    output = defaultMessage;
  }
  document.getElementById("sql_output_block_" + destination).innerHTML = output;
}

const SqlOutput = ({ destination, defaultMessage }) => {
  return (
    <pre id={ "sql_output_block_" + destination }>
      { defaultMessage }
    </pre>
  );
};

export const BigQueryMigrationGenerator = () => {
  const defaultMessage =
`Enter your stream's name and namespace to generate a SQL statement.
If your stream has no namespace, take the default value from the destination connector's settings.
You may need to tweak the sql statement if your stream name/namespace contain unusual characters.`;
  function updateSql(event) {
    let namespace = document.getElementById("stream_namespace_bigquery").value;
    let name = document.getElementById("stream_name_bigquery").value;
    let v2RawTableName = '`' + concatenateRawTableName(namespace, name) + '`';
    let v1RawTableName = '`' + namespace + '`.`_airbyte_raw_' + name + '`';
    let sql =
`CREATE OR REPLACE TABLE \`airbyte_internal\`.${v2RawTableName} (
  _airbyte_raw_id STRING NOT NULL,
  _airbyte_data JSON NOT NULL,
  _airbyte_extracted_at TIMESTAMP NOT NULL,
  _airbyte_loaded_at TIMESTAMP)
PARTITION BY DATE(_airbyte_extracted_at)
CLUSTER BY _airbyte_extracted_at
AS (
    SELECT
        _airbyte_ab_id AS _airbyte_raw_id,
        PARSE_JSON(_airbyte_data) AS _airbyte_data,
        _airbyte_emitted_at AS _airbyte_extracted_at,
        CAST(NULL AS TIMESTAMP) AS _airbyte_loaded_at
    FROM ${v1RawTableName}
)`;
    setSql(namespace, name, "bigquery", sql, defaultMessage);
  }
  return (
    <div>
      <label>Stream namespace </label>
      <input type="text" id="stream_namespace_bigquery" name="stream_namespace" onChange={ updateSql }/><br/>
      <label>Stream name </label>
      <input type="text" id="stream_name_bigquery" name="stream_name" onChange={ updateSql }/><br/>
      <SqlOutput destination="bigquery" defaultMessage={ defaultMessage }/>
    </div>
  )
}

export const SnowflakeMigrationGenerator = () => {
  const defaultMessage =
`Enter your stream's name and namespace to see the SQL output.
If your stream has no namespace, take the default value from the destination connector's settings.
You may need to tweak the sql statement if your stream name/namespace contain unusual characters.`;
  function updateSql(event) {
    let namespace = document.getElementById("stream_namespace_snowflake").value;
    let name = document.getElementById("stream_name_snowflake").value;
    let v2RawTableName = '"' + concatenateRawTableName(namespace, name) + '"';
    let v1RawTableName = namespace + '._airbyte_raw_' + name;
    let sql =
`CREATE OR REPLACE TABLE "airbyte_internal".${v2RawTableName} (
  "_airbyte_raw_id" STRING NOT NULL,
  "_airbyte_data" JSON NOT NULL,
  "_airbyte_extracted_at" TIMESTAMP NOT NULL,
  "_airbyte_loaded_at" TIMESTAMP)
PARTITION BY DATE("_airbyte_extracted_at")
CLUSTER BY "_airbyte_extracted_at"
AS (
    SELECT
        _airbyte_ab_id AS "_airbyte_raw_id",
        PARSE_JSON(_airbyte_data) AS "_airbyte_data",
        _airbyte_emitted_at AS "_airbyte_extracted_at",
        CAST(NULL AS TIMESTAMP) AS "_airbyte_loaded_at"
    FROM ${v1RawTableName}
)`
    setSql(namespace, name, "snowflake", sql, defaultMessage)
  }
  return (
    <div>
      <label>Stream namespace </label>
      <input type="text" id="stream_namespace_snowflake" name="stream_namespace" onChange={ updateSql }/><br/>
      <label>Stream name </label>
      <input type="text" id="stream_name_snowflake" name="stream_name" onChange={ updateSql }/><br/>
      <SqlOutput destination="snowflake" defaultMessage={ defaultMessage }/>
    </div>
  )
}
