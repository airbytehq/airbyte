
/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.teradata.util;

import static org.junit.jupiter.api.Assertions.*;

import java.sql.SQLException;
import java.util.HashMap;
import java.util.Map;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;

/**
 * Unit tests for the JSONStruct class.
 */
public class JSONStructTest {

  private JSONStruct struct;
  private final String json = "{\n" +
      "\t\"id\":123,\n" +
      "\t\"name\":\"Pankaj Kumar\",\n" +
      "}";

  /**
   * Setup method to initialize objects before each test.
   */
  @BeforeEach
  void setup() {
    struct = new JSONStruct("JSON", new Object[] {json});
  }

  /**
   * Test the getAttributes method.
   *
   * @throws SQLException if an SQL exception occurs
   */
  @Test
  void testGetAttributes() throws SQLException {
    assertEquals(json, struct.getAttributes()[0]);
  }

  /**
   * Test the getAttributes method when an exception is expected.
   */
  @Test
  void testGetAttributesException() {
    SQLException exception = assertThrows(SQLException.class, () -> {
      Map<Integer, String> map = new HashMap<>();
      struct.getAttributes(map);
    });
    String expectedMessage = "getAttributes (Map) NOT SUPPORTED";
    String actualMessage = exception.getMessage();
    assertTrue(actualMessage.contains(expectedMessage));
  }

  /**
   * Test the getSQLTypeName method.
   *
   * @throws SQLException if an SQL exception occurs
   */
  @Test
  void testGetSQLTypeName() throws SQLException {
    assertEquals("JSON", struct.getSQLTypeName());
  }

}
