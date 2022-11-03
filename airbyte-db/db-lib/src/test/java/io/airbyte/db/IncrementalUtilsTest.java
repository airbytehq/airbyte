/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.db;

import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;

import com.fasterxml.jackson.databind.node.ObjectNode;
import com.google.common.collect.Lists;
import io.airbyte.commons.json.Jsons;
import io.airbyte.protocol.models.CatalogHelpers;
import io.airbyte.protocol.models.ConfiguredAirbyteStream;
import io.airbyte.protocol.models.Field;
import io.airbyte.protocol.models.JsonSchemaPrimitive;
import io.airbyte.protocol.models.JsonSchemaType;
import java.util.Collections;
import org.junit.jupiter.api.Assertions;
import org.junit.jupiter.api.Test;

class IncrementalUtilsTest {

  private static final String STREAM_NAME = "shoes";
  private static final String UUID_FIELD_NAME = "ascending_inventory_uuid";
  private static final ConfiguredAirbyteStream STREAM = CatalogHelpers.createConfiguredAirbyteStream(
      STREAM_NAME,
      null,
      Field.of("ascending_inventory_uuid", JsonSchemaType.STRING));
  private static final String ABC = "abc";

  @Test
  void testGetCursorField() {
    final ConfiguredAirbyteStream stream = Jsons.clone(STREAM);
    stream.setCursorField(Lists.newArrayList(UUID_FIELD_NAME));
    Assertions.assertEquals(UUID_FIELD_NAME, IncrementalUtils.getCursorField(stream));
  }

  @Test
  void testGetCursorFieldNoCursorFieldSet() {
    assertThrows(IllegalStateException.class, () -> Assertions
        .assertEquals(UUID_FIELD_NAME, IncrementalUtils.getCursorField(STREAM)));
  }

  @Test
  void testGetCursorFieldCompositCursor() {
    final ConfiguredAirbyteStream stream = Jsons.clone(STREAM);
    stream.setCursorField(Lists.newArrayList(UUID_FIELD_NAME, "something_else"));
    assertThrows(IllegalStateException.class, () -> IncrementalUtils.getCursorField(stream));
  }

  @Test
  void testGetCursorType() {
    Assertions.assertEquals(JsonSchemaPrimitive.STRING, IncrementalUtils.getCursorType(STREAM, UUID_FIELD_NAME));
  }

  @Test
  void testGetCursorTypeNoProperties() {
    final ConfiguredAirbyteStream stream = Jsons.clone(STREAM);
    stream.getStream().setJsonSchema(Jsons.jsonNode(Collections.emptyMap()));
    assertThrows(IllegalStateException.class, () -> IncrementalUtils.getCursorType(stream, UUID_FIELD_NAME));
  }

  @Test
  void testGetCursorTypeNoCursor() {
    assertThrows(IllegalStateException.class, () -> IncrementalUtils.getCursorType(STREAM, "does not exist"));
  }

  @Test
  void testGetCursorTypeCursorHasNoType() {
    final ConfiguredAirbyteStream stream = Jsons.clone(STREAM);
    ((ObjectNode) stream.getStream().getJsonSchema().get("properties").get(UUID_FIELD_NAME)).remove("type");
    assertThrows(IllegalStateException.class, () -> IncrementalUtils.getCursorType(stream, UUID_FIELD_NAME));
  }

  @Test
  void testCompareCursors() {
    assertTrue(IncrementalUtils.compareCursors(ABC, "def", JsonSchemaPrimitive.STRING) < 0);
    Assertions.assertEquals(0, IncrementalUtils.compareCursors(ABC, ABC, JsonSchemaPrimitive.STRING));
    assertTrue(IncrementalUtils.compareCursors("1", "2", JsonSchemaPrimitive.NUMBER) < 0);
    assertTrue(IncrementalUtils.compareCursors("5000000000", "5000000001", JsonSchemaPrimitive.NUMBER) < 0);
    assertTrue(IncrementalUtils.compareCursors("false", "true", JsonSchemaPrimitive.BOOLEAN) < 0);
    assertTrue(IncrementalUtils.compareCursors(null, "def", JsonSchemaPrimitive.STRING) < 1);
    assertTrue(IncrementalUtils.compareCursors(ABC, null, JsonSchemaPrimitive.STRING) > 0);
    Assertions.assertEquals(0, IncrementalUtils.compareCursors(null, null, JsonSchemaPrimitive.STRING));
    assertThrows(IllegalStateException.class, () -> IncrementalUtils.compareCursors("a", "a", JsonSchemaPrimitive.ARRAY));
    assertThrows(IllegalStateException.class, () -> IncrementalUtils.compareCursors("a", "a", JsonSchemaPrimitive.OBJECT));
    assertThrows(IllegalStateException.class, () -> IncrementalUtils.compareCursors("a", "a", JsonSchemaPrimitive.NULL));
  }

}
