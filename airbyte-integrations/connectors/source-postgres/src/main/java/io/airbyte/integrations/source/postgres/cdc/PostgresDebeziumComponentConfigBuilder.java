/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.postgres.cdc;

import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.cdk.components.debezium.RelationalConfigBuilder;
import io.airbyte.cdk.db.jdbc.JdbcDatabase;
import io.airbyte.cdk.db.jdbc.JdbcUtils;
import io.airbyte.cdk.integrations.source.jdbc.JdbcSSLConnectionUtils;
import io.airbyte.integrations.source.postgres.PostgresSource;
import io.airbyte.integrations.source.postgres.PostgresUtils;
import io.debezium.connector.postgresql.PostgresConnector;
import java.net.URI;
import java.nio.file.Path;
import java.time.Duration;

import static io.airbyte.cdk.integrations.source.jdbc.JdbcSSLConnectionUtils.CLIENT_KEY_STORE_PASS;
import static io.airbyte.cdk.integrations.source.jdbc.JdbcSSLConnectionUtils.CLIENT_KEY_STORE_URL;
import static io.airbyte.cdk.integrations.source.jdbc.JdbcSSLConnectionUtils.SSL_MODE;
import static io.airbyte.cdk.integrations.source.jdbc.JdbcSSLConnectionUtils.TRUST_KEY_STORE_PASS;

public class PostgresDebeziumComponentConfigBuilder extends RelationalConfigBuilder<PostgresDebeziumComponentConfigBuilder> {

  static public PostgresDebeziumComponentConfigBuilder builder() {
    return new PostgresDebeziumComponentConfigBuilder()
        .withConnector(PostgresConnector.class)
        .with("plugin.name", "pgoutput")
        .with("publication.autocreate.mode", "disabled")
        .with("converters", "postgres_converter")
        .with("postgres_converter.type", PostgresConverter.class.getName())
        .with("include.unknown.datatypes", "true")
        .with("snapshot.mode", "initial")
        .withLsnMapper(new PostgresLsnMapper())
        .withMaxRecords(10_000)
        .withMaxRecordBytes(1_000_000_000)
        .withMaxTime(Duration.ofMinutes(15L));
  }

  private static final Duration HEARTBEAT_INTERVAL = Duration.ofSeconds(10L);

  // Test execution latency is lower when heartbeats are more frequent.
  private static final Duration HEARTBEAT_INTERVAL_IN_TESTS = Duration.ofSeconds(1L);

  public PostgresDebeziumComponentConfigBuilder withConfig(JdbcDatabase database) {
    final JsonNode dbConfig = database.getDatabaseConfig();
    final JsonNode sourceConfig = database.getSourceConfig();

    withMaxTime(PostgresUtils.getFirstRecordWaitTime(sourceConfig));

    if (sourceConfig.has("snapshot_mode")) {
      // The parameter `snapshot_mode` is passed in test to simulate reading the WAL Logs directly and
      // skip initial snapshot
      with("snapshot.mode", sourceConfig.get("snapshot_mode").asText());
    }

    with("slot.name", sourceConfig.get("replication_method").get("replication_slot").asText());
    with("publication.name", sourceConfig.get("replication_method").get("publication").asText());

    withHeartbeats((database.getSourceConfig().has("is_test") && database.getSourceConfig().get("is_test").asBoolean())
            ? HEARTBEAT_INTERVAL_IN_TESTS
            : HEARTBEAT_INTERVAL);

    if (sourceConfig.get("replication_method").has("heartbeat_action_query")) {
      var actionQuery = sourceConfig.get("replication_method").get("heartbeat_action_query").asText();
      if (!actionQuery.isEmpty()) {
        with("heartbeat.action.query", actionQuery);
      }
    }

    if (PostgresUtils.shouldFlushAfterSync(sourceConfig)) {
      with("flush.lsn.source", "false");
    }

    // Check params for SSL connection in config and add properties for CDC SSL connection
    // https://debezium.io/documentation/reference/2.2/connectors/postgresql.html#postgresql-property-database-sslmode
    if (!sourceConfig.has(JdbcUtils.SSL_KEY) || sourceConfig.get(JdbcUtils.SSL_KEY).asBoolean()) {
      if (sourceConfig.has(JdbcUtils.SSL_MODE_KEY) && sourceConfig.get(JdbcUtils.SSL_MODE_KEY).has(JdbcUtils.MODE_KEY)) {

        if (dbConfig.has(SSL_MODE) && !dbConfig.get(SSL_MODE).asText().isEmpty()) {
          with("database.sslmode", PostgresSource.toSslJdbcParamInternal(JdbcSSLConnectionUtils.SslMode.valueOf(dbConfig.get(SSL_MODE).asText())));
        }

        if (dbConfig.has(PostgresSource.CA_CERTIFICATE_PATH) && !dbConfig.get(PostgresSource.CA_CERTIFICATE_PATH).asText().isEmpty()) {
          with("database.sslrootcert", dbConfig.get(PostgresSource.CA_CERTIFICATE_PATH).asText());
        }

        if (dbConfig.has(TRUST_KEY_STORE_PASS) && !dbConfig.get(TRUST_KEY_STORE_PASS).asText().isEmpty()) {
          with("database.ssl.truststore.password", dbConfig.get(TRUST_KEY_STORE_PASS).asText());
        }

        if (dbConfig.has(CLIENT_KEY_STORE_URL) && !dbConfig.get(CLIENT_KEY_STORE_URL).asText().isEmpty()) {
          with("database.sslkey", Path.of(URI.create(dbConfig.get(CLIENT_KEY_STORE_URL).asText())).toString());
        }

        if (dbConfig.has(CLIENT_KEY_STORE_PASS) && !dbConfig.get(CLIENT_KEY_STORE_PASS).asText().isEmpty()) {
          with("database.sslpassword", dbConfig.get(CLIENT_KEY_STORE_PASS).asText());
        }
      } else {
        with("database.sslmode", "required");
      }
    }

    withDatabaseHost(sourceConfig.get(JdbcUtils.HOST_KEY).asText());
    withDatabasePort(sourceConfig.get(JdbcUtils.PORT_KEY).asInt());
    withDatabaseUser(sourceConfig.get(JdbcUtils.USERNAME_KEY).asText());
    withDatabaseName(sourceConfig.get(JdbcUtils.DATABASE_KEY).asText());

    if (sourceConfig.has(JdbcUtils.PASSWORD_KEY)) {
      withDatabasePassword(sourceConfig.get(JdbcUtils.PASSWORD_KEY).asText());
    }

    return this;
  }
}
