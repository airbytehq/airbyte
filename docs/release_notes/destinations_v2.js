import React, { useState } from "react";
import CodeBlock from "@theme/CodeBlock";

function concatenateRawTableName(namespace, name) {
  let plainConcat = namespace + name;
  // Pretend we always have at least one underscore, so that we never generate `_raw_stream_`
  let longestUnderscoreRun = 1;
  for (let i = 0; i < plainConcat.length; i++) {
    // If we've found an underscore, count the number of consecutive underscores
    let underscoreRun = 0;
    while (i < plainConcat.length && plainConcat.charAt(i) === "_") {
      underscoreRun++;
      i++;
    }
    longestUnderscoreRun = Math.max(longestUnderscoreRun, underscoreRun);
  }
  return (
    namespace + "_raw" + "_".repeat(longestUnderscoreRun + 1) + "stream_" + name
  );
}

// Taken from StandardNameTransformer
function convertStreamName(str) {
  return str
    .normalize("NFKD")
    .replaceAll(/\p{M}/gu, "")
    .replaceAll(/\s+/g, "_")
    .replaceAll(/[^A-Za-z0-9_]/g, "_");
}

export const BigQueryMigrationGenerator = () => {
  // See BigQuerySQLNameTransformer
  function bigqueryConvertStreamName(str) {
    str = convertStreamName(str);
    if (str.charAt(0).match(/[A-Za-z_]/)) {
      return str;
    } else {
      return "_" + str;
    }
  }
  function escapeNamespace(namespace) {
    namespace = convertStreamName(namespace);
    if (!namespace.charAt(0).match(/[A-Za-z0-9]/)) {
      namespace = "n" + namespace;
    }
    return namespace;
  }

  function generateSql(og_namespace, new_namespace, name, raw_dataset) {
    let v2RawTableName =
      "`" +
      bigqueryConvertStreamName(concatenateRawTableName(new_namespace, name)) +
      "`";
    let v1namespace = "`" + escapeNamespace(og_namespace) + "`";
    let v1name = "`" + bigqueryConvertStreamName("_airbyte_raw_" + name) + "`";
    return `CREATE SCHEMA IF NOT EXISTS ${raw_dataset};
CREATE OR REPLACE TABLE \`${raw_dataset}\`.${v2RawTableName} (
  _airbyte_raw_id STRING,
  _airbyte_extracted_at TIMESTAMP,
  _airbyte_loaded_at TIMESTAMP,
  _airbyte_data JSON)
PARTITION BY DATE(_airbyte_extracted_at)
CLUSTER BY _airbyte_extracted_at
AS (
    SELECT
        _airbyte_ab_id AS _airbyte_raw_id,
        _airbyte_emitted_at AS _airbyte_extracted_at,
        CAST(NULL AS TIMESTAMP) AS _airbyte_loaded_at,
        PARSE_JSON(_airbyte_data) AS _airbyte_data
    FROM ${v1namespace}.${v1name}
)`;
  }

  return (
    <MigrationGenerator destination="bigquery" generateSql={generateSql} />
  );
};

export const SnowflakeMigrationGenerator = () => {
  // See SnowflakeSQLNameTransformer
  function snowflakeConvertStreamName(str) {
    str = convertStreamName(str);
    if (str.charAt(0).match(/[A-Za-z_]/)) {
      return str;
    } else {
      return "_" + str;
    }
  }
  function generateSql(og_namespace, new_namespace, name, raw_schema) {
    let v2RawTableName =
      '"' + concatenateRawTableName(new_namespace, name) + '"';
    let v1namespace = snowflakeConvertStreamName(og_namespace);
    let v1name = snowflakeConvertStreamName("_airbyte_raw_" + name);
    return `CREATE SCHEMA IF NOT EXISTS "${raw_schema}";
CREATE OR REPLACE TABLE "${raw_schema}".${v2RawTableName} (
  "_airbyte_raw_id" STRING NOT NULL PRIMARY KEY,
  "_airbyte_extracted_at" TIMESTAMP_TZ DEFAULT CURRENT_TIMESTAMP(),
  "_airbyte_loaded_at" TIMESTAMP_TZ,
  "_airbyte_data" VARIANT)
AS (
    SELECT
        _airbyte_ab_id AS "_airbyte_raw_id",
        _airbyte_emitted_at AS "_airbyte_extracted_at",
        CAST(NULL AS TIMESTAMP_TZ) AS "_airbyte_loaded_at",
        _airbyte_data AS "_airbyte_data"
    FROM ${v1namespace}.${v1name}
)`;
  }
  return (
    <MigrationGenerator destination="snowflake" generateSql={generateSql} />
  );
};

