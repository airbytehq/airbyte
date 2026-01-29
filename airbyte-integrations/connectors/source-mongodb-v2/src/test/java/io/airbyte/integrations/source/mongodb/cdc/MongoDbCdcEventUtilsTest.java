/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.mongodb.cdc;

import static io.airbyte.integrations.source.mongodb.cdc.MongoDbCdcEventUtils.DOCUMENT_OBJECT_ID_FIELD;
import static io.airbyte.integrations.source.mongodb.cdc.MongoDbCdcEventUtils.ID_FIELD;
import static io.airbyte.integrations.source.mongodb.cdc.MongoDbCdcEventUtils.OBJECT_ID_FIELD;
import static io.airbyte.integrations.source.mongodb.cdc.MongoDbCdcEventUtils.OBJECT_ID_FIELD_PATTERN;
import static io.airbyte.integrations.source.mongodb.cdc.MongoDbDebeziumConstants.Configuration.SCHEMALESS_MODE_DATA_FIELD;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertNotEquals;
import static org.junit.jupiter.api.Assertions.assertNotNull;
import static org.junit.jupiter.api.Assertions.assertNull;
import static org.junit.jupiter.api.Assertions.assertTrue;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.node.JsonNodeType;
import com.fasterxml.jackson.databind.node.ObjectNode;
import io.airbyte.cdk.db.DataTypeUtils;
import io.airbyte.commons.json.Jsons;
import java.nio.charset.Charset;
import java.util.*;
import org.bson.BsonBinary;
import org.bson.BsonBoolean;
import org.bson.BsonDateTime;
import org.bson.BsonDecimal128;
import org.bson.BsonDocument;
import org.bson.BsonDouble;
import org.bson.BsonInt32;
import org.bson.BsonInt64;
import org.bson.BsonJavaScript;
import org.bson.BsonJavaScriptWithScope;
import org.bson.BsonNull;
import org.bson.BsonObjectId;
import org.bson.BsonRegularExpression;
import org.bson.BsonString;
import org.bson.BsonSymbol;
import org.bson.BsonTimestamp;
import org.bson.Document;
import org.bson.UuidRepresentation;
import org.bson.types.Decimal128;
import org.bson.types.ObjectId;
import org.junit.jupiter.api.Test;

class MongoDbCdcEventUtilsTest {

  private static final String OBJECT_ID = "64f24244f95155351c4185b1";

  @Test
  void testGenerateObjectIdDocument() {
    final String key = "{\"" + OBJECT_ID_FIELD + "\": \"" + OBJECT_ID + "\"}";
    JsonNode debeziumEventKey = Jsons.jsonNode(Map.of(ID_FIELD, key));

    String updated = MongoDbCdcEventUtils.generateObjectIdDocument(debeziumEventKey);

    assertTrue(updated.contains(DOCUMENT_OBJECT_ID_FIELD));
    assertEquals(key.replaceAll(OBJECT_ID_FIELD_PATTERN, DOCUMENT_OBJECT_ID_FIELD), updated);

    debeziumEventKey = Jsons.jsonNode(Map.of(ID_FIELD, "\"" + OBJECT_ID + "\""));
    updated = MongoDbCdcEventUtils.generateObjectIdDocument(debeziumEventKey);
    assertTrue(updated.contains(DOCUMENT_OBJECT_ID_FIELD));
    assertEquals(Jsons.serialize(Jsons.jsonNode(Map.of(DOCUMENT_OBJECT_ID_FIELD, OBJECT_ID))), updated);
  }

  @Test
  void testNormalizeObjectId() {
    final JsonNode data = MongoDbCdcEventUtils.normalizeObjectId((ObjectNode) Jsons.jsonNode(
        Map.of(DOCUMENT_OBJECT_ID_FIELD, Map.of(OBJECT_ID_FIELD, OBJECT_ID))));
    assertEquals(OBJECT_ID, data.get(DOCUMENT_OBJECT_ID_FIELD).asText());

    final JsonNode dataWithoutObjectId = MongoDbCdcEventUtils.normalizeObjectId((ObjectNode) Jsons.jsonNode(
        Map.of(DOCUMENT_OBJECT_ID_FIELD, Map.of())));
    assertNotEquals(OBJECT_ID, dataWithoutObjectId.get(DOCUMENT_OBJECT_ID_FIELD).asText());

    final JsonNode dataWithoutId = MongoDbCdcEventUtils.normalizeObjectId((ObjectNode) Jsons.jsonNode(Map.of()));
    assertNull(dataWithoutId.get(DOCUMENT_OBJECT_ID_FIELD));

    final JsonNode stringId = MongoDbCdcEventUtils.normalizeObjectId((ObjectNode) Jsons.jsonNode(Map.of(DOCUMENT_OBJECT_ID_FIELD, "abcd")));
    assertEquals("abcd", stringId.get(DOCUMENT_OBJECT_ID_FIELD).asText());
  }

