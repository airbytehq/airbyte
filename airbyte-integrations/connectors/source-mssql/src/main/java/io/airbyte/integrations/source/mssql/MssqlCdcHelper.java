/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.mssql;

import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.integrations.source.mssql.MssqlSource.ReplicationMethod;
import io.debezium.annotation.VisibleForTesting;
import java.util.Properties;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class MssqlCdcHelper {

  private static final Logger LOGGER = LoggerFactory.getLogger(MssqlCdcHelper.class);

  @VisibleForTesting
  static boolean isCdc(final JsonNode config) {
    final JsonNode replicationMethod = config.get("replication_method");

    // legacy replication method config before version 0.4.0
    if (replicationMethod.isTextual()) {
      return ReplicationMethod.valueOf(replicationMethod.asText()) == ReplicationMethod.CDC;
    }

    // new replication method config since version 0.4.0
    if (replicationMethod.isObject()) {
      return replicationMethod.hasNonNull("replication_type") &&
          ReplicationMethod.valueOf(replicationMethod.get("replication_type").asText()) == ReplicationMethod.CDC;
    }

    LOGGER.warn("Unexpected replication method: {}, default to non CDC", replicationMethod);
    return false;
  }

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
    if (replication_config.hasNonNull("replication_method")) {
      final JsonNode cdcMethod = config.get("replication_method");
      if (cdcMethod.hasNonNull("is_snapshot_disabled") &&
          cdcMethod.get("is_snapshot_disabled").asBoolean()) {
        props.setProperty("snapshot.isolation.mode", "read_committed");
      } else {
        // https://docs.microsoft.com/en-us/sql/t-sql/statements/set-transaction-isolation-level-transact-sql?view=sql-server-ver15
        // https://debezium.io/documentation/reference/1.4/connectors/sqlserver.html#sqlserver-property-snapshot-isolation-mode
        // we set this to avoid preventing other (non-Airbyte) transactions from updating table rows while
        // we snapshot
        props.setProperty("snapshot.isolation.mode", "snapshot");
      }
      if (cdcMethod.hasNonNull("is_cdc_only") &&
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
