/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.postgres;

import com.fasterxml.jackson.databind.JsonNode;
import java.util.Properties;

public class PostgresCdcProperties {

  static Properties getDebeziumProperties(JsonNode config) {
    final Properties props = new Properties();
    props.setProperty("plugin.name", PostgresUtils.getPluginValue(config.get("replication_method")));
    props.setProperty("connector.class", "io.debezium.connector.postgresql.PostgresConnector");
    props.setProperty("snapshot.mode", "exported");

    props.setProperty("slot.name", config.get("replication_method").get("replication_slot").asText());
    props.setProperty("publication.name", config.get("replication_method").get("publication").asText());

    props.setProperty("publication.autocreate.mode", "disabled");

    return props;
  }

}