  @Test
  void testNormalizeObjectIdNoSchema() {
    var objectNode = (ObjectNode) Jsons.jsonNode(Map.of(DOCUMENT_OBJECT_ID_FIELD, Map.of(OBJECT_ID_FIELD, OBJECT_ID)));
    objectNode.set(SCHEMALESS_MODE_DATA_FIELD,
        Jsons.jsonNode(Map.of(DOCUMENT_OBJECT_ID_FIELD, Map.of(OBJECT_ID_FIELD, OBJECT_ID))));

    final JsonNode data = MongoDbCdcEventUtils.normalizeObjectIdNoSchema(objectNode);
    assertEquals(OBJECT_ID, data.get(DOCUMENT_OBJECT_ID_FIELD).asText());
    assertEquals(OBJECT_ID, data.get(SCHEMALESS_MODE_DATA_FIELD).get(DOCUMENT_OBJECT_ID_FIELD).asText());

    objectNode = (ObjectNode) Jsons.jsonNode(Map.of(DOCUMENT_OBJECT_ID_FIELD, Map.of()));
    objectNode.set(SCHEMALESS_MODE_DATA_FIELD, Jsons.jsonNode(Map.of(DOCUMENT_OBJECT_ID_FIELD, Map.of())));
    final JsonNode dataWithoutObjectId = MongoDbCdcEventUtils.normalizeObjectIdNoSchema(objectNode);
    assertNotEquals(OBJECT_ID, dataWithoutObjectId.get(DOCUMENT_OBJECT_ID_FIELD).asText());
    assertNotEquals(OBJECT_ID, dataWithoutObjectId.get(SCHEMALESS_MODE_DATA_FIELD).get(DOCUMENT_OBJECT_ID_FIELD).asText());

    final JsonNode dataWithoutId = MongoDbCdcEventUtils.normalizeObjectIdNoSchema((ObjectNode) Jsons.jsonNode(Map.of()));
    assertNull(dataWithoutId.get(DOCUMENT_OBJECT_ID_FIELD));
  }

  // Helper method to create a simple schema map (for tests that don't need type checking)
  private Map<String, JsonNode> toSchemaMap(Set<String> fieldNames) {
    final Map<String, JsonNode> schemaMap = new HashMap<>();
    for (String fieldName : fieldNames) {
      schemaMap.put(fieldName, Jsons.jsonNode(Collections.emptyMap()));
    }
    return schemaMap;
  }

  @Test
  void testTransformDataTypes() {
    final BsonTimestamp bsonTimestamp = new BsonTimestamp(394, 1926745562);
    final String expectedTimestamp = DataTypeUtils.toISO8601StringWithMilliseconds(bsonTimestamp.getValue());
    final UUID standardUuid = UUID.randomUUID();
    final UUID legacyUuid = UUID.randomUUID();

    final Document document = new Document("field1", new BsonBoolean(true))
        .append("field2", new BsonInt32(1))
        .append("field3", new BsonInt64(2))
        .append("field4", new BsonDouble(3.0))
        .append("field5", new BsonDecimal128(new Decimal128(4)))
        .append("field6", bsonTimestamp)
        .append("field7", new BsonDateTime(bsonTimestamp.getValue()))
        .append("field8", new BsonBinary("test".getBytes(Charset.defaultCharset())))
        .append("field9", new BsonSymbol("test2"))
        .append("field10", new BsonString("test3"))
        .append("field11", new BsonObjectId(new ObjectId(OBJECT_ID)))
        .append("field12", new BsonJavaScript("code"))
        .append("field13", new BsonJavaScriptWithScope("code2", new BsonDocument("scope", new BsonString("scope"))))
        .append("field14", new BsonRegularExpression("pattern"))
        .append("field15", new BsonNull())
        .append("field16", new Document("key", "value"))
        .append("field17", new BsonBinary(standardUuid, UuidRepresentation.STANDARD))
        .append("field18", new BsonBinary(legacyUuid, UuidRepresentation.JAVA_LEGACY));

    final String documentAsJson = document.toJson();
    final ObjectNode transformed = MongoDbCdcEventUtils.transformDataTypes(documentAsJson, toSchemaMap(document.keySet()));

    assertNotNull(transformed);
    assertNotEquals(documentAsJson, Jsons.serialize(transformed));
    assertEquals(true, transformed.get("field1").asBoolean());
    assertEquals(1, transformed.get("field2").asInt());
    assertEquals(2, transformed.get("field3").asInt());
    assertEquals(3.0, transformed.get("field4").asDouble());
    assertEquals(4.0, transformed.get("field5").asDouble());
    assertEquals(expectedTimestamp, transformed.get("field6").asText());
    assertEquals(expectedTimestamp, transformed.get("field7").asText());
    assertEquals(Base64.getEncoder().encodeToString("test".getBytes(Charset.defaultCharset())), transformed.get("field8").asText());
    assertEquals("test2", transformed.get("field9").asText());
    assertEquals("test3", transformed.get("field10").asText());
    assertEquals(OBJECT_ID, transformed.get("field11").asText());
    assertEquals("code", transformed.get("field12").asText());
    assertEquals("code2", transformed.get("field13").get("code").asText());
    assertEquals("scope", transformed.get("field13").get("scope").get("scope").asText());
    assertEquals("pattern", transformed.get("field14").asText());
    assertTrue(transformed.has("field15"));
    assertEquals(JsonNodeType.NULL, transformed.get("field15").getNodeType());
    assertEquals("value", transformed.get("field16").get("key").asText());
    // Assert that UUIDs can be serialized. Currently, they will be represented as base 64 encoded
    // strings. Since the original mongo source
    // may have these UUIDs written by a variety of sources, each with different encodings - we cannot
    // decode these back to the original UUID.
    assertTrue(transformed.has("field17"));
    assertTrue(transformed.has("field18"));
  }

