/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.mysql;

import static io.airbyte.integrations.source.jdbc.AbstractJdbcSource.CLIENT_KEY_STORE_PASS;
import static io.airbyte.integrations.source.jdbc.AbstractJdbcSource.CLIENT_KEY_STORE_URL;
import static io.airbyte.integrations.source.jdbc.AbstractJdbcSource.SSL_MODE;
import static io.airbyte.integrations.source.jdbc.AbstractJdbcSource.TRUST_KEY_STORE_PASS;
import static io.airbyte.integrations.source.jdbc.AbstractJdbcSource.TRUST_KEY_STORE_URL;

import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.db.jdbc.JdbcDatabase;
import io.airbyte.db.jdbc.JdbcUtils;
import io.airbyte.integrations.source.jdbc.AbstractJdbcSource.SslMode;
import java.net.URI;
import java.nio.file.Path;
import java.util.Properties;

public class MySqlCdcProperties {

  static Properties getDebeziumProperties(final JdbcDatabase database) {
    final JsonNode sourceConfig = database.getSourceConfig();
    final Properties props = commonProperties(database);
    // snapshot config
    if (sourceConfig.has("snapshot_mode")) {
      // The parameter `snapshot_mode` is passed in test to simulate reading the binlog directly and skip
      // initial snapshot
      props.setProperty("snapshot.mode", sourceConfig.get("snapshot_mode").asText());
    } else {
      // https://debezium.io/documentation/reference/1.9/connectors/mysql.html#mysql-property-snapshot-mode
      props.setProperty("snapshot.mode", "when_needed");
    }

    return props;
  }

