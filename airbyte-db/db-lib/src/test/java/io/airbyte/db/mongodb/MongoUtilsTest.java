/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.db.mongodb;

import static io.airbyte.db.mongodb.MongoUtils.AIRBYTE_SUFFIX;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertNotNull;
import static org.junit.jupiter.api.Assertions.assertNull;
import static org.junit.jupiter.api.Assertions.assertTrue;
import static org.mockito.ArgumentMatchers.any;
import static org.mockito.Mockito.mock;
import static org.mockito.Mockito.when;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.node.ObjectNode;
import com.google.api.client.util.DateTime;
import io.airbyte.commons.json.Jsons;
import io.airbyte.protocol.models.JsonSchemaType;
import java.util.List;
import java.util.Map;
import java.util.Set;
import org.bson.BsonDateTime;
import org.bson.BsonDocument;
import org.bson.BsonDouble;
import org.bson.BsonInt32;
import org.bson.BsonInt64;
import org.bson.BsonString;
import org.bson.BsonTimestamp;
import org.bson.BsonType;
import org.bson.BsonValue;
import org.bson.Document;
import org.bson.types.Decimal128;
import org.bson.types.ObjectId;
import org.bson.types.Symbol;
import org.junit.jupiter.api.Test;

class MongoUtilsTest {

  @Test
  void testBsonTypeToJsonSchemaType() {
    assertEquals(JsonSchemaType.BOOLEAN, MongoUtils.getType(BsonType.BOOLEAN));
    assertEquals(JsonSchemaType.NUMBER, MongoUtils.getType(BsonType.INT32));
    assertEquals(JsonSchemaType.NUMBER, MongoUtils.getType(BsonType.DOUBLE));
    assertEquals(JsonSchemaType.NUMBER, MongoUtils.getType(BsonType.DECIMAL128));
    assertEquals(JsonSchemaType.STRING, MongoUtils.getType(BsonType.STRING));
    assertEquals(JsonSchemaType.STRING, MongoUtils.getType(BsonType.SYMBOL));
    assertEquals(JsonSchemaType.STRING, MongoUtils.getType(BsonType.BINARY));
    assertEquals(JsonSchemaType.STRING, MongoUtils.getType(BsonType.DATE_TIME));
    assertEquals(JsonSchemaType.STRING, MongoUtils.getType(BsonType.OBJECT_ID));
    assertEquals(JsonSchemaType.STRING, MongoUtils.getType(BsonType.REGULAR_EXPRESSION));
    assertEquals(JsonSchemaType.STRING, MongoUtils.getType(BsonType.JAVASCRIPT));
    assertEquals(JsonSchemaType.STRING, MongoUtils.getType(BsonType.TIMESTAMP));
    assertEquals(JsonSchemaType.ARRAY, MongoUtils.getType(BsonType.ARRAY));
    assertEquals(JsonSchemaType.OBJECT, MongoUtils.getType(BsonType.DOCUMENT));
    assertEquals(JsonSchemaType.OBJECT, MongoUtils.getType(BsonType.JAVASCRIPT_WITH_SCOPE));
    assertEquals(JsonSchemaType.STRING, MongoUtils.getType(BsonType.MAX_KEY));
  }

  @Test
  void testBsonToJsonValue() {
    final String timestamp = "2023-07-11T10:16:32.000";
    final ObjectId objectId = new ObjectId();
    final String value = "5";
    assertEquals(new BsonInt32(Integer.parseInt(value)), MongoUtils.getBsonValue(BsonType.INT32, value));
    assertEquals(new BsonInt64(Integer.parseInt(value)), MongoUtils.getBsonValue(BsonType.INT64, value));
    assertEquals(new BsonDouble(5.5), MongoUtils.getBsonValue(BsonType.DOUBLE, "5.5"));
    assertEquals(Decimal128.parse(value), MongoUtils.getBsonValue(BsonType.DECIMAL128, value));
    assertEquals(new BsonTimestamp(new DateTime(timestamp).getValue()), MongoUtils.getBsonValue(BsonType.TIMESTAMP, timestamp));
    assertEquals(new BsonDateTime(new DateTime(timestamp).getValue()), MongoUtils.getBsonValue(BsonType.DATE_TIME, timestamp));
    assertEquals(objectId, MongoUtils.getBsonValue(BsonType.OBJECT_ID, objectId.toHexString()));
    assertEquals(new Symbol(value), MongoUtils.getBsonValue(BsonType.SYMBOL, value));
    assertEquals(new BsonString(value), MongoUtils.getBsonValue(BsonType.STRING, value));

    // Default case
    assertEquals(value, MongoUtils.getBsonValue(BsonType.MAX_KEY, value));

    // Error case
    assertEquals(value, MongoUtils.getBsonValue(BsonType.DATE_TIME, value));
  }

