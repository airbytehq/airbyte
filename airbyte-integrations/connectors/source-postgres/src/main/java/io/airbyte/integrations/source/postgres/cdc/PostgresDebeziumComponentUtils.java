/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.postgres.cdc;

import static io.airbyte.cdk.integrations.source.jdbc.JdbcSSLConnectionUtils.CLIENT_KEY_STORE_PASS;
import static io.airbyte.cdk.integrations.source.jdbc.JdbcSSLConnectionUtils.CLIENT_KEY_STORE_URL;
import static io.airbyte.cdk.integrations.source.jdbc.JdbcSSLConnectionUtils.SSL_MODE;
import static io.airbyte.cdk.integrations.source.jdbc.JdbcSSLConnectionUtils.TRUST_KEY_STORE_PASS;

import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.cdk.components.ComponentRunner;
import io.airbyte.cdk.components.debezium.DebeziumConsumer;
import io.airbyte.cdk.components.debezium.DebeziumProducer;
import io.airbyte.cdk.components.debezium.DebeziumRecord;
import io.airbyte.cdk.components.debezium.DebeziumState;
import io.airbyte.cdk.db.jdbc.JdbcDatabase;
import io.airbyte.cdk.db.jdbc.JdbcUtils;
import io.airbyte.cdk.integrations.source.jdbc.JdbcSSLConnectionUtils;
import io.airbyte.integrations.source.postgres.PostgresSource;
import io.airbyte.integrations.source.postgres.PostgresUtils;
import io.debezium.connector.postgresql.PostgresConnector;
import java.net.URI;
import java.nio.file.Path;
import java.time.Duration;

public class PostgresDebeziumComponentUtils {

  static public final String COMPONENT_NAME = "debezium";
  static public final long MAX_RECORDS = 10_000L;
  static public final long MAX_RECORD_BYTES = 1_000_000_000L;
  static public final DebeziumConsumer.Builder CONSUMER_BUILDER = new DebeziumConsumer.Builder(MAX_RECORDS, MAX_RECORD_BYTES);
  static public final Duration HEARTBEAT_INTERVAL = Duration.ofSeconds(10L);
  // Test execution latency is lower when heartbeats are more frequent.
  static public final Duration HEARTBEAT_INTERVAL_IN_TESTS = Duration.ofMillis(100L);

  static public ComponentRunner<DebeziumRecord, DebeziumState> runner(JdbcDatabase database, DebeziumState upperBound) {
    final JsonNode sourceConfig = database.getSourceConfig();
    final JsonNode dbConfig = database.getDatabaseConfig();
    final DebeziumProducer.Builder b = producerBuilder().withBoundChecker(new PostgresLsnMapper(), upperBound);

    if (sourceConfig.has("snapshot_mode")) {
      // The parameter `snapshot_mode` is passed in test to simulate reading the WAL Logs directly and
      // skip initial snapshot
      b.with("snapshot.mode", sourceConfig.get("snapshot_mode").asText());
    }

    b.with("slot.name", sourceConfig.get("replication_method").get("replication_slot").asText());
    b.with("publication.name", sourceConfig.get("replication_method").get("publication").asText());

    b.withHeartbeats((database.getSourceConfig().has("is_test") && database.getSourceConfig().get("is_test").asBoolean())
        ? HEARTBEAT_INTERVAL_IN_TESTS
        : HEARTBEAT_INTERVAL);

    if (sourceConfig.get("replication_method").has("heartbeat_action_query")) {
      var actionQuery = sourceConfig.get("replication_method").get("heartbeat_action_query").asText();
      if (!actionQuery.isEmpty()) {
        b.with("heartbeat.action.query", actionQuery);
      }
    }

    if (PostgresUtils.shouldFlushAfterSync(sourceConfig)) {
      b.with("flush.lsn.source", "false");
    }

    // Check params for SSL connection in config and add properties for CDC SSL connection
    // https://debezium.io/documentation/reference/2.2/connectors/postgresql.html#postgresql-property-database-sslmode
    if (!sourceConfig.has(JdbcUtils.SSL_KEY) || sourceConfig.get(JdbcUtils.SSL_KEY).asBoolean()) {
      if (sourceConfig.has(JdbcUtils.SSL_MODE_KEY) && sourceConfig.get(JdbcUtils.SSL_MODE_KEY).has(JdbcUtils.MODE_KEY)) {

        if (dbConfig.has(SSL_MODE) && !dbConfig.get(SSL_MODE).asText().isEmpty()) {
          b.with("database.sslmode", PostgresSource.toSslJdbcParamInternal(JdbcSSLConnectionUtils.SslMode.valueOf(dbConfig.get(SSL_MODE).asText())));
        }

        if (dbConfig.has(PostgresSource.CA_CERTIFICATE_PATH) && !dbConfig.get(PostgresSource.CA_CERTIFICATE_PATH).asText().isEmpty()) {
          b.with("database.sslrootcert", dbConfig.get(PostgresSource.CA_CERTIFICATE_PATH).asText());
        }

        if (dbConfig.has(TRUST_KEY_STORE_PASS) && !dbConfig.get(TRUST_KEY_STORE_PASS).asText().isEmpty()) {
          b.with("database.ssl.truststore.password", dbConfig.get(TRUST_KEY_STORE_PASS).asText());
        }

        if (dbConfig.has(CLIENT_KEY_STORE_URL) && !dbConfig.get(CLIENT_KEY_STORE_URL).asText().isEmpty()) {
          b.with("database.sslkey", Path.of(URI.create(dbConfig.get(CLIENT_KEY_STORE_URL).asText())).toString());
        }

        if (dbConfig.has(CLIENT_KEY_STORE_PASS) && !dbConfig.get(CLIENT_KEY_STORE_PASS).asText().isEmpty()) {
          b.with("database.sslpassword", dbConfig.get(CLIENT_KEY_STORE_PASS).asText());
        }
      } else {
        b.with("database.sslmode", "required");
      }
    }

    b.withDatabaseHost(sourceConfig.get(JdbcUtils.HOST_KEY).asText());
    b.withDatabasePort(sourceConfig.get(JdbcUtils.PORT_KEY).asInt());
    b.withDatabaseUser(sourceConfig.get(JdbcUtils.USERNAME_KEY).asText());
    b.withDatabaseName(sourceConfig.get(JdbcUtils.DATABASE_KEY).asText());

    if (sourceConfig.has(JdbcUtils.PASSWORD_KEY)) {
      b.withDatabasePassword(sourceConfig.get(JdbcUtils.PASSWORD_KEY).asText());
    }

    final Duration maxTime = PostgresUtils.getFirstRecordWaitTime(sourceConfig);

    return new ComponentRunner<>(COMPONENT_NAME, b, CONSUMER_BUILDER, maxTime, new PostgresLsnMapper().comparator());
  }

  static public DebeziumProducer.Builder producerBuilder() {
    return new DebeziumProducer.Builder()
        .withConnector(PostgresConnector.class)
        .with("plugin.name", "pgoutput")
        .with("publication.autocreate.mode", "disabled")
        .with("converters", "postgres_converter")
        .with("postgres_converter.type", PostgresConverter.class.getName())
        .with("include.unknown.datatypes", "true")
        .with("snapshot.mode", "initial")
        // https://debezium.io/documentation/reference/2.2/connectors/postgresql.html#postgresql-property-max-queue-size-in-bytes
        .with("max.queue.size.in.bytes", Long.toString(256L * 1024 * 1024));
  }

}
