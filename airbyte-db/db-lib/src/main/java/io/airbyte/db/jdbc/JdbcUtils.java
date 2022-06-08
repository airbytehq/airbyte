/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.db.jdbc;

import com.fasterxml.jackson.databind.JsonNode;
import com.google.common.collect.Maps;
import java.util.HashMap;
import java.util.Map;
import org.jooq.JSONFormat;

public class JdbcUtils {

  private static final JdbcSourceOperations defaultSourceOperations = new JdbcSourceOperations();

  private static final JSONFormat defaultJSONFormat = new JSONFormat().recordFormat(JSONFormat.RecordFormat.OBJECT);

  public static JdbcSourceOperations getDefaultSourceOperations() {
    return defaultSourceOperations;
  }

  public static JSONFormat getDefaultJSONFormat() {
    return defaultJSONFormat;
  }

  public static String getFullyQualifiedTableName(final String schemaName, final String tableName) {
    return schemaName != null ? schemaName + "." + tableName : tableName;
  }

  public static Map<String, String> parseJdbcParameters(final JsonNode config, final String jdbcUrlParamsKey) {
    return parseJdbcParameters(config, jdbcUrlParamsKey, "&");
  }

  public static Map<String, String> parseJdbcParameters(final JsonNode config, final String jdbcUrlParamsKey, final String delimiter) {
    if (config.has(jdbcUrlParamsKey)) {
      return parseJdbcParameters(config.get(jdbcUrlParamsKey).asText(), delimiter);
    } else {
      return Maps.newHashMap();
    }
  }

  public static Map<String, String> parseJdbcParameters(final String jdbcPropertiesString) {
    return parseJdbcParameters(jdbcPropertiesString, "&");
  }

  public static Map<String, String> parseJdbcParameters(final String jdbcPropertiesString, final String delimiter) {
    final Map<String, String> parameters = new HashMap<>();
    if (!jdbcPropertiesString.isBlank()) {
      final String[] keyValuePairs = jdbcPropertiesString.split(delimiter);
      for (final String kv : keyValuePairs) {
        final String[] split = kv.split("=");
        if (split.length == 2) {
          parameters.put(split[0], split[1]);
        } else {
          throw new IllegalArgumentException(
              "jdbc_url_params must be formatted as 'key=value' pairs separated by the symbol '&'. (example: key1=value1&key2=value2&key3=value3). Got "
                  + jdbcPropertiesString);
        }
      }
    }
    return parameters;
  }

}