  @Test
  void testToJsonNodeFromDocument() {
    final String key = "key";
    final String value = "foo";
    final BsonDocument bsonDocument = mock(BsonDocument.class);
    final Document document = mock(Document.class);
    final Set<Map.Entry<String, org.bson.BsonValue>> entrySet = Map.of(key, (BsonValue) new BsonString(value)).entrySet();

    when(document.toBsonDocument(any(), any())).thenReturn(bsonDocument);
    when(bsonDocument.asDocument()).thenReturn(bsonDocument);
    when(bsonDocument.entrySet()).thenReturn(entrySet);

    final JsonNode jsonNode = MongoUtils.toJsonNode(document, List.of());
    assertNotNull(jsonNode);
    assertEquals(value, jsonNode.get(key).asText());
  }

  @Test
  void testToJsonNodeFromBsonDocument() {
    final String key = "key";
    final String value = "foo";
    final BsonDocument bsonDocument = mock(BsonDocument.class);
    final Set<Map.Entry<String, org.bson.BsonValue>> entrySet = Map.of(key, (BsonValue) new BsonString(value)).entrySet();

    when(bsonDocument.asDocument()).thenReturn(bsonDocument);
    when(bsonDocument.entrySet()).thenReturn(entrySet);

    final JsonNode jsonNode = MongoUtils.toJsonNode(bsonDocument, List.of());
    assertNotNull(jsonNode);
    assertEquals(value, jsonNode.get(key).asText());
  }

  @Test
  void testTransformToStringIfMarked() {
    final List<String> columnNames = List.of("_id", "createdAt", "connectedWallets", "connectedAccounts_aibyte_transform");
    final String fieldName = "connectedAccounts";
    final JsonNode node = Jsons.deserialize("""
                                            {
                                              "_id":"12345678as",
                                              "createdAt":"2022-11-11 12:13:14",
                                              "connectedWallets":"wallet1",
                                              "connectedAccounts":{
                                                  "google":{
                                                    "provider":"google",
                                                    "refreshToken":"test-rfrsh-google-token-1",
                                                    "accessToken":"test-access-google-token-1",
                                                    "expiresAt":"2020-09-01T21:07:00Z",
                                                    "createdAt":"2020-09-01T20:07:01Z"
                                                  },
                                                  "figma":{
                                                    "provider":"figma",
                                                    "refreshToken":"test-rfrsh-figma-token-1",
                                                    "accessToken":"test-access-figma-token-1",
                                                    "expiresAt":"2020-12-13T22:08:03Z",
                                                    "createdAt":"2020-09-14T22:08:03Z",
                                                    "figmaInfo":{
                                                      "teamID":"501087711831561793"
                                                    }
                                                  },
                                                  "slack":{
                                                    "provider":"slack",
                                                    "accessToken":"test-access-slack-token-1",
                                                    "createdAt":"2020-09-01T20:15:07Z",
                                                    "slackInfo":{
                                                      "userID":"UM5AD2YCE",
                                                      "teamID":"T2VGY5GH5"
                                                    }
                                                  }
                                              }
                                            }""");
    assertTrue(node.get(fieldName).isObject());

    MongoUtils.transformToStringIfMarked((ObjectNode) node, columnNames, fieldName);

    assertNull(node.get(fieldName));
    assertNotNull(node.get(fieldName + AIRBYTE_SUFFIX));
    assertTrue(node.get(fieldName + AIRBYTE_SUFFIX).isTextual());

  }

}