  private static Properties commonProperties(final JdbcDatabase database) {
    final Properties props = new Properties();
    final JsonNode sourceConfig = database.getSourceConfig();
    final JsonNode dbConfig = database.getDatabaseConfig();
    // debezium engine configuration
    props.setProperty("connector.class", "io.debezium.connector.mysql.MySqlConnector");

    // https://debezium.io/documentation/reference/connectors/mysql.html#mysql-boolean-values
    // https://debezium.io/documentation/reference/1.9/development/converters.html
    /**
     * {@link io.debezium.connector.mysql.converters.TinyIntOneToBooleanConverter}
     * {@link MySQLConverter}
     */
    props.setProperty("converters", "boolean, datetime");
    props.setProperty("boolean.type", "io.airbyte.integrations.debezium.internals.CustomMySQLTinyIntOneToBooleanConverter");
    props.setProperty("datetime.type", "io.airbyte.integrations.debezium.internals.MySQLDateTimeConverter");

    // For CDC mode, the user cannot provide timezone arguments as JDBC parameters - they are
    // specifically defined in the replication_method
    // config.
    if (sourceConfig.get("replication_method").has("server_time_zone")) {
      final String serverTimeZone = sourceConfig.get("replication_method").get("server_time_zone").asText();
      if (!serverTimeZone.isEmpty()) {
        props.setProperty("database.serverTimezone", serverTimeZone);
      }
    }

    // Check params for SSL connection in config and add properties for CDC SSL connection
    // https://debezium.io/documentation/reference/stable/connectors/mysql.html#mysql-property-database-ssl-mode
    if (!sourceConfig.has(JdbcUtils.SSL_KEY) || sourceConfig.get(JdbcUtils.SSL_KEY).asBoolean()) {
      if (dbConfig.has(SSL_MODE) && !dbConfig.get(SSL_MODE).asText().isEmpty()) {
        props.setProperty("database.ssl.mode", MySqlSource.toSslJdbcParamInternal(SslMode.valueOf(dbConfig.get(SSL_MODE).asText())));
        props.setProperty("database.history.producer.security.protocol", "SSL");
        props.setProperty("database.history.consumer.security.protocol", "SSL");

        if (dbConfig.has(TRUST_KEY_STORE_URL) && !dbConfig.get(TRUST_KEY_STORE_URL).asText().isEmpty()) {
          props.setProperty("database.ssl.truststore", Path.of(URI.create(dbConfig.get(TRUST_KEY_STORE_URL).asText())).toString());
          props.setProperty("database.history.producer.ssl.truststore.location",
              Path.of(URI.create(dbConfig.get(TRUST_KEY_STORE_URL).asText())).toString());
          props.setProperty("database.history.consumer.ssl.truststore.location",
              Path.of(URI.create(dbConfig.get(TRUST_KEY_STORE_URL).asText())).toString());
          props.setProperty("database.history.producer.ssl.truststore.type", "PKCS12");
          props.setProperty("database.history.consumer.ssl.truststore.type", "PKCS12");

        }
        if (dbConfig.has(TRUST_KEY_STORE_PASS) && !dbConfig.get(TRUST_KEY_STORE_PASS).asText().isEmpty()) {
          props.setProperty("database.ssl.truststore.password", dbConfig.get(TRUST_KEY_STORE_PASS).asText());
          props.setProperty("database.history.producer.ssl.truststore.password", dbConfig.get(TRUST_KEY_STORE_PASS).asText());
          props.setProperty("database.history.consumer.ssl.truststore.password", dbConfig.get(TRUST_KEY_STORE_PASS).asText());
          props.setProperty("database.history.producer.ssl.key.password", dbConfig.get(TRUST_KEY_STORE_PASS).asText());
          props.setProperty("database.history.consumer.ssl.key.password", dbConfig.get(TRUST_KEY_STORE_PASS).asText());

        }
        if (dbConfig.has(CLIENT_KEY_STORE_URL) && !dbConfig.get(CLIENT_KEY_STORE_URL).asText().isEmpty()) {
          props.setProperty("database.ssl.keystore", Path.of(URI.create(dbConfig.get(CLIENT_KEY_STORE_URL).asText())).toString());
          props.setProperty("database.history.producer.ssl.keystore.location",
              Path.of(URI.create(dbConfig.get(CLIENT_KEY_STORE_URL).asText())).toString());
          props.setProperty("database.history.consumer.ssl.keystore.location",
              Path.of(URI.create(dbConfig.get(CLIENT_KEY_STORE_URL).asText())).toString());
          props.setProperty("database.history.producer.ssl.keystore.type", "PKCS12");
          props.setProperty("database.history.consumer.ssl.keystore.type", "PKCS12");

        }
        if (dbConfig.has(CLIENT_KEY_STORE_PASS) && !dbConfig.get(CLIENT_KEY_STORE_PASS).asText().isEmpty()) {
          props.setProperty("database.ssl.keystore.password", dbConfig.get(CLIENT_KEY_STORE_PASS).asText());
          props.setProperty("database.history.producer.ssl.keystore.password", dbConfig.get(CLIENT_KEY_STORE_PASS).asText());
          props.setProperty("database.history.consumer.ssl.keystore.password", dbConfig.get(CLIENT_KEY_STORE_PASS).asText());
        }
      } else {
        props.setProperty("database.ssl.mode", "required");
      }
    }

    // https://debezium.io/documentation/reference/1.9/connectors/mysql.html#mysql-property-snapshot-locking-mode
    // This is to make sure other database clients are allowed to write to a table while Airbyte is
    // taking a snapshot. There is a risk involved that
    // if any database client makes a schema change then the sync might break
    props.setProperty("snapshot.locking.mode", "none");
    // https://debezium.io/documentation/reference/1.9/connectors/mysql.html#mysql-property-include-schema-changes
    props.setProperty("include.schema.changes", "false");
    // This to make sure that binary data represented as a base64-encoded String.
    // https://debezium.io/documentation/reference/1.9/connectors/mysql.html#mysql-property-binary-handling-mode
    props.setProperty("binary.handling.mode", "base64");
    props.setProperty("database.include.list", sourceConfig.get("database").asText());

    return props;
  }

  static Properties getSnapshotProperties(final JdbcDatabase database) {
    final Properties props = commonProperties(database);
    props.setProperty("snapshot.mode", "initial_only");
    return props;
  }

}