  @Test
  void testTransformDataTypesWithFilteredFields() {
    final BsonTimestamp bsonTimestamp = new BsonTimestamp(394, 1926745562);
    final String expectedTimestamp = DataTypeUtils.toISO8601StringWithMilliseconds(bsonTimestamp.getValue());

    final Document document = new Document("field1", new BsonBoolean(true))
        .append("field2", new BsonInt32(1))
        .append("field3", new BsonInt64(2))
        .append("field4", new BsonDouble(3.0))
        .append("field5", new BsonDecimal128(new Decimal128(4)))
        .append("field6", bsonTimestamp)
        .append("field7", new BsonDateTime(bsonTimestamp.getValue()))
        .append("field8", new BsonBinary("test".getBytes(Charset.defaultCharset())))
        .append("field9", new BsonSymbol("test2"))
        .append("field10", new BsonString("test3"))
        .append("field11", new BsonObjectId(new ObjectId(OBJECT_ID)))
        .append("field12", new BsonJavaScript("code"))
        .append("field13", new BsonJavaScriptWithScope("code2", new BsonDocument("scope", new BsonString("scope"))))
        .append("field14", new BsonRegularExpression("pattern"))
        .append("field15", new BsonNull())
        .append("field16", new Document("key", "value"));

    final String documentAsJson = document.toJson();
    final ObjectNode transformed = MongoDbCdcEventUtils.transformDataTypes(documentAsJson, toSchemaMap(Set.of("field1", "field2", "field3")));

    assertNotNull(transformed);
    assertNotEquals(documentAsJson, Jsons.serialize(transformed));
    assertEquals(true, transformed.get("field1").asBoolean());
    assertEquals(1, transformed.get("field2").asInt());
    assertEquals(2, transformed.get("field3").asInt());
    assertFalse(transformed.has("field4"));
    assertFalse(transformed.has("field5"));
    assertFalse(transformed.has("field6"));
    assertFalse(transformed.has("field7"));
    assertFalse(transformed.has("field8"));
    assertFalse(transformed.has("field9"));
    assertFalse(transformed.has("field10"));
    assertFalse(transformed.has("field11"));
    assertFalse(transformed.has("field12"));
    assertFalse(transformed.has("field13"));
    assertFalse(transformed.has("field14"));
    assertFalse(transformed.has("field15"));
    assertFalse(transformed.has("field16"));
  }

