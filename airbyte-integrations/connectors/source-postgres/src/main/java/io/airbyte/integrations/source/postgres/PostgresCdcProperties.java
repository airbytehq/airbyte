/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.postgres;

import com.fasterxml.jackson.databind.JsonNode;
import java.util.Properties;

public class PostgresCdcProperties {

  static Properties getDebeziumDefaultProperties(final JsonNode config) {
    final Properties props = commonProperties();
    props.setProperty("plugin.name", PostgresUtils.getPluginValue(config.get("replication_method")));
    props.setProperty("snapshot.mode", "initial");

    props.setProperty("slot.name", config.get("replication_method").get("replication_slot").asText());
    props.setProperty("publication.name", config.get("replication_method").get("publication").asText());

    props.setProperty("publication.autocreate.mode", "disabled");

    return props;
  }

  private static Properties commonProperties() {
    final Properties props = new Properties();
    props.setProperty("connector.class", "io.debezium.connector.postgresql.PostgresConnector");

    props.setProperty("converters", "datetime");
    props.setProperty("datetime.type", "io.airbyte.integrations.debezium.internals.PostgresConverter");
    return props;
  }

  static Properties getSnapshotProperties() {
    final Properties props = commonProperties();
    props.setProperty("snapshot.mode", "initial_only");
    return props;
  }

}
