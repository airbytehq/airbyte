/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.db.jdbc;

import com.fasterxml.jackson.databind.JsonNode;
import com.google.common.collect.Maps;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import org.jooq.JSONFormat;

public class JdbcUtils {

  // config parameters in alphabetical order
  public static final String CONNECTION_PROPERTIES_KEY = "connection_properties";
  public static final String DATABASE_KEY = "database";
  public static final String ENCRYPTION_KEY = "encryption";
  public static final String HOST_KEY = "host";
  public static final List<String> HOST_LIST_KEY = List.of("host");
  public static final String JDBC_URL_KEY = "jdbc_url";
  public static final String JDBC_URL_PARAMS_KEY = "jdbc_url_params";
  public static final String PASSWORD_KEY = "password";
  public static final String PORT_KEY = "port";
  public static final String TCP_PORT_KEY = "tcp-port";
  public static final List<String> PORT_LIST_KEY = List.of("port");
  public static final String SCHEMA_KEY = "schema";
  // NOTE: this is the plural version of SCHEMA_KEY
  public static final String SCHEMAS_KEY = "schemas";
  public static final String SSL_KEY = "ssl";
  public static final String TLS_KEY = "tls";
  public static final String USERNAME_KEY = "username";
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

  /**
   * Checks that SSL_KEY has not been set or that an SSL_KEY is set and value can be mapped to true
   * (e.g. non-zero integers, string true, etc)
   *
   * @param config A configuration used to check Jdbc connection
   * @return true: if ssl has not been set or it has been set with true, false: in all other cases
   */
  public static boolean useSsl(final JsonNode config) {
    return !config.has(SSL_KEY) || config.get(SSL_KEY).asBoolean();
  }

}
