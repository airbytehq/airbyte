/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.debezium.internals;

import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.db.jdbc.JdbcUtils;
import io.airbyte.protocol.models.ConfiguredAirbyteCatalog;
import io.airbyte.protocol.models.ConfiguredAirbyteStream;
import io.airbyte.protocol.models.SyncMode;
import java.util.Optional;
import java.util.Properties;
import java.util.stream.Collectors;
import org.codehaus.plexus.util.StringUtils;

public class DebeziumPropertiesManager {

  private final JsonNode config;
  private final AirbyteFileOffsetBackingStore offsetManager;
  private final Optional<AirbyteSchemaHistoryStorage> schemaHistoryManager;

  private final Properties properties;
  private final ConfiguredAirbyteCatalog catalog;

  public DebeziumPropertiesManager(final Properties properties,
                                   final JsonNode config,
                                   final ConfiguredAirbyteCatalog catalog,
                                   final AirbyteFileOffsetBackingStore offsetManager,
                                   final Optional<AirbyteSchemaHistoryStorage> schemaHistoryManager) {
    this.properties = properties;
    this.config = config;
    this.catalog = catalog;
    this.offsetManager = offsetManager;
    this.schemaHistoryManager = schemaHistoryManager;
  }

  protected Properties getDebeziumProperties() {
    final Properties props = new Properties();
    props.putAll(properties);

    // debezium engine configuration
    props.setProperty("name", "engine");
    props.setProperty("offset.storage", "org.apache.kafka.connect.storage.FileOffsetBackingStore");
    props.setProperty("offset.storage.file.filename", offsetManager.getOffsetFilePath().toString());
    props.setProperty("offset.flush.interval.ms", "1000"); // todo: make this longer
    // default values from debezium CommonConnectorConfig
    props.setProperty("max.batch.size", "2048");
    props.setProperty("max.queue.size", "8192");

    if (schemaHistoryManager.isPresent()) {
      // https://debezium.io/documentation/reference/1.9/operations/debezium-server.html#debezium-source-database-history-class
      // https://debezium.io/documentation/reference/development/engine.html#_in_the_code
      // As mentioned in the documents above, debezium connector for MySQL needs to track the schema
      // changes. If we don't do this, we can't fetch records for the table.
      props.setProperty("database.history", "io.debezium.relational.history.FileDatabaseHistory");
      props.setProperty("database.history.file.filename", schemaHistoryManager.get().getPath().toString());
    }

    // https://debezium.io/documentation/reference/configuration/avro.html
    props.setProperty("key.converter.schemas.enable", "false");
    props.setProperty("value.converter.schemas.enable", "false");

    // debezium names
    props.setProperty("name", config.get(JdbcUtils.DATABASE_KEY).asText());
    props.setProperty("database.server.name", config.get(JdbcUtils.DATABASE_KEY).asText());

    // db connection configuration
    props.setProperty("database.hostname", config.get(JdbcUtils.HOST_KEY).asText());
    props.setProperty("database.port", config.get(JdbcUtils.PORT_KEY).asText());
    props.setProperty("database.user", config.get(JdbcUtils.USERNAME_KEY).asText());
    props.setProperty("database.dbname", config.get(JdbcUtils.DATABASE_KEY).asText());

    if (config.has(JdbcUtils.PASSWORD_KEY)) {
      props.setProperty("database.password", config.get(JdbcUtils.PASSWORD_KEY).asText());
    }

    // By default "decimal.handing.mode=precise" which's caused returning this value as a binary.
    // The "double" type may cause a loss of precision, so set Debezium's config to store it as a String
    // explicitly in its Kafka messages for more details see:
    // https://debezium.io/documentation/reference/1.9/connectors/postgresql.html#postgresql-decimal-types
    // https://debezium.io/documentation/faq/#how_to_retrieve_decimal_field_from_binary_representation
    props.setProperty("decimal.handling.mode", "string");

    // table selection
    final String tableWhitelist = getTableWhitelist(catalog);
    props.setProperty("table.include.list", tableWhitelist);

    return props;
  }

  public static String getTableWhitelist(final ConfiguredAirbyteCatalog catalog) {
    return catalog.getStreams().stream()
        .filter(s -> s.getSyncMode() == SyncMode.INCREMENTAL)
        .map(ConfiguredAirbyteStream::getStream)
        .map(stream -> stream.getNamespace() + "." + stream.getName())
        // debezium needs commas escaped to split properly
        .map(x -> StringUtils.escape(x, new char[] {','}, "\\,"))
        .collect(Collectors.joining(","));
  }

}
