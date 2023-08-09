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

const SqlOutput = ({ destination, defaultMessage }) => {
  return (
    <pre id={ "sql_output_block_" + destination }>
      { defaultMessage }
    </pre>
  );
};

export const BigQueryMigrationGenerator = () => {
  function generateSql(namespace, name) {
    let v2RawTableName = '`' + concatenateRawTableName(namespace, name) + '`';
    let v1RawTableName = '`' + namespace + '`.`_airbyte_raw_' + name + '`';
    return `CREATE OR REPLACE TABLE \`airbyte_internal\`.${v2RawTableName} (
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
  }
  return (
    <MigrationGenerator destination="bigquery" generateSql={generateSql}/>
  );
}

export const SnowflakeMigrationGenerator = () => {
  function generateSql(namespace, name) {
    let v2RawTableName = '"' + concatenateRawTableName(namespace, name) + '"';
    let v1RawTableName = namespace + '._airbyte_raw_' + name;
    return `CREATE OR REPLACE TABLE "airbyte_internal".${v2RawTableName} (
  "_airbyte_raw_id" STRING NOT NULL,
  "_airbyte_data" JSON NOT NULL,
  "_airbyte_extracted_at" TIMESTAMP NOT NULL,
  "_airbyte_loaded_at" TIMESTAMP)
PARTITION BY DATE("_airbyte_extracted_at")
CLUSTER BY "_airbyte_extracted_at"
AS (
    SELECT
        _airbyte_ab_id AS "_airbyte_raw_id",
        _airbyte_data AS "_airbyte_data",
        _airbyte_emitted_at AS "_airbyte_extracted_at",
        CAST(NULL AS TIMESTAMP) AS "_airbyte_loaded_at"
    FROM ${v1RawTableName}
)`;
  }
  return (
    <MigrationGenerator destination="snowflake" generateSql={generateSql}/>
  );
}

export const MigrationGenerator = ({destination, generateSql}) => {
  const defaultMessage =
`Enter your stream's name and namespace to see the SQL output.
If your stream has no namespace, take the default value from the destination connector's settings.`;
  function updateSql(event) {
    let namespace = document.getElementById("stream_namespace_" + destination).value;
    let name = document.getElementById("stream_name_" + destination).value;
    let sql = generateSql(namespace, name);
    var output;
    if (namespace != "" && name != "") {
      output = sql;
    } else {
      output = defaultMessage;
    }
    document.getElementById("sql_output_block_" + destination).innerHTML = output;
  }
  return (
    <div>
      <label>Stream namespace </label>
      <input type="text" id={"stream_namespace_" + destination} onChange={ updateSql }/><br/>
      <label>Stream name </label>
      <input type="text" id={"stream_name_" + destination} onChange={ updateSql }/><br/>
      <SqlOutput destination={destination} defaultMessage={ defaultMessage }/>
    </div>
  );
}
