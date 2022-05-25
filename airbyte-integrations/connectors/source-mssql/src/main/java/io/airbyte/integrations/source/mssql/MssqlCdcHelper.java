/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.mssql;

import com.fasterxml.jackson.databind.JsonNode;
import io.debezium.annotation.VisibleForTesting;
import java.util.Properties;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

/**
 * Before version 0.4.0, the "replication_method" parameter is just an enum with two possible
 * values: STANDARD and CDC. Debezium "snapshot.mode" defaults "snapshot", and
 * "snapshot.isolation.mode" defaults to "snapshot".
 * <p/>
 * Version 0.4.0 changed the "replication_method" parameter to an "oneOf" field. The CDC replication
 * type has more details configurations for Debezium.
 */
public class MssqlCdcHelper {

  public enum ReplicationMethod {
    STANDARD,
    CDC
  }

  /**
   * The default "SNAPSHOT" mode can prevent other (non-Airbyte) transactions from updating table rows
   * while we snapshot. References:
   * https://docs.microsoft.com/en-us/sql/t-sql/statements/set-transaction-isolation-level-transact-sql?view=sql-server-ver15
   * https://debezium.io/documentation/reference/1.4/connectors/sqlserver.html#sqlserver-property-snapshot-isolation-mode
   */
  public enum SnapshotIsolation {

    SNAPSHOT("Snapshot", "snapshot"),
    READ_COMMITTED("Read Committed", "read_committed");

    private final String snapshotIsolationLevel;
    private final String debeziumIsolationMode;

    SnapshotIsolation(final String snapshotIsolationLevel, final String debeziumIsolationMode) {
      this.snapshotIsolationLevel = snapshotIsolationLevel;
      this.debeziumIsolationMode = debeziumIsolationMode;
    }

    public String getDebeziumIsolationMode() {
      return debeziumIsolationMode;
    }

    public static SnapshotIsolation from(final String jsonValue) {
      for (final SnapshotIsolation value : values()) {
        if (value.snapshotIsolationLevel.equalsIgnoreCase(jsonValue)) {
          return value;
        }
      }
      throw new IllegalArgumentException("Unexpected snapshot isolation level: " + jsonValue);
    }

  }

  // https://debezium.io/documentation/reference/1.4/connectors/sqlserver.html#sqlserver-property-snapshot-mode
  public enum DataToSync {

    EXISTING_AND_NEW("Existing and New", "initial"),
    NEW_CHANGES_ONLY("New Changes Only", "schema_only");

    private final String dataToSyncConfig;
    private final String debeziumSnapshotMode;

    DataToSync(final String value, final String debeziumSnapshotMode) {
      this.dataToSyncConfig = value;
      this.debeziumSnapshotMode = debeziumSnapshotMode;
    }

    public String getDebeziumSnapshotMode() {
      return debeziumSnapshotMode;
    }

    public static DataToSync from(final String value) {
      for (final DataToSync s : values()) {
        if (s.dataToSyncConfig.equalsIgnoreCase(value)) {
          return s;
        }
      }
      throw new IllegalArgumentException("Unexpected data to sync setting: " + value);
    }

  }

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

  @VisibleForTesting
  static SnapshotIsolation getSnapshotIsolationConfig(final JsonNode config) {
    // legacy replication method config before version 0.4.0
    final JsonNode replicationMethod = config.get("replication_method");
    if (replicationMethod == null || replicationMethod.isNull()) {
      return SnapshotIsolation.SNAPSHOT;
    }
    // new replication method config since version 0.4.0
    final JsonNode snapshotIsolation = replicationMethod.get("snapshot_isolation");
    if (snapshotIsolation == null || snapshotIsolation.isNull()) {
      return SnapshotIsolation.SNAPSHOT;
    }
    return SnapshotIsolation.from(snapshotIsolation.asText());
  }

  @VisibleForTesting
  static DataToSync getDataToSyncConfig(final JsonNode config) {
    // legacy replication method config before version 0.4.0
    final JsonNode replicationMethod = config.get("replication_method");
    if (replicationMethod == null || replicationMethod.isNull()) {
      return DataToSync.EXISTING_AND_NEW;
    }
    // new replication method config since version 0.4.0
    final JsonNode dataToSync = replicationMethod.get("data_to_sync");
    if (dataToSync == null || dataToSync.isNull()) {
      return DataToSync.EXISTING_AND_NEW;
    }
    return DataToSync.from(dataToSync.asText());
  }

  @VisibleForTesting
  static Properties getDebeziumProperties(final JsonNode config) {
    final Properties props = new Properties();
    props.setProperty("connector.class", "io.debezium.connector.sqlserver.SqlServerConnector");

    // https://debezium.io/documentation/reference/1.4/connectors/sqlserver.html#sqlserver-property-include-schema-changes
    props.setProperty("include.schema.changes", "false");
    // https://debezium.io/documentation/reference/1.4/connectors/sqlserver.html#sqlserver-property-provide-transaction-metadata
    props.setProperty("provide.transaction.metadata", "false");

    props.setProperty("converters", "mssql_converter");
    props.setProperty("mssql_converter.type", "io.airbyte.integrations.debezium.internals.MSSQLConverter");

    props.setProperty("snapshot.mode", getDataToSyncConfig(config).getDebeziumSnapshotMode());
    props.setProperty("snapshot.isolation.mode", getSnapshotIsolationConfig(config).getDebeziumIsolationMode());

    return props;
  }

}
