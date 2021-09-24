/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.protocol.models;

import static org.junit.jupiter.api.Assertions.assertEquals;

import com.fasterxml.jackson.databind.JsonNode;
import com.google.common.collect.ImmutableSet;
import com.google.common.collect.Sets;
import io.airbyte.commons.json.Jsons;
import io.airbyte.commons.resources.MoreResources;
import java.io.IOException;
import java.util.Set;
import org.junit.jupiter.api.Test;

class CatalogHelpersTest {

  @Test
  void testFieldToJsonSchema() {
    final String expected = "{ \"type\": \"object\", \"properties\": { \"name\": { \"type\": \"string\" } } } ";
    final JsonNode actual = CatalogHelpers.fieldsToJsonSchema(Field.of("name", JsonSchemaPrimitive.STRING));

    assertEquals(Jsons.deserialize(expected), actual);
  }

  @Test
  void testGetTopLevelFieldNames() {
    final String json = "{ \"type\": \"object\", \"properties\": { \"name\": { \"type\": \"string\" } } } ";
    final Set<String> actualFieldNames =
        CatalogHelpers.getTopLevelFieldNames(new ConfiguredAirbyteStream().withStream(new AirbyteStream().withJsonSchema(Jsons.deserialize(json))));

    assertEquals(Sets.newHashSet("name"), actualFieldNames);
  }

  @Test
  void testGetFieldNames() throws IOException {
    JsonNode node = Jsons.deserialize(MoreResources.readResource("valid_schema.json"));
    Set<String> actualFieldNames = CatalogHelpers.getAllFieldNames(node);
    Set<String> expectedFieldNames = ImmutableSet.of("date", "CAD", "HKD", "ISK", "PHP", "DKK", "HUF", "文", "somekey", "something", "nestedkey");

    assertEquals(expectedFieldNames, actualFieldNames);
  }

}
