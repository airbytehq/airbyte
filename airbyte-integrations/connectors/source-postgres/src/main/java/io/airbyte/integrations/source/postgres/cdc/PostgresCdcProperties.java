/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.postgres.cdc;

import static io.airbyte.cdk.db.jdbc.JdbcSSLConnectionUtils.CLIENT_KEY_STORE_PASS;
import static io.airbyte.cdk.db.jdbc.JdbcSSLConnectionUtils.CLIENT_KEY_STORE_URL;
import static io.airbyte.cdk.db.jdbc.JdbcSSLConnectionUtils.SSL_MODE;
import static io.airbyte.cdk.db.jdbc.JdbcSSLConnectionUtils.TRUST_KEY_STORE_PASS;

import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.cdk.db.jdbc.JdbcDatabase;
import io.airbyte.cdk.db.jdbc.JdbcSSLConnectionUtils.SslMode;
import io.airbyte.cdk.db.jdbc.JdbcUtils;
import io.airbyte.integrations.source.postgres.PostgresSource;
import io.airbyte.integrations.source.postgres.PostgresUtils;
import java.net.URI;
import java.nio.file.Path;
import java.time.Duration;
import java.util.Properties;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class PostgresCdcProperties {

  private static final Duration HEARTBEAT_INTERVAL = Duration.ofSeconds(10L);

  // Test execution latency is lower when heartbeats are more frequent.
  private static final Duration HEARTBEAT_INTERVAL_IN_TESTS = Duration.ofSeconds(1L);

  private static final Logger LOGGER = LoggerFactory.getLogger(PostgresCdcProperties.class);

  public static Properties getDebeziumDefaultProperties(final JdbcDatabase database) {
    final JsonNode sourceConfig = database.getSourceConfig();
    final Properties props = commonProperties(database);
    props.setProperty("plugin.name", PostgresUtils.getPluginValue(sourceConfig.get("replication_method")));
    if (sourceConfig.has("snapshot_mode")) {
      // The parameter `snapshot_mode` is passed in test to simulate reading the WAL Logs directly and
      // skip initial snapshot
      props.setProperty("snapshot.mode", sourceConfig.get("snapshot_mode").asText());
    } else {
      props.setProperty("snapshot.mode", "initial");
    }

    props.setProperty("slot.name", sourceConfig.get("replication_method").get("replication_slot").asText());
    props.setProperty("publication.name", sourceConfig.get("replication_method").get("publication").asText());

    props.setProperty("publication.autocreate.mode", "disabled");

    return props;
  }

  private static Properties commonProperties(final JdbcDatabase database) {
    final JsonNode dbConfig = database.getDatabaseConfig();
    final JsonNode sourceConfig = database.getSourceConfig();

    final Properties props = new Properties();
    props.setProperty("connector.class", "io.debezium.connector.postgresql.PostgresConnector");

    props.setProperty("converters", "datetime");
    props.setProperty("datetime.type", PostgresConverter.class.getName());
    props.setProperty("include.unknown.datatypes", "true");

    final Duration heartbeatInterval =
        (database.getSourceConfig().has("is_test") && database.getSourceConfig().get("is_test").asBoolean())
            ? HEARTBEAT_INTERVAL_IN_TESTS
            : HEARTBEAT_INTERVAL;
    props.setProperty("heartbeat.interval.ms", Long.toString(heartbeatInterval.toMillis()));

    if (sourceConfig.get("replication_method").has("heartbeat_action_query")
        && !sourceConfig.get("replication_method").get("heartbeat_action_query").asText().isEmpty()) {
      props.setProperty("heartbeat.action.query", sourceConfig.get("replication_method").get("heartbeat_action_query").asText());
    }

    if (PostgresUtils.shouldFlushAfterSync(sourceConfig)) {
      props.setProperty("flush.lsn.source", "false");
    }

    // Check params for SSL connection in config and add properties for CDC SSL connection
    // https://debezium.io/documentation/reference/2.2/connectors/postgresql.html#postgresql-property-database-sslmode
    if (!sourceConfig.has(JdbcUtils.SSL_KEY) || sourceConfig.get(JdbcUtils.SSL_KEY).asBoolean()) {
      if (sourceConfig.has(JdbcUtils.SSL_MODE_KEY) && sourceConfig.get(JdbcUtils.SSL_MODE_KEY).has(JdbcUtils.MODE_KEY)) {

        if (dbConfig.has(SSL_MODE) && !dbConfig.get(SSL_MODE).asText().isEmpty()) {
          LOGGER.debug("sslMode: {}", dbConfig.get(SSL_MODE).asText());
          props.setProperty("database.sslmode", PostgresSource.toSslJdbcParamInternal(SslMode.valueOf(dbConfig.get(SSL_MODE).asText())));
        }

        if (dbConfig.has(PostgresSource.CA_CERTIFICATE_PATH) && !dbConfig.get(PostgresSource.CA_CERTIFICATE_PATH).asText().isEmpty()) {
          props.setProperty("database.sslrootcert", dbConfig.get(PostgresSource.CA_CERTIFICATE_PATH).asText());
        }

        if (dbConfig.has(TRUST_KEY_STORE_PASS) && !dbConfig.get(TRUST_KEY_STORE_PASS).asText().isEmpty()) {
          props.setProperty("database.ssl.truststore.password", dbConfig.get(TRUST_KEY_STORE_PASS).asText());
        }

        if (dbConfig.has(CLIENT_KEY_STORE_URL) && !dbConfig.get(CLIENT_KEY_STORE_URL).asText().isEmpty()) {
          props.setProperty("database.sslkey", Path.of(URI.create(dbConfig.get(CLIENT_KEY_STORE_URL).asText())).toString());
        }

        if (dbConfig.has(CLIENT_KEY_STORE_PASS) && !dbConfig.get(CLIENT_KEY_STORE_PASS).asText().isEmpty()) {
          props.setProperty("database.sslpassword", dbConfig.get(CLIENT_KEY_STORE_PASS).asText());
        }
      } else {
        props.setProperty("database.sslmode", "required");
      }
    }
    return props;
  }

  public static Properties getSnapshotProperties(final JdbcDatabase database) {
    final Properties props = commonProperties(database);
    props.setProperty("snapshot.mode", "initial_only");
    return props;
  }

}
