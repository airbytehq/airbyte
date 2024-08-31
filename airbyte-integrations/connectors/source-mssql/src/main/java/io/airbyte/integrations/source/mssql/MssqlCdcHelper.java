/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.mssql;

import com.fasterxml.jackson.databind.JsonNode;
import com.google.common.annotations.VisibleForTesting;
import io.airbyte.cdk.db.jdbc.JdbcDatabase;
import io.airbyte.cdk.db.jdbc.JdbcUtils;
import io.airbyte.protocol.models.v0.AirbyteStream;
import io.airbyte.protocol.models.v0.ConfiguredAirbyteCatalog;
import io.airbyte.protocol.models.v0.ConfiguredAirbyteStream;
import io.airbyte.protocol.models.v0.SyncMode;
import java.time.Duration;
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

  private static final Duration HEARTBEAT_INTERVAL = Duration.ofSeconds(10L);

  // Test execution latency is lower when heartbeats are more frequent.
  private static final Duration HEARTBEAT_INTERVAL_IN_TESTS = Duration.ofSeconds(1L);

  public enum ReplicationMethod {
    STANDARD,
    CDC
  }

  @VisibleForTesting
  static boolean isCdc(final JsonNode config) {
    if (config != null) {
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
    }

    return false;
  }

  public static Properties getDebeziumProperties(final JdbcDatabase database, final ConfiguredAirbyteCatalog catalog, final boolean isSnapshot) {
    final JsonNode config = database.getSourceConfig();
    final JsonNode dbConfig = database.getDatabaseConfig();

    final Properties props = new Properties();
    props.setProperty("connector.class", "io.debezium.connector.sqlserver.SqlServerConnector");

    // https://debezium.io/documentation/reference/2.2/connectors/sqlserver.html#sqlserver-property-include-schema-changes
    props.setProperty("include.schema.changes", "false");
    // https://debezium.io/documentation/reference/2.2/connectors/sqlserver.html#sqlserver-property-provide-transaction-metadata
    props.setProperty("provide.transaction.metadata", "false");

    props.setProperty("converters", "mssql_converter");

    props.setProperty("mssql_converter.type", MssqlDebeziumConverter.class.getName());

    // If new stream(s) are added after a previously successful sync,
    // the snapshot.mode needs to be initial_only since we don't want to continue streaming changes
    // https://debezium.io/documentation/reference/stable/connectors/sqlserver.html#sqlserver-property-snapshot-mode
    if (isSnapshot) {
      props.setProperty("snapshot.mode", "initial_only");
    } else {
      // If not in snapshot mode, initial will make sure that a snapshot is taken if the transaction log
      // is rotated out. This will also end up read streaming changes from the transaction_log.
      props.setProperty("snapshot.mode", "when_needed");
    }

    props.setProperty("snapshot.isolation.mode", "read_committed");

    props.setProperty("schema.include.list", getSchema(catalog));
    props.setProperty("database.names", config.get(JdbcUtils.DATABASE_KEY).asText());

    final Duration heartbeatInterval =
        (database.getSourceConfig().has("is_test") && database.getSourceConfig().get("is_test").asBoolean())
            ? HEARTBEAT_INTERVAL_IN_TESTS
            : HEARTBEAT_INTERVAL;
    props.setProperty("heartbeat.interval.ms", Long.toString(heartbeatInterval.toMillis()));

    if (config.has("ssl_method")) {
      final JsonNode sslConfig = config.get("ssl_method");
      final String sslMethod = sslConfig.get("ssl_method").asText();
      if ("unencrypted".equals(sslMethod)) {
        props.setProperty("database.encrypt", "false");
        props.setProperty("driver.trustServerCertificate", "true");
      } else if ("encrypted_trust_server_certificate".equals(sslMethod)) {
        props.setProperty("driver.encrypt", "true");
        props.setProperty("driver.trustServerCertificate", "true");
      } else if ("encrypted_verify_certificate".equals(sslMethod)) {
        props.setProperty("driver.encrypt", "true");
        props.setProperty("driver.trustServerCertificate", "false");
        if (dbConfig.has("trustStore") && !dbConfig.get("trustStore").asText().isEmpty()) {
          props.setProperty("database.trustStore", dbConfig.get("trustStore").asText());
        }

        if (dbConfig.has("trustStorePassword") && !dbConfig.get("trustStorePassword").asText().isEmpty()) {
          props.setProperty("database.trustStorePassword", dbConfig.get("trustStorePassword").asText());
        }

        if (dbConfig.has("hostNameInCertificate") && !dbConfig.get("hostNameInCertificate").asText().isEmpty()) {
          props.setProperty("database.hostNameInCertificate", dbConfig.get("hostNameInCertificate").asText());
        }
      }
    } else {
      props.setProperty("driver.trustServerCertificate", "true");
    }

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