export const RedshiftMigrationGenerator = () => {
  // See RedshiftSQLNameTransformer
  function redshiftConvertStreamName(str) {
    str = convertStreamName(str);
    if (str.charAt(0).match(/[A-Za-z_]/)) {
      return str;
    } else {
      return "_" + str;
    }
  }
  function generateSql(og_namespace, new_namespace, name, raw_schema) {
    let v2RawTableName =
      '"' + concatenateRawTableName(new_namespace, name) + '"';
    let v1namespace = redshiftConvertStreamName(og_namespace);
    let v1name = redshiftConvertStreamName("_airbyte_raw_" + name);
    return `CREATE SCHEMA IF NOT EXISTS "${raw_schema}";
DROP TABLE IF EXISTS "${raw_schema}".${v2RawTableName};
CREATE TABLE "${raw_schema}".${v2RawTableName} (
  "_airbyte_raw_id" VARCHAR(36) NOT NULL PRIMARY KEY
  , "_airbyte_extracted_at" TIMESTAMPTZ DEFAULT NOW()
  , "_airbyte_loaded_at" TIMESTAMPTZ
  , "_airbyte_data" SUPER
);
INSERT INTO "${raw_schema}".${v2RawTableName} (
    SELECT
        _airbyte_ab_id AS "_airbyte_raw_id",
        _airbyte_emitted_at AS "_airbyte_extracted_at",
        CAST(NULL AS TIMESTAMPTZ) AS "_airbyte_loaded_at",
        _airbyte_data AS "_airbyte_data"
    FROM ${v1namespace}.${v1name}
);`;
  }
  return (
    <MigrationGenerator destination="redshift" generateSql={generateSql} />
  );
};

export const PostgresMigrationGenerator = () => {
  // StandardNameTransformer + identifier should start with a letter or an underscore
  function postgresConvertStreamName(str) {
    str = convertStreamName(str);
    if (str.charAt(0).match(/[A-Za-z_]/)) {
      return str;
    } else {
      return "_" + str;
    }
  }
  function generateSql(og_namespace, new_namespace, name, raw_schema) {
    let v2RawTableName =
        concatenateRawTableName(new_namespace, name).toLowerCase();
    let v1namespace = postgresConvertStreamName(og_namespace);
    let v1name = postgresConvertStreamName("_airbyte_raw_" + name).toLowerCase();
    return `CREATE SCHEMA IF NOT EXISTS "${raw_schema}";
DROP TABLE IF EXISTS "${raw_schema}".${v2RawTableName};
CREATE TABLE "${raw_schema}".${v2RawTableName} (
  "_airbyte_raw_id" VARCHAR(36) NOT NULL PRIMARY KEY
  , "_airbyte_extracted_at" TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
  , "_airbyte_loaded_at" TIMESTAMP WITH TIME ZONE DEFAULT NULL
  , "_airbyte_data" JSONB
);
INSERT INTO "${raw_schema}".${v2RawTableName} (
    SELECT
        _airbyte_ab_id AS "_airbyte_raw_id",
        _airbyte_emitted_at AS "_airbyte_extracted_at",
        CAST(NULL AS TIMESTAMP WITH TIME ZONE) AS "_airbyte_loaded_at",
        _airbyte_data AS "_airbyte_data"
    FROM ${v1namespace}.${v1name}
);`;
  }
  return (
      <MigrationGenerator destination="postgres" generateSql={generateSql} />
  );
};

export const MigrationGenerator = ({ destination, generateSql }) => {
  const defaultMessage = `Enter your stream's name and namespace to see the SQL output.
If your stream has no namespace, take the default value from the destination connector's settings.`;
  const [message, updateMessage] = useState({
    message: defaultMessage,
    language: "text",
  });
  function updateSql(event) {
    let og_namespace = document.getElementById(
      "og_stream_namespace_" + destination
    ).value;
    let new_namespace = document.getElementById(
      "new_stream_namespace_" + destination
    ).value;
    let name = document.getElementById("stream_name_" + destination).value;
    var raw_dataset = document.getElementById(
      "raw_dataset_" + destination
    ).value;
    if (raw_dataset === "") {
      raw_dataset = "airbyte_internal";
    }
    let sql = generateSql(og_namespace, new_namespace, name, raw_dataset);
    if ([og_namespace, new_namespace, name].every((text) => text != "")) {
      updateMessage({
        message: sql,
        language: "sql",
      });
    } else {
      updateMessage({
        message: defaultMessage,
        language: "text",
      });
    }
  }

  return (
    <div>
      <label>Original Stream namespace </label>
      <input
        type="text"
        id={"og_stream_namespace_" + destination}
        onChange={updateSql}
      />
      <br />
      <label>New Stream namespace (to avoid overwriting)</label>
      <input
        type="text"
        id={"new_stream_namespace_" + destination}
        onChange={updateSql}
      />
      <br />
      <label>Stream name </label>
      <input
        type="text"
        id={"stream_name_" + destination}
        onChange={updateSql}
      />
      <br />
      <label>
        Raw table dataset/schema (defaults to <code>airbyte_internal</code>){" "}
      </label>
      <input
        type="text"
        id={"raw_dataset_" + destination}
        onChange={updateSql}
      />
      <br />
      <CodeBlock
        id={"sql_output_block_" + destination}
        language={message["language"]}
      >
        {message["message"]}
      </CodeBlock>
    </div>
  );
};
