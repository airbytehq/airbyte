/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.mysql;

import static io.airbyte.integrations.util.MySqlSslConnectionUtils.checkOrCreatePassword;

import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.db.jdbc.JdbcUtils;
import java.util.Properties;

public class MySqlCdcProperties {

  static Properties getDebeziumProperties(final JsonNode config) {
    final Properties props = new Properties();

    // debezium engine configuration
    props.setProperty("connector.class", "io.debezium.connector.mysql.MySqlConnector");

    // https://debezium.io/documentation/reference/connectors/mysql.html#mysql-boolean-values
    // https://debezium.io/documentation/reference/1.9/development/converters.html
    /**
     * {@link io.debezium.connector.mysql.converters.TinyIntOneToBooleanConverter}
     * {@link MySQLConverter}
     */
    props.setProperty("converters", "boolean, datetime");
    props.setProperty("boolean.type", "io.debezium.connector.mysql.converters.TinyIntOneToBooleanConverter");
    props.setProperty("datetime.type", "io.airbyte.integrations.debezium.internals.MySQLDateTimeConverter");

    // snapshot config
    if (config.has("snapshot_mode")) {
      // The parameter `snapshot_mode` is passed in test to simulate reading the binlog directly and skip
      // initial snapshot
      props.setProperty("snapshot.mode", config.get("snapshot_mode").asText());
    } else {
      // https://debezium.io/documentation/reference/1.9/connectors/mysql.html#mysql-property-snapshot-mode
      props.setProperty("snapshot.mode", "when_needed");
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
    props.setProperty("database.include.list", config.get("database").asText());
    // Check params for SSL connection in config and add properties for CDC SSL connection
    // https://debezium.io/documentation/reference/stable/connectors/mysql.html#mysql-property-database-ssl-mode
    if (!config.has(JdbcUtils.SSL_KEY) || config.get(JdbcUtils.SSL_KEY).asBoolean()) {
      if (config.has(JdbcUtils.SSL_MODE_KEY) && config.get(JdbcUtils.SSL_MODE_KEY).has(JdbcUtils.MODE_KEY)) {
        props.setProperty("database.ssl.mode", config.get(JdbcUtils.SSL_MODE_KEY).get(JdbcUtils.MODE_KEY).asText());
        final var method = config.get(JdbcUtils.SSL_MODE_KEY).get(JdbcUtils.MODE_KEY).asText();
        if (method.equals("verify_ca") || method.equals("verify_identity")) {
          var sslPassword = checkOrCreatePassword(config.get(JdbcUtils.SSL_MODE_KEY));
          props.setProperty("database.history.producer.security.protocol", "SSL");
          props.setProperty("database.history.producer.ssl.truststore.location", "customtruststore.jks");
          props.setProperty("database.history.producer.ssl.truststore.password", sslPassword);
          props.setProperty("database.history.producer.ssl.key.password", sslPassword);

          props.setProperty("database.history.consumer.security.protocol", "SSL");
          props.setProperty("database.history.consumer.ssl.truststore.location", "customtruststore.jks");
          props.setProperty("database.history.consumer.ssl.truststore.password", sslPassword);
          props.setProperty("database.history.consumer.ssl.key.password", sslPassword);
          if (method.equals("verify_identity")) {
            props.setProperty("database.history.producer.ssl.keystore.location", "customkeystore.jks");
            props.setProperty("database.history.producer.ssl.keystore.password", sslPassword);

            props.setProperty("database.history.consumer.ssl.keystore.location", "customkeystore.jks");
            props.setProperty("database.history.consumer.ssl.keystore.password", sslPassword);
          }
        }
      } else {
        props.setProperty("database.ssl.mode", "required");
      }
    }
    return props;
  }

}
