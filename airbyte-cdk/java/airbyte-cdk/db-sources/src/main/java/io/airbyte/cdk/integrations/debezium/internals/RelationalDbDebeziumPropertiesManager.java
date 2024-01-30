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
import java.util.Properties;
import java.util.regex.Pattern;
import java.util.stream.Collectors;
import java.util.stream.StreamSupport;
import org.codehaus.plexus.util.StringUtils;

public class RelationalDbDebeziumPropertiesManager extends DebeziumPropertiesManager {

  public RelationalDbDebeziumPropertiesManager(final Properties properties,
                                               final JsonNode config,
                                               final ConfiguredAirbyteCatalog catalog) {
    super(properties, config, catalog);
  }

  @Override
  protected Properties getConnectionConfiguration(JsonNode config) {
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
  protected String getName(JsonNode config) {
    return config.get(JdbcUtils.DATABASE_KEY).asText();
  }

  @Override
  protected Properties getIncludeConfiguration(ConfiguredAirbyteCatalog catalog, JsonNode config) {
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

}