  @Test
  void testTransformDataTypesNoSchema() {
    final BsonTimestamp bsonTimestamp = new BsonTimestamp(394, 1926745562);
    final String expectedTimestamp = DataTypeUtils.toISO8601StringWithMilliseconds(bsonTimestamp.getValue());

    final Document document = new Document("field1", new BsonBoolean(true))
        .append("field2", new BsonInt32(1))
        .append("field3", new BsonInt64(2))
        .append("field4", new BsonDouble(3.0))
        .append("field5", new BsonDecimal128(new Decimal128(4)))
        .append("field6", bsonTimestamp)
        .append("field7", new BsonDateTime(bsonTimestamp.getValue()))
        .append("field8", new BsonBinary("test".getBytes(Charset.defaultCharset())))
        .append("field9", new BsonSymbol("test2"))
        .append("field10", new BsonString("test3"))
        .append("field11", new BsonObjectId(new ObjectId(OBJECT_ID)))
        .append("field12", new BsonJavaScript("code"))
        .append("field13", new BsonJavaScriptWithScope("code2", new BsonDocument("scope", new BsonString("scope"))))
        .append("field14", new BsonRegularExpression("pattern"))
        .append("field15", new BsonNull())
        .append("field16", new Document("key", "value"));

    final String documentAsJson = document.toJson();
    final ObjectNode transformed = MongoDbCdcEventUtils.transformDataTypesNoSchema(documentAsJson);

    assertNotNull(transformed);
    final var abDataNode = transformed.get(SCHEMALESS_MODE_DATA_FIELD);
    assertNotEquals(documentAsJson, Jsons.serialize(abDataNode));
    assertEquals(true, abDataNode.get("field1").asBoolean());
    assertEquals(1, abDataNode.get("field2").asInt());
    assertEquals(2, abDataNode.get("field3").asInt());
    assertEquals(3.0, abDataNode.get("field4").asDouble());
    assertEquals(4.0, abDataNode.get("field5").asDouble());
    assertTrue(abDataNode.has("field6"));
    assertTrue(abDataNode.has("field7"));
    assertTrue(abDataNode.has("field8"));
    assertTrue(abDataNode.has("field9"));
    assertTrue(abDataNode.has("field10"));
    assertTrue(abDataNode.has("field11"));
    assertTrue(abDataNode.has("field12"));
    assertTrue(abDataNode.has("field13"));
    assertTrue(abDataNode.has("field14"));
    assertTrue(abDataNode.has("field15"));
    assertEquals(JsonNodeType.NULL, abDataNode.get("field15").getNodeType());
    assertTrue(abDataNode.has("field16"));
  }

  /*
   * The following tests the dynamic array wrapping functionality. If discovery identifies a field as
   * an array, the schema expects an array. Since MongoDB is dynamic, users can store int, object, or
   * string values in that field. To prevent destinations from nulling out these values due to type
   * mismatch, we wrap them in arrays.
   */
  @Test
  void testTransformDataTypesWrapsObjectInArrayWhenSchemaExpectsArray() {
    // Document has single object in "reviews", but schema expects array of objects
    final Document document = new Document("_id", new BsonObjectId(new ObjectId(OBJECT_ID)))
        .append("reviews", new Document("rating", "A").append("score", 10));

    final String documentAsJson = document.toJson();

    // Schema says "reviews" should be an array
    final Map<String, JsonNode> schemaMap = Map.of(
        "_id", Jsons.jsonNode(Map.of("type", "string")),
        "reviews", Jsons.jsonNode(Map.of("type", "array")));

    final ObjectNode transformed = MongoDbCdcEventUtils.transformDataTypes(documentAsJson, schemaMap);

    assertNotNull(transformed);
    assertTrue(transformed.get("reviews").isArray());
    assertEquals(1, transformed.get("reviews").size());
    assertEquals("A", transformed.get("reviews").get(0).get("rating").asText());
    assertEquals(10, transformed.get("reviews").get(0).get("score").asInt());
  }

  @Test
  void testTransformDataTypesWrapsIntInArrayWhenSchemaExpectsArray() {
    // Document has an int in "scores", but schema expects array
    final Document document = new Document("_id", new BsonObjectId(new ObjectId(OBJECT_ID)))
        .append("scores", new BsonInt32(50));

    final String documentAsJson = document.toJson();

    // Schema says "scores" should be an array
    final Map<String, JsonNode> schemaMap = Map.of(
        "_id", Jsons.jsonNode(Map.of("type", "string")),
        "scores", Jsons.jsonNode(Map.of("type", "array")));

    final ObjectNode transformed = MongoDbCdcEventUtils.transformDataTypes(documentAsJson, schemaMap);

    assertNotNull(transformed);
    assertTrue(transformed.get("scores").isArray());
    assertEquals(1, transformed.get("scores").size());
    assertEquals(50, transformed.get("scores").get(0).asInt());
  }

