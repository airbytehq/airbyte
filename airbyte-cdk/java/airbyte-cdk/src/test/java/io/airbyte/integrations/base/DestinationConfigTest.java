/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.base;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertNotNull;
import static org.junit.jupiter.api.Assertions.assertNull;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;

import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.commons.json.Jsons;
import org.junit.jupiter.api.Test;

public class DestinationConfigTest {

  private static final String JSON = """
                                     {
                                       "foo": "bar",
                                       "baz": true
                                     }
                                     """;

  private static final JsonNode NODE = Jsons.deserialize(JSON);

  @Test
  public void testInitialization() {
    // bad initialization
    assertThrows(IllegalArgumentException.class, () -> DestinationConfig.initialize(null));
    assertThrows(IllegalStateException.class, DestinationConfig::getInstance);

    // good initialization
    DestinationConfig.initialize(NODE);
    assertNotNull(DestinationConfig.getInstance());
    assertEquals(NODE, DestinationConfig.getInstance().root);

    // initializing again doesn't change the config
    final JsonNode nodeUnused = Jsons.deserialize("{}");
    DestinationConfig.initialize(nodeUnused);
    assertEquals(NODE, DestinationConfig.getInstance().root);
  }

  @Test
  public void testValues() {
    DestinationConfig.initialize(NODE);

    assertEquals("bar", DestinationConfig.getInstance().getTextValue("foo"));
    assertEquals("", DestinationConfig.getInstance().getTextValue("baz"));

    assertFalse(DestinationConfig.getInstance().getBooleanValue("foo"));
    assertTrue(DestinationConfig.getInstance().getBooleanValue("baz"));

    // non-existent key
    assertEquals("", DestinationConfig.getInstance().getTextValue("blah"));
    assertFalse(DestinationConfig.getInstance().getBooleanValue("blah"));

    assertEquals(Jsons.deserialize("\"bar\""), DestinationConfig.getInstance().getNodeValue("foo"));
    assertEquals(Jsons.deserialize("true"), DestinationConfig.getInstance().getNodeValue("baz"));
    assertNull(DestinationConfig.getInstance().getNodeValue("blah"));
  }

}
