/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.jdbc;

import static org.assertj.core.api.AssertionsForClassTypes.assertThat;
import static org.junit.Assert.assertTrue;
import static org.junit.jupiter.api.Assertions.assertThrows;

import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.commons.json.Jsons;
import java.util.List;
import java.util.Map;
import org.junit.jupiter.api.Test;

public class JdbcDataSourceUtilsTest {

  @Test
  void test() {
    final String validConfigString = "{\"jdbc_url_params\":\"key1=val1&key3=key3\",\"connection_properties\":\"key1=val1&key2=val2\"}";
    final JsonNode validConfig = Jsons.deserialize(validConfigString);
    final Map<String, String> connectionProperties = JdbcDataSourceUtils.getConnectionProperties(validConfig);
    final List<String> validKeys = List.of("key1", "key2", "key3");
    validKeys.forEach(key -> assertTrue(connectionProperties.containsKey(key)));

    // For an invalid config, there is a conflict betweeen the values of keys in jdbc_url_params and
    // connection_properties
    final String invalidConfigString = "{\"jdbc_url_params\":\"key1=val2&key3=key3\",\"connection_properties\":\"key1=val1&key2=val2\"}";
    final JsonNode invalidConfig = Jsons.deserialize(invalidConfigString);
    final Exception exception = assertThrows(IllegalArgumentException.class, () -> {
      JdbcDataSourceUtils.getConnectionProperties(invalidConfig);
    });

    final String expectedMessage = "Cannot overwrite default JDBC parameter key1";
    assertThat(expectedMessage.equals(exception.getMessage()));
  }

}