  /**
   * Tests the new transformDataTypesAllFields method which includes ALL fields from the document
   * without filtering to a discovered schema. This is used when schema_enforced=true but
   * fail_sync_on_schema_mismatch=false (the new default behavior).
   */
  @Test
  void testTransformDataTypesAllFields() {
    final BsonTimestamp bsonTimestamp = new BsonTimestamp(394, 1926745562);
    final String expectedTimestamp = DataTypeUtils.toISO8601StringWithMilliseconds(bsonTimestamp.getValue());

    final Document document = new Document("field1", new BsonBoolean(true))
        .append("field2", new BsonInt32(1))
        .append("field3", new BsonInt64(2))
        .append("field4", new BsonDouble(3.0))
        .append("field5", new BsonDecimal128(new Decimal128(4)))
        .append("field6", bsonTimestamp)
        .append("field7", new BsonDateTime(bsonTimestamp.getValue()))
        .append("field8", new BsonBinary("test".getBytes(Charset.defaultCharset())))
        .append("field9", new BsonSymbol("test2"))
        .append("field10", new BsonString("test3"))
        .append("field11", new BsonObjectId(new ObjectId(OBJECT_ID)))
        .append("field12", new BsonJavaScript("code"))
        .append("field13", new BsonJavaScriptWithScope("code2", new BsonDocument("scope", new BsonString("scope"))))
        .append("field14", new BsonRegularExpression("pattern"))
        .append("field15", new BsonNull())
        .append("field16", new Document("key", "value"));

    final String documentAsJson = document.toJson();
    // transformDataTypesAllFields should include ALL fields without any filtering
    final ObjectNode transformed = MongoDbCdcEventUtils.transformDataTypesAllFields(documentAsJson);

    assertNotNull(transformed);
    // Verify all fields are present (unlike transformDataTypes with filtered fields)
    assertEquals(true, transformed.get("field1").asBoolean());
    assertEquals(1, transformed.get("field2").asInt());
    assertEquals(2, transformed.get("field3").asInt());
    assertEquals(3.0, transformed.get("field4").asDouble());
    assertEquals(4.0, transformed.get("field5").asDouble());
    assertEquals(expectedTimestamp, transformed.get("field6").asText());
    assertEquals(expectedTimestamp, transformed.get("field7").asText());
    assertEquals(Base64.getEncoder().encodeToString("test".getBytes(Charset.defaultCharset())), transformed.get("field8").asText());
    assertEquals("test2", transformed.get("field9").asText());
    assertEquals("test3", transformed.get("field10").asText());
    assertEquals(OBJECT_ID, transformed.get("field11").asText());
    assertEquals("code", transformed.get("field12").asText());
    assertEquals("code2", transformed.get("field13").get("code").asText());
    assertEquals("scope", transformed.get("field13").get("scope").get("scope").asText());
    assertEquals("pattern", transformed.get("field14").asText());
    assertTrue(transformed.has("field15"));
    assertEquals(JsonNodeType.NULL, transformed.get("field15").getNodeType());
    assertEquals("value", transformed.get("field16").get("key").asText());

    // Verify it does NOT wrap data in a "data" field (unlike schemaless mode)
    assertFalse(transformed.has(SCHEMALESS_MODE_DATA_FIELD));
  }

  /**
   * Tests that transformDataTypesAllFields includes fields that would be filtered out
   * by transformDataTypes when using a limited schema map.
   */
  @Test
  void testTransformDataTypesAllFieldsIncludesUndiscoveredFields() {
    final Document document = new Document("discovered_field", new BsonString("value1"))
        .append("undiscovered_field", new BsonString("value2"))
        .append("another_undiscovered", new BsonInt32(42));

    final String documentAsJson = document.toJson();

    // With transformDataTypes and limited schema, undiscovered fields would be filtered
    final ObjectNode filteredTransform = MongoDbCdcEventUtils.transformDataTypes(documentAsJson, toSchemaMap(Set.of("discovered_field")));
    assertTrue(filteredTransform.has("discovered_field"));
    assertFalse(filteredTransform.has("undiscovered_field"));
    assertFalse(filteredTransform.has("another_undiscovered"));

    // With transformDataTypesAllFields, ALL fields should be included
    final ObjectNode allFieldsTransform = MongoDbCdcEventUtils.transformDataTypesAllFields(documentAsJson);
    assertTrue(allFieldsTransform.has("discovered_field"));
    assertTrue(allFieldsTransform.has("undiscovered_field"));
    assertTrue(allFieldsTransform.has("another_undiscovered"));
    assertEquals("value1", allFieldsTransform.get("discovered_field").asText());
    assertEquals("value2", allFieldsTransform.get("undiscovered_field").asText());
    assertEquals(42, allFieldsTransform.get("another_undiscovered").asInt());
  }

}
