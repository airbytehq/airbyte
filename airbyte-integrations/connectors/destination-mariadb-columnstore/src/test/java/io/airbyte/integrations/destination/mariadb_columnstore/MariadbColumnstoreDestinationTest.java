/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.mariadb_columnstore;

import static org.junit.jupiter.api.Assertions.*;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import org.junit.jupiter.api.Test;

public class MariadbColumnstoreDestinationTest {

  @Test
  public void testToJdbcConfig() throws Exception {
    final MariadbColumnstoreDestination dest = new MariadbColumnstoreDestination();
    String configJson = "{\"host\": \"localhost\", \"port\": 3306, \"database\": \"test\", \"username\": \"root\", \"password\": \"secret\"}";
    String expectedJson = "{\"username\": \"root\", \"password\": \"secret\", \"jdbc_url\": \"jdbc:mariadb://localhost:3306/test\"}";
    ObjectMapper mapper = new ObjectMapper();
    JsonNode config = mapper.readTree(configJson);

    JsonNode actual = dest.toJdbcConfig(config);
    JsonNode expected = mapper.readTree(expectedJson);

    assertEquals(expected, actual);
  }

}
