/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.mysql;

import com.fasterxml.jackson.databind.JsonNode;
import java.util.Properties;

public class MySqlCdcProperties {

  static Properties getDebeziumProperties(JsonNode config) {
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
    // https://debezium.io/documentation/reference/1.9/connectors/mysql.html#mysql-property-snapshot-mode
    props.setProperty("snapshot.mode", "when_needed");
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

    return props;
  }

}
