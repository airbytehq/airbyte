/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.integrations.source.jdbc;

import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.cdk.db.jdbc.JdbcUtils;
import io.airbyte.commons.map.MoreMaps;
import java.util.Map;
import java.util.Objects;

public class JdbcDataSourceUtils {

  public static final String DEFAULT_JDBC_PARAMETERS_DELIMITER = "&";

  /**
   * Validates for duplication parameters
   *
   * @param customParameters custom connection properties map as specified by each Jdbc source
   * @param defaultParameters connection properties map as specified by each Jdbc source
   * @throws IllegalArgumentException
   */
  public static void assertCustomParametersDontOverwriteDefaultParameters(final Map<String, String> customParameters,
                                                                          final Map<String, String> defaultParameters) {
    for (final String key : defaultParameters.keySet()) {
      if (customParameters.containsKey(key) && !Objects.equals(customParameters.get(key), defaultParameters.get(key))) {
        throw new IllegalArgumentException("Cannot overwrite default JDBC parameter " + key);
      }
    }
  }

  /**
   * Retrieves connection_properties from config and also validates if custom jdbc_url parameters
   * overlap with the default properties
   *
   * @param config A configuration used to check Jdbc connection
   * @return A mapping of connection properties
   */
  public static Map<String, String> getConnectionProperties(final JsonNode config) {
    return getConnectionProperties(config, DEFAULT_JDBC_PARAMETERS_DELIMITER);
  }

  public static Map<String, String> getConnectionProperties(final JsonNode config, String parameterDelimiter) {
    final Map<String, String> customProperties = JdbcUtils.parseJdbcParameters(config, JdbcUtils.JDBC_URL_PARAMS_KEY, parameterDelimiter);
    final Map<String, String> defaultProperties = JdbcDataSourceUtils.getDefaultConnectionProperties(config);
    assertCustomParametersDontOverwriteDefaultParameters(customProperties, defaultProperties);
    return MoreMaps.merge(customProperties, defaultProperties);
  }

  /**
   * Retrieves default connection_properties from config
   *
   * TODO: make this method abstract and add parity features to destination connectors
   *
   * @param config A configuration used to check Jdbc connection
   * @return A mapping of the default connection properties
   */
  public static Map<String, String> getDefaultConnectionProperties(final JsonNode config) {
    // NOTE that Postgres returns an empty map for some reason?
    return JdbcUtils.parseJdbcParameters(config, "connection_properties", DEFAULT_JDBC_PARAMETERS_DELIMITER);
  };

}
