/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.mssql;

import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.protocol.models.AirbyteStream;
import io.airbyte.protocol.models.ConfiguredAirbyteCatalog;
import io.airbyte.protocol.models.ConfiguredAirbyteStream;
import io.airbyte.protocol.models.SyncMode;
import io.debezium.annotation.VisibleForTesting;
import java.util.Properties;
import java.util.stream.Collectors;
import org.codehaus.plexus.util.StringUtils;

public class MssqlCdcHelper {

  // legacy replication method config before version 0.4.0
  // it is an enum with possible values: STANDARD and CDC
  private static final String LEGACY_REPLICATION_FIELD = "replication_method";
  // new replication method config since version 0.4.0
  // it is an oneOf object
  private static final String REPLICATION_FIELD = "replication";
  private static final String REPLICATION_TYPE_FIELD = "replication_type";
  private static final String METHOD_FIELD = "method";
  private static final String CDC_SNAPSHOT_ISOLATION_FIELD = "snapshot_isolation";
  private static final String CDC_DATA_TO_SYNC_FIELD = "data_to_sync";

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

  @VisibleForTesting
  static boolean isCdc(final JsonNode config) {
    // new replication method config since version 0.4.0
    if (config.hasNonNull(LEGACY_REPLICATION_FIELD) && config.get(LEGACY_REPLICATION_FIELD).isObject()) {
      final JsonNode replicationConfig = config.get(LEGACY_REPLICATION_FIELD);
      return ReplicationMethod.valueOf(replicationConfig.get(METHOD_FIELD).asText()) == ReplicationMethod.CDC;
    }
    // legacy replication method config before version 0.4.0
    if (config.hasNonNull(LEGACY_REPLICATION_FIELD) && config.get(LEGACY_REPLICATION_FIELD).isTextual()) {
      return ReplicationMethod.valueOf(config.get(LEGACY_REPLICATION_FIELD).asText()) == ReplicationMethod.CDC;
    }
    if (config.hasNonNull(REPLICATION_FIELD)) {
      final JsonNode replicationConfig = config.get(REPLICATION_FIELD);
      return ReplicationMethod.valueOf(replicationConfig.get(REPLICATION_TYPE_FIELD).asText()) == ReplicationMethod.CDC;
    }

    return false;
  }

  @VisibleForTesting
  static SnapshotIsolation getSnapshotIsolationConfig(final JsonNode config) {
    // new replication method config since version 0.4.0
    if (config.hasNonNull(REPLICATION_FIELD)) {
      final JsonNode replicationConfig = config.get(REPLICATION_FIELD);
      final JsonNode snapshotIsolation = replicationConfig.get(CDC_SNAPSHOT_ISOLATION_FIELD);
      return SnapshotIsolation.from(snapshotIsolation.asText());
    }
    return SnapshotIsolation.SNAPSHOT;
  }

  @VisibleForTesting
  static DataToSync getDataToSyncConfig(final JsonNode config) {
    // new replication method config since version 0.4.0
    if (config.hasNonNull(REPLICATION_FIELD)) {
      final JsonNode replicationConfig = config.get(REPLICATION_FIELD);
      final JsonNode dataToSync = replicationConfig.get(CDC_DATA_TO_SYNC_FIELD);
      return DataToSync.from(dataToSync.asText());
    }
    return DataToSync.EXISTING_AND_NEW;
  }

  static Properties getDebeziumProperties(final JsonNode config, final ConfiguredAirbyteCatalog catalog) {
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

    props.setProperty("schema.include.list", getSchema(catalog));

    return props;
  }

  private static String getSchema(final ConfiguredAirbyteCatalog catalog) {
    return catalog.getStreams().stream()
        .filter(s -> s.getSyncMode() == SyncMode.INCREMENTAL)
        .map(ConfiguredAirbyteStream::getStream)
        .map(AirbyteStream::getNamespace)
        // debezium needs commas escaped to split properly
        .map(x -> StringUtils.escape(x, new char[] {','}, "\\,"))
        .collect(Collectors.joining(","));
  }

}
