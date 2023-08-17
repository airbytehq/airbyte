/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.debezium.internals;

import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.db.jdbc.JdbcUtils;
import io.airbyte.protocol.models.v0.ConfiguredAirbyteCatalog;
import io.airbyte.protocol.models.v0.ConfiguredAirbyteStream;
import io.airbyte.protocol.models.v0.SyncMode;
import java.util.Iterator;
import java.util.Optional;
import java.util.Properties;
import java.util.regex.Pattern;
import java.util.stream.Collectors;
import java.util.stream.StreamSupport;
import org.codehaus.plexus.util.StringUtils;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class DebeziumPropertiesManager {

  private static final Logger LOGGER = LoggerFactory.getLogger(DebeziumPropertiesManager.class);
  private static final String BYTE_VALUE_256_MB = Integer.toString(256 * 1024 * 1024);
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

  public Properties getDebeziumProperties() {
    final Properties props = new Properties();
    props.putAll(properties);

    // debezium engine configuration
    // https://debezium.io/documentation/reference/2.2/development/engine.html#engine-properties
    props.setProperty("offset.storage", "org.apache.kafka.connect.storage.FileOffsetBackingStore");
    props.setProperty("offset.storage.file.filename", offsetManager.getOffsetFilePath().toString());
    props.setProperty("offset.flush.interval.ms", "1000"); // todo: make this longer
    // default values from debezium CommonConnectorConfig
    props.setProperty("max.batch.size", "2048");
    props.setProperty("max.queue.size", "8192");

    // Disabling retries because debezium startup time might exceed our 60-second wait limit
    // The maximum number of retries on connection errors before failing (-1 = no limit, 0 = disabled, >
    // 0 = num of retries).
    props.setProperty("errors.max.retries", "0");
    // This property must be strictly less than errors.retry.delay.max.ms
    // (https://github.com/debezium/debezium/blob/bcc7d49519a4f07d123c616cfa45cd6268def0b9/debezium-core/src/main/java/io/debezium/util/DelayStrategy.java#L135)
    props.setProperty("errors.retry.delay.initial.ms", "299");
    props.setProperty("errors.retry.delay.max.ms", "300");

    if (schemaHistoryManager.isPresent()) {
      // https://debezium.io/documentation/reference/2.2/operations/debezium-server.html#debezium-source-database-history-class
      // https://debezium.io/documentation/reference/development/engine.html#_in_the_code
      // As mentioned in the documents above, debezium connector for MySQL needs to track the schema
      // changes. If we don't do this, we can't fetch records for the table.
      props.setProperty("schema.history.internal", "io.debezium.storage.file.history.FileSchemaHistory");
      props.setProperty("schema.history.internal.file.filename", schemaHistoryManager.get().getPath().toString());
    }

    // https://debezium.io/documentation/reference/2.2/configuration/avro.html
    props.setProperty("key.converter.schemas.enable", "false");
    props.setProperty("value.converter.schemas.enable", "false");

    // debezium names
    props.setProperty("name", config.get(JdbcUtils.DATABASE_KEY).asText());

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
    // https://debezium.io/documentation/reference/2.2/connectors/postgresql.html#postgresql-decimal-types
    // https://debezium.io/documentation/faq/#how_to_retrieve_decimal_field_from_binary_representation
    props.setProperty("decimal.handling.mode", "string");

    // https://debezium.io/documentation/reference/2.2/connectors/postgresql.html#postgresql-property-max-queue-size-in-bytes
    props.setProperty("max.queue.size.in.bytes", BYTE_VALUE_256_MB);

    // WARNING : Never change the value of this otherwise all the connectors would start syncing from
    // scratch
    props.setProperty("topic.prefix", config.get(JdbcUtils.DATABASE_KEY).asText());

    // table selection
    props.setProperty("table.include.list", getTableIncludelist(catalog));
    // column selection
    props.setProperty("column.include.list", getColumnIncludeList(catalog));
    return props;
  }

  public static String getTableIncludelist(final ConfiguredAirbyteCatalog catalog) {
    // Turn "stream": {
    // "namespace": "schema1"
    // "name": "table1
    // },
    // "stream": {
    // "namespace": "schema2"
    // "name": "table2
    // } -------> info "schema1.table1, schema2.table2"

    return catalog.getStreams().stream()
        .filter(s -> s.getSyncMode() == SyncMode.INCREMENTAL)
        .map(ConfiguredAirbyteStream::getStream)
        .map(stream -> stream.getNamespace() + "." + stream.getName())
        // debezium needs commas escaped to split properly
        .map(x -> StringUtils.escape(Pattern.quote(x), ",".toCharArray(), "\\,"))
        .collect(Collectors.joining(","));
  }

  public static String getColumnIncludeList(final ConfiguredAirbyteCatalog catalog) {
    // Turn "stream": {
    // "namespace": "schema1"
    // "name": "table1"
    // "jsonSchema": {
    // "properties": {
    // "column1": {
    // },
    // "column2": {
    // }
    // }
    // }
    // } -------> info "schema1.table1.(column1 | column2)"

    return catalog.getStreams().stream()
        .filter(s -> s.getSyncMode() == SyncMode.INCREMENTAL)
        .map(ConfiguredAirbyteStream::getStream)
        .map(s -> {
          final String fields = parseFields(s.getJsonSchema().get("properties").fieldNames());
          // schema.table.(col1|col2)
          return Pattern.quote(s.getNamespace() + "." + s.getName()) + (StringUtils.isNotBlank(fields) ? "\\." + fields : "");
        })
        .map(x -> StringUtils.escape(x, ",".toCharArray(), "\\,"))
        .collect(Collectors.joining(","));
  }

  private static String parseFields(final Iterator<String> fieldNames) {
    if (fieldNames == null || !fieldNames.hasNext()) {
      return "";
    }
    final Iterable<String> iter = () -> fieldNames;
    return StreamSupport.stream(iter.spliterator(), false)
        .map(f -> Pattern.quote(f))
        .collect(Collectors.joining("|", "(", ")"));
  }

}
