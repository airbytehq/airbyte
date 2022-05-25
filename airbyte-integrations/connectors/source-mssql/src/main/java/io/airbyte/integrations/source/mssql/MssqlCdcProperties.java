/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.mssql;

import com.fasterxml.jackson.databind.JsonNode;

import java.util.Properties;

public class MssqlCdcProperties {

  static Properties getDebeziumProperties(final JsonNode config) {
    final Properties props = new Properties();
    props.setProperty("connector.class", "io.debezium.connector.sqlserver.SqlServerConnector");

    // https://debezium.io/documentation/reference/1.4/connectors/sqlserver.html#sqlserver-property-include-schema-changes
    props.setProperty("include.schema.changes", "false");
    // https://debezium.io/documentation/reference/1.4/connectors/sqlserver.html#sqlserver-property-provide-transaction-metadata
    props.setProperty("provide.transaction.metadata", "false");

    props.setProperty("converters", "mssql_converter");
    props.setProperty("mssql_converter.type", "io.airbyte.integrations.debezium.internals.MSSQLConverter");

      final JsonNode replication_config = config.get("replication_method");
      if(replication_config.hasNonNull("replication_method")) {
        final JsonNode cdcMethod = config.get("replication_method");
        if(cdcMethod.hasNonNull("is_snapshot_disabled") &&
                cdcMethod.get("is_snapshot_disabled").asBoolean()) {
          props.setProperty("snapshot.isolation.mode", "read_committed");
        } else {
          // https://docs.microsoft.com/en-us/sql/t-sql/statements/set-transaction-isolation-level-transact-sql?view=sql-server-ver15
          // https://debezium.io/documentation/reference/1.4/connectors/sqlserver.html#sqlserver-property-snapshot-isolation-mode
          // we set this to avoid preventing other (non-Airbyte) transactions from updating table rows while
          // we snapshot
          props.setProperty("snapshot.isolation.mode", "snapshot");
        }
        if(cdcMethod.hasNonNull("is_cdc_only") &&
                cdcMethod.get("is_cdc_only").asBoolean()) {
          props.setProperty("snapshot.mode", "schema_only");
        } else {
          // snapshot config
          // https://debezium.io/documentation/reference/1.4/connectors/sqlserver.html#sqlserver-property-snapshot-mode
          props.setProperty("snapshot.mode", "initial");
        }
      } else {
        props.setProperty("snapshot.isolation.mode", "snapshot");
        props.setProperty("snapshot.mode", "initial");
      }
    return props;
  }

}
