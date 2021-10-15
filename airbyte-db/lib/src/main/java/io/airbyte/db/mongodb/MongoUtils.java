/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.db.mongodb;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.node.ObjectNode;
import com.google.api.client.util.DateTime;
import com.mongodb.client.MongoCollection;
import com.mongodb.client.MongoCursor;
import io.airbyte.commons.json.Jsons;
import io.airbyte.db.DataTypeUtils;
import io.airbyte.protocol.models.JsonSchemaPrimitive;
import java.util.Collections;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
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
import org.bson.conversions.Bson;
import org.bson.types.Decimal128;
import org.bson.types.ObjectId;
import org.bson.types.Symbol;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class MongoUtils {

  private static final Logger LOGGER = LoggerFactory.getLogger(MongoUtils.class);

  private static final int DISCOVERY_BATCH_SIZE = 10000;
  private static final String AIRBYTE_SUFFIX = "_aibyte_transform";

  public static JsonSchemaPrimitive getType(final BsonType dataType) {
    return switch (dataType) {
      case BOOLEAN -> JsonSchemaPrimitive.BOOLEAN;
      case INT32, INT64, DOUBLE, DECIMAL128 -> JsonSchemaPrimitive.NUMBER;
      case STRING, SYMBOL, BINARY, DATE_TIME, TIMESTAMP, OBJECT_ID, REGULAR_EXPRESSION, JAVASCRIPT, JAVASCRIPT_WITH_SCOPE -> JsonSchemaPrimitive.STRING;
      case ARRAY -> JsonSchemaPrimitive.ARRAY;
      case DOCUMENT -> JsonSchemaPrimitive.OBJECT;
      default -> JsonSchemaPrimitive.STRING;
    };
  }

  public static JsonNode toJsonNode(final Document document, final List<String> columnNames) {
    final ObjectNode objectNode = (ObjectNode) Jsons.jsonNode(Collections.emptyMap());
    readBson(document, objectNode, columnNames);
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
      LOGGER.error("Failed to get BsonValue for field type " + type, e.getMessage());
      return value;
    }
  }

  private static void readBson(final Document document, final ObjectNode o, final List<String> columnNames) {
    final BsonDocument bsonDocument = toBsonDocument(document);
    try (final BsonReader reader = new BsonDocumentReader(bsonDocument)) {
      reader.readStartDocument();
      while (reader.readBsonType() != BsonType.END_OF_DOCUMENT) {
        final var fieldName = reader.readName();
        final var fieldType = reader.getCurrentBsonType();

        switch (fieldType) {
          case BOOLEAN -> o.put(fieldName, reader.readBoolean());
          case INT32 -> o.put(fieldName, reader.readInt32());
          case INT64 -> o.put(fieldName, reader.readInt64());
          case DOUBLE -> o.put(fieldName, reader.readDouble());
          case DECIMAL128 -> o.put(fieldName, toDouble(reader.readDecimal128()));
          case TIMESTAMP -> o.put(fieldName, toString(reader.readTimestamp()));
          case DATE_TIME -> o.put(fieldName, DataTypeUtils.toISO8601String(reader.readDateTime()));
          case BINARY -> o.put(fieldName, toByteArray(reader.readBinaryData()));
          case SYMBOL -> o.put(fieldName, reader.readSymbol());
          case STRING -> o.put(fieldName, reader.readString());
          case OBJECT_ID -> o.put(fieldName, toString(reader.readObjectId()));
          case JAVASCRIPT -> o.put(fieldName, reader.readJavaScript());
          case JAVASCRIPT_WITH_SCOPE -> o.put(fieldName, reader.readJavaScriptWithScope());
          case REGULAR_EXPRESSION -> o.put(fieldName, toString(reader.readRegularExpression()));
          case DOCUMENT -> o.put(fieldName, documentToString(document.get(fieldName), reader));
          case ARRAY -> o.put(fieldName, arrayToString(document.get(fieldName), reader));
          default -> reader.skipValue();
        }

        if (columnNames.contains(fieldName + AIRBYTE_SUFFIX)) {
          o.put(fieldName, o.get(fieldName).asText());
        }
      }
      reader.readEndDocument();
    } catch (final Exception e) {
      LOGGER.error("Exception while parsing BsonDocument: ", e.getMessage());
      throw new RuntimeException(e);
    }
  }

  /**
   * Gets 10.000 documents from collection, gathers all unique fields and its type. In case when one
   * field has different types in 2 and more documents, the type is set to String.
   *
   * @param collection mongo collection
   * @return map of unique fields and its type
   */
  public static Map<String, BsonType> getUniqueFields(final MongoCollection<Document> collection) {
    final Map<String, BsonType> uniqueFields = new HashMap<>();
    try (final MongoCursor<Document> cursor = collection.find().batchSize(DISCOVERY_BATCH_SIZE).iterator()) {
      while (cursor.hasNext()) {
        final BsonDocument document = toBsonDocument(cursor.next());
        try (final BsonReader reader = new BsonDocumentReader(document)) {
          reader.readStartDocument();
          while (reader.readBsonType() != BsonType.END_OF_DOCUMENT) {
            final var fieldName = reader.readName();
            final var fieldType = reader.getCurrentBsonType();
            reader.skipValue();
            if (uniqueFields.containsKey(fieldName) && fieldType.compareTo(uniqueFields.get(fieldName)) != 0) {
              uniqueFields.replace(fieldName + AIRBYTE_SUFFIX, BsonType.STRING);
            } else {
              uniqueFields.put(fieldName, fieldType);
            }
          }
          reader.readEndDocument();
        }
      }
    }
    return uniqueFields;
  }

  private static BsonDocument toBsonDocument(final Document document) {
    try {
      return document.toBsonDocument(BsonDocument.class, Bson.DEFAULT_CODEC_REGISTRY);
    } catch (final Exception e) {
      LOGGER.error("Exception while converting Document to BsonDocument: ", e.getMessage());
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

  // temporary method for MVP
  private static String documentToString(final Object obj, final BsonReader reader) {
    try {
      reader.skipValue();
      final Document document = (Document) obj;
      return document.toJson();
    } catch (final Exception e) {
      LOGGER.error("Failed to convert document to a String: ", e.getMessage());
      return null;
    }
  }

  // temporary method for MVP
  private static String arrayToString(final Object obj, final BsonReader reader) {
    try {
      reader.skipValue();
      return obj.toString();
    } catch (final Exception e) {
      LOGGER.error("Failed to convert array to a String: ", e.getMessage());
      return null;
    }
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
