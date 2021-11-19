/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.db.mongodb;

import static org.bson.BsonType.ARRAY;
import static org.bson.BsonType.DOCUMENT;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.node.ObjectNode;
import com.google.api.client.util.DateTime;
import com.google.common.collect.ImmutableMap;
import com.google.common.collect.Lists;
import com.mongodb.client.AggregateIterable;
import com.mongodb.client.MongoCollection;
import io.airbyte.commons.json.Jsons;
import io.airbyte.commons.util.MoreIterators;
import io.airbyte.db.DataTypeUtils;
import io.airbyte.protocol.models.JsonSchemaPrimitive;
import java.util.Arrays;
import java.util.Collections;
import java.util.HashMap;
import java.util.HashSet;
import java.util.List;
import java.util.Map;
import java.util.Set;
import org.bson.BsonBinary;
import org.bson.BsonDateTime;
import org.bson.BsonDocument;
import org.bson.BsonDocumentReader;
import org.bson.BsonDouble;
import org.bson.BsonInt32;
import org.bson.BsonInt64;
import org.bson.BsonReader;
import org.bson.BsonString;
import org.bson.BsonTimestamp;
import org.bson.BsonType;
import org.bson.Document;
import org.bson.types.Decimal128;
import org.bson.types.ObjectId;
import org.bson.types.Symbol;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class MongoUtils {

  private static final Logger LOGGER = LoggerFactory.getLogger(MongoUtils.class);

  private static final String MISSING_TYPE = "missing";
  private static final String NULL_TYPE = "null";
  private static final String TYPE = "type";
  private static final String AIRBYTE_SUFFIX = "_aibyte_transform";

  public static JsonSchemaPrimitive getType(final BsonType dataType) {
    return switch (dataType) {
      case BOOLEAN -> JsonSchemaPrimitive.BOOLEAN;
      case INT32, INT64, DOUBLE, DECIMAL128 -> JsonSchemaPrimitive.NUMBER;
      case STRING, SYMBOL, BINARY, DATE_TIME, TIMESTAMP, OBJECT_ID, REGULAR_EXPRESSION, JAVASCRIPT -> JsonSchemaPrimitive.STRING;
      case ARRAY -> JsonSchemaPrimitive.ARRAY;
      case DOCUMENT, JAVASCRIPT_WITH_SCOPE -> JsonSchemaPrimitive.OBJECT;
      default -> JsonSchemaPrimitive.STRING;
    };
  }

  public static JsonNode toJsonNode(final Document document, final List<String> columnNames) {
    final ObjectNode objectNode = (ObjectNode) Jsons.jsonNode(Collections.emptyMap());
    formatDocument(document, objectNode, columnNames);
    return objectNode;
  }

  public static Object getBsonValue(final BsonType type, final String value) {
    try {
      return switch (type) {
        case INT32 -> new BsonInt32(Integer.parseInt(value));
        case INT64 -> new BsonInt64(Long.parseLong(value));
        case DOUBLE -> new BsonDouble(Double.parseDouble(value));
        case DECIMAL128 -> Decimal128.parse(value);
        case TIMESTAMP -> new BsonTimestamp(Long.parseLong(value));
        case DATE_TIME -> new BsonDateTime(new DateTime(value).getValue());
        case OBJECT_ID -> new ObjectId(value);
        case SYMBOL -> new Symbol(value);
        case STRING -> new BsonString(value);
        default -> value;
      };
    } catch (final Exception e) {
      LOGGER.error(String.format("Failed to get BsonValue for field type %s", type), e.getMessage());
      return value;
    }
  }

  private static void formatDocument(final Document document, final ObjectNode objectNode, final List<String> columnNames) {
    final BsonDocument bsonDocument = toBsonDocument(document);
    try (final BsonReader reader = new BsonDocumentReader(bsonDocument)) {
      readDocument(reader, objectNode, columnNames);
    } catch (final Exception e) {
      LOGGER.error("Exception while parsing BsonDocument: {}", e.getMessage());
      throw new RuntimeException(e);
    }
  }

  private static ObjectNode readDocument(final BsonReader reader, final ObjectNode jsonNodes, final List<String> columnNames) {
    reader.readStartDocument();
    while (reader.readBsonType() != BsonType.END_OF_DOCUMENT) {
      final var fieldName = reader.readName();
      final var fieldType = reader.getCurrentBsonType();
      if (DOCUMENT.equals(fieldType)) {
        // recursion in used to parse inner documents
        jsonNodes.set(fieldName, readDocument(reader, (ObjectNode) Jsons.jsonNode(Collections.emptyMap()), columnNames));
      } else if (ARRAY.equals(fieldType)) {
        jsonNodes.set(fieldName, readArray(reader, columnNames, fieldName));
      } else {
        readField(reader, jsonNodes, columnNames, fieldName, fieldType);
      }
      transformToStringIfMarked(jsonNodes, columnNames, fieldName);
    }
    reader.readEndDocument();

    return jsonNodes;
  }

  private static void transformToStringIfMarked(final ObjectNode jsonNodes, final List<String> columnNames, final String fieldName) {
    if (columnNames.contains(fieldName + AIRBYTE_SUFFIX)) {
      jsonNodes.put(fieldName, jsonNodes.get(fieldName).asText());
    }
  }

  private static JsonNode readArray(final BsonReader reader, final List<String> columnNames, final String fieldName) {
    reader.readStartArray();
    final var elements = Lists.newArrayList();

    while (reader.readBsonType() != BsonType.END_OF_DOCUMENT) {
      final var arrayFieldType = reader.getCurrentBsonType();
      if (DOCUMENT.equals(arrayFieldType)) {
        // recursion is used to read inner doc
        elements.add(readDocument(reader, (ObjectNode) Jsons.jsonNode(Collections.emptyMap()), columnNames));
      } else if (ARRAY.equals(arrayFieldType)) {
        // recursion is used to read inner array
        elements.add(readArray(reader, columnNames, fieldName));
      } else {
        final var element = readField(reader, (ObjectNode) Jsons.jsonNode(Collections.emptyMap()), columnNames, fieldName, arrayFieldType);
        elements.add(element.get(fieldName));
      }
    }
    reader.readEndArray();
    return Jsons.jsonNode(MoreIterators.toList(elements.iterator()));
  }

  private static ObjectNode readField(final BsonReader reader,
                                      final ObjectNode o,
                                      final List<String> columnNames,
                                      final String fieldName,
                                      final BsonType fieldType) {
    switch (fieldType) {
      case BOOLEAN -> o.put(fieldName, reader.readBoolean());
      case INT32 -> o.put(fieldName, reader.readInt32());
      case INT64 -> o.put(fieldName, reader.readInt64());
      case DOUBLE -> o.put(fieldName, reader.readDouble());
      case DECIMAL128 -> o.put(fieldName, toDouble(reader.readDecimal128()));
      case TIMESTAMP -> o.put(fieldName, DataTypeUtils.toISO8601StringWithMilliseconds(reader.readTimestamp().getValue()));
      case DATE_TIME -> o.put(fieldName, DataTypeUtils.toISO8601String(reader.readDateTime()));
      case BINARY -> o.put(fieldName, toByteArray(reader.readBinaryData()));
      case SYMBOL -> o.put(fieldName, reader.readSymbol());
      case STRING -> o.put(fieldName, reader.readString());
      case OBJECT_ID -> o.put(fieldName, toString(reader.readObjectId()));
      case JAVASCRIPT -> o.put(fieldName, reader.readJavaScript());
      case JAVASCRIPT_WITH_SCOPE -> readJavaScriptWithScope(o, reader, fieldName, columnNames);
      case REGULAR_EXPRESSION -> toString(reader.readRegularExpression());
      default -> reader.skipValue();
    }
    return o;
  }

  /**
   * Gets 10.000 documents from collection, gathers all unique fields and its type. In case when one
   * field has different types in 2 and more documents, the type is set to String.
   *
   * @param collection mongo collection
   * @return map of unique fields and its type
   */
  public static Map<String, BsonType> getUniqueFields(final MongoCollection<Document> collection) {

    Map<String, BsonType> result = new HashMap<>();
    var allkeys = getFieldsName(collection);
    allkeys.forEach(key -> {
      var types = getTypes(collection, key);
      addUniqueType(result, collection, key, types);
    });

    return result;
  }

  private static List<String> getFieldsName(MongoCollection<Document> collection) {
    AggregateIterable<Document> output = collection.aggregate(Arrays.asList(
        new Document("$project", new Document("arrayofkeyvalue", new Document("$objectToArray", "$$ROOT"))),
        new Document("$unwind", "$arrayofkeyvalue"),
        new Document("$group", new Document("_id", null).append("allkeys", new Document("$addToSet", "$arrayofkeyvalue.k")))));
    if (output.cursor().hasNext()) {
      return (List) output.cursor().next().get("allkeys");
    } else {
      return Collections.emptyList();
    }
  }

  private static void addUniqueType(Map<String, BsonType> map,
                                    MongoCollection<Document> collection,
                                    String fieldName,
                                    Set<String> types) {
    if (types.size() != 1) {
      map.put(fieldName + AIRBYTE_SUFFIX, BsonType.STRING);
    } else {
      var document = collection.find(new Document(fieldName,
          new Document("$type", types.stream().findFirst().get()))).first();
      var bsonDoc = toBsonDocument(document);
      try (final BsonReader reader = new BsonDocumentReader(bsonDoc)) {
        reader.readStartDocument();
        while (reader.readBsonType() != BsonType.END_OF_DOCUMENT) {
          if (reader.readName().equals(fieldName)) {
            final var fieldType = reader.getCurrentBsonType();
            map.put(fieldName, fieldType);
          }
          reader.skipValue();
        }
        reader.readEndDocument();
      }
    }
  }

  private static Set<String> getTypes(MongoCollection<Document> collection, String fieldName) {
    var searchField = "$" + fieldName;
    var docTypes = collection.aggregate(List.of(
        new Document("$project", new Document(TYPE, new Document("$type", searchField))))).cursor();
    Set<String> types = new HashSet<>();
    while (docTypes.hasNext()) {
      var type = String.valueOf(docTypes.next().get(TYPE));
      if (!MISSING_TYPE.equals(type) && !NULL_TYPE.equals(type)) {
        types.add(type);
      }
    }
    return types.isEmpty() ? Set.of(NULL_TYPE) : types;
  }

  private static BsonDocument toBsonDocument(final Document document) {
    try {
      return document.toBsonDocument();
    } catch (final Exception e) {
      LOGGER.error("Exception while converting Document to BsonDocument: {}", e.getMessage());
      throw new RuntimeException(e);
    }
  }

  private static String toString(final Object value) {
    return value == null ? null : value.toString();
  }

  private static Double toDouble(final Decimal128 value) {
    return value == null ? null : value.doubleValue();
  }

  private static byte[] toByteArray(final BsonBinary value) {
    return value == null ? null : value.getData();
  }

  private static void readJavaScriptWithScope(ObjectNode o, BsonReader reader, String fieldName, List<String> columnNames) {
    var code = reader.readJavaScriptWithScope();
    var scope = readDocument(reader, (ObjectNode) Jsons.jsonNode(Collections.emptyMap()), columnNames);
    o.set(fieldName, Jsons.jsonNode(ImmutableMap.of("code", code, "scope", scope)));
  }

  public enum MongoInstanceType {

    STANDALONE("standalone"),
    REPLICA("replica"),
    ATLAS("atlas");

    private final String type;

    public String getType() {
      return this.type;
    }

    MongoInstanceType(final String type) {
      this.type = type;
    }

    public static MongoInstanceType fromValue(final String value) {
      for (final MongoInstanceType instance : values()) {
        if (value.equalsIgnoreCase(instance.type)) {
          return instance;
        }
      }
      throw new IllegalArgumentException("Unknown instance type value: " + value);
    }

  }

}
