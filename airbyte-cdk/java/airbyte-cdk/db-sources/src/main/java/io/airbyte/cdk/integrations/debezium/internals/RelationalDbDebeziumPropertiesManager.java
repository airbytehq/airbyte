/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.integrations.debezium.internals;

import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.cdk.db.jdbc.JdbcUtils;
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

public class RelationalDbDebeziumPropertiesManager extends DebeziumPropertiesManager {

  private static final Logger LOGGER = LoggerFactory.getLogger(RelationalDbDebeziumPropertiesManager.class);

  public RelationalDbDebeziumPropertiesManager(final Properties properties,
                                               final JsonNode config,
                                               final ConfiguredAirbyteCatalog catalog,
                                               final AirbyteFileOffsetBackingStore offsetManager,
                                               final Optional<AirbyteSchemaHistoryStorage> schemaHistoryManager) {
    super(properties, config, catalog, offsetManager, schemaHistoryManager);
  }

  @Override
  protected Properties getConnectionConfiguration(final JsonNode config) {
    final Properties properties = new Properties();

    // db connection configuration
    properties.setProperty("database.hostname", config.get(JdbcUtils.HOST_KEY).asText());
    properties.setProperty("database.port", config.get(JdbcUtils.PORT_KEY).asText());
    properties.setProperty("database.user", config.get(JdbcUtils.USERNAME_KEY).asText());
    properties.setProperty("database.dbname", config.get(JdbcUtils.DATABASE_KEY).asText());

    if (config.has(JdbcUtils.PASSWORD_KEY)) {
      properties.setProperty("database.password", config.get(JdbcUtils.PASSWORD_KEY).asText());
    }

    return properties;
  }

  @Override
  protected String getName(final JsonNode config) {
    // return "fixed_topic_prefix_name";
    final String name = config.get(JdbcUtils.DATABASE_KEY).asText();
    if (isInvalidName(name)) {
      final String validName = normalizeName(name);
      LOGGER.info("Invalid name detected for debezium name & topic prefix {}, renaming to {} ", name, validName);
      return validName;
    }
    return name;
  }

  @Override
  protected Properties getIncludeConfiguration(final ConfiguredAirbyteCatalog catalog, final JsonNode config) {
    final Properties properties = new Properties();

    // table selection
    properties.setProperty("table.include.list", getTableIncludelist(catalog));
    // column selection
    properties.setProperty("column.include.list", getColumnIncludeList(catalog));

    return properties;
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

  /**
   * Checks if the string contains any of the invalid characters. A string is valid if it contains
   * only underscore, hyphen, dot or alphanumeric chars. This is according to the rules for values of
   * topic.prefix outlined here :
   * https://debezium.io/documentation/reference/stable/connectors/postgresql.html#postgresql-property-topic-prefix.
   * The same applies for other debezium connectors Airbyte currently supports (Postgres, MySQL,
   * MsSQL)
   *
   * @param name - the input string to check.
   * @return - true if it contains any invalid characters, false otherwise.
   */
  private static boolean isInvalidName(final String name) {
    return !name.matches("[^a-zA-Z0-9._-]*");
  }

  /**
   * Removes any invalid characters from the given name. A string is valid if it contains only
   * underscore, hyphen, dot or alphanumeric chars. This is according to the rules for valid values of
   * topic.prefix outlined here :
   * https://debezium.io/documentation/reference/stable/connectors/postgresql.html#postgresql-property-topic-prefix.
   * The same applies for other debezium connectors Airbyte currently supports (Postgres, MySQL,
   * MsSQL)
   *
   * @param name - the input string to clean.
   * @return - the cleaned string.
   */
  private static String normalizeName(final String name) {
    return name.replaceAll("[^a-zA-Z0-9._-]", "");
  }

}
