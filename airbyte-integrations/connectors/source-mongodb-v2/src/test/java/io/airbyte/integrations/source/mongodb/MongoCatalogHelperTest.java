/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.mongodb;

import static io.airbyte.integrations.source.mongodb.MongoCatalogHelper.DEFAULT_CURSOR_FIELD;
import static io.airbyte.integrations.source.mongodb.MongoCatalogHelper.DEFAULT_PRIMARY_KEY;
import static io.airbyte.integrations.source.mongodb.MongoCatalogHelper.SUPPORTED_SYNC_MODES;
import static io.airbyte.integrations.source.mongodb.MongoConstants.ID_FIELD;
import static io.airbyte.integrations.source.mongodb.MongoConstants.SCHEMALESS_MODE_DATA_FIELD;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertNotNull;
import static org.junit.jupiter.api.Assertions.assertTrue;

import io.airbyte.cdk.integrations.debezium.internals.DebeziumEventConverter;
import io.airbyte.protocol.models.Field;
import io.airbyte.protocol.models.JsonSchemaType;
import io.airbyte.protocol.models.v0.AirbyteStream;
import java.util.List;
import org.junit.jupiter.api.Test;

class MongoCatalogHelperTest {

  @Test
  void testBuildingAirbyteStream() {
    final String streamName = "name";
    final String streamNamespace = "namespace";
    final List<Field> discoveredFields = List.of(new Field("field1", JsonSchemaType.STRING),
        new Field("field2", JsonSchemaType.NUMBER));

    final AirbyteStream airbyteStream = MongoCatalogHelper.buildAirbyteStream(streamName, streamNamespace, discoveredFields);

    assertNotNull(airbyteStream);
    assertEquals(streamNamespace, airbyteStream.getNamespace());
    assertEquals(streamName, airbyteStream.getName());
    assertEquals(List.of(DEFAULT_CURSOR_FIELD), airbyteStream.getDefaultCursorField());
    assertEquals(true, airbyteStream.getSourceDefinedCursor());
    assertEquals(List.of(List.of(DEFAULT_PRIMARY_KEY)), airbyteStream.getSourceDefinedPrimaryKey());
    assertEquals(SUPPORTED_SYNC_MODES, airbyteStream.getSupportedSyncModes());
    assertEquals(5, airbyteStream.getJsonSchema().get("properties").size());

    discoveredFields.forEach(f -> assertTrue(airbyteStream.getJsonSchema().get("properties").has(f.getName())));
    assertTrue(airbyteStream.getJsonSchema().get("properties").has(DEFAULT_CURSOR_FIELD));
    assertEquals(JsonSchemaType.NUMBER.getJsonSchemaTypeMap().get("type"),
        airbyteStream.getJsonSchema().get("properties").get(DEFAULT_CURSOR_FIELD).get("type").asText());
    assertTrue(airbyteStream.getJsonSchema().get("properties").has(DebeziumEventConverter.CDC_DELETED_AT));
    assertEquals(JsonSchemaType.STRING.getJsonSchemaTypeMap().get("type"),
        airbyteStream.getJsonSchema().get("properties").get(DebeziumEventConverter.CDC_DELETED_AT).get("type").asText());
    assertTrue(airbyteStream.getJsonSchema().get("properties").has(DebeziumEventConverter.CDC_UPDATED_AT));
    assertEquals(JsonSchemaType.STRING.getJsonSchemaTypeMap().get("type"),
        airbyteStream.getJsonSchema().get("properties").get(DebeziumEventConverter.CDC_UPDATED_AT).get("type").asText());

  }

  @Test
  void testSchemalessModeAirbyteStream() {
    final String streamName = "name";
    final String streamNamespace = "namespace";
    final List<Field> discoveredFields = List.of(new Field("_id", JsonSchemaType.STRING), new Field("field1", JsonSchemaType.STRING),
        new Field("field2", JsonSchemaType.NUMBER));

    final AirbyteStream airbyteStream = MongoCatalogHelper.buildSchemalessAirbyteStream(streamName, streamNamespace, discoveredFields);

    assertNotNull(airbyteStream);
    assertEquals(streamNamespace, airbyteStream.getNamespace());
    assertEquals(streamName, airbyteStream.getName());
    assertEquals(List.of(DEFAULT_CURSOR_FIELD), airbyteStream.getDefaultCursorField());
    assertEquals(true, airbyteStream.getSourceDefinedCursor());
    assertEquals(List.of(List.of(DEFAULT_PRIMARY_KEY)), airbyteStream.getSourceDefinedPrimaryKey());
    assertEquals(SUPPORTED_SYNC_MODES, airbyteStream.getSupportedSyncModes());
    assertEquals(5, airbyteStream.getJsonSchema().get("properties").size());

    // All discovered fields that are not the _id field should be discarded
    assertTrue(airbyteStream.getJsonSchema().get("properties").has(SCHEMALESS_MODE_DATA_FIELD));
    assertEquals(JsonSchemaType.OBJECT.getJsonSchemaTypeMap().get("type"),
        airbyteStream.getJsonSchema().get("properties").get(SCHEMALESS_MODE_DATA_FIELD).get("type").asText());
    assertTrue(airbyteStream.getJsonSchema().get("properties").has(ID_FIELD));
    assertEquals(JsonSchemaType.STRING.getJsonSchemaTypeMap().get("type"),
        airbyteStream.getJsonSchema().get("properties").get(ID_FIELD).get("type").asText());
    assertTrue(airbyteStream.getJsonSchema().get("properties").has(DEFAULT_CURSOR_FIELD));
    assertEquals(JsonSchemaType.NUMBER.getJsonSchemaTypeMap().get("type"),
        airbyteStream.getJsonSchema().get("properties").get(DEFAULT_CURSOR_FIELD).get("type").asText());
    assertTrue(airbyteStream.getJsonSchema().get("properties").has(DebeziumEventConverter.CDC_DELETED_AT));
    assertEquals(JsonSchemaType.STRING.getJsonSchemaTypeMap().get("type"),
        airbyteStream.getJsonSchema().get("properties").get(DebeziumEventConverter.CDC_DELETED_AT).get("type").asText());
    assertTrue(airbyteStream.getJsonSchema().get("properties").has(DebeziumEventConverter.CDC_UPDATED_AT));
    assertEquals(JsonSchemaType.STRING.getJsonSchemaTypeMap().get("type"),
        airbyteStream.getJsonSchema().get("properties").get(DebeziumEventConverter.CDC_UPDATED_AT).get("type").asText());

  }

}
