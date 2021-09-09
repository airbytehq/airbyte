/*
 * MIT License
 *
 * Copyright (c) 2020 Airbyte
 *
 * Permission is hereby granted, free of charge, to any person obtaining a copy
 * of this software and associated documentation files (the "Software"), to deal
 * in the Software without restriction, including without limitation the rights
 * to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
 * copies of the Software, and to permit persons to whom the Software is
 * furnished to do so, subject to the following conditions:
 *
 * The above copyright notice and this permission notice shall be included in all
 * copies or substantial portions of the Software.
 *
 * THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
 * IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
 * FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
 * AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
 * LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
 * OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
 * SOFTWARE.
 */

package io.airbyte.db.mongodb;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.node.ObjectNode;
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
import org.bson.BsonDocument;
import org.bson.BsonDocumentReader;
import org.bson.BsonReader;
import org.bson.BsonType;
import org.bson.Document;
import org.bson.conversions.Bson;
import org.bson.types.Decimal128;
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

  private static void readBson(final Document document, final ObjectNode o, final List<String> columnNames) {
    final BsonDocument bsonDocument = toBsonDocument(document);
    try (BsonReader reader = new BsonDocumentReader(bsonDocument)) {
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
    } catch (Exception e) {
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
  public static Map<String, BsonType> getUniqueFields(MongoCollection<Document> collection) {
    Map<String, BsonType> uniqueFields = new HashMap<>();
    try (MongoCursor<Document> cursor = collection.find().batchSize(DISCOVERY_BATCH_SIZE).iterator()) {
      while (cursor.hasNext()) {
        BsonDocument document = toBsonDocument(cursor.next());
        try (BsonReader reader = new BsonDocumentReader(document)) {
          reader.readStartDocument();
          while (reader.readBsonType() != BsonType.END_OF_DOCUMENT) {
            var fieldName = reader.readName();
            var fieldType = reader.getCurrentBsonType();
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
    } catch (Exception e) {
      LOGGER.error("Exception while converting Document to BsonDocument: ", e.getMessage());
      throw new RuntimeException(e);
    }
  }

  private static String toString(Object value) {
    return value == null ? null : value.toString();
  }

  private static Double toDouble(Decimal128 value) {
    return value == null ? null : value.doubleValue();
  }

  private static byte[] toByteArray(BsonBinary value) {
    return value == null ? null : value.getData();
  }

  // temporary method for MVP
  private static String documentToString(Object obj, BsonReader reader) {
    try {
      reader.skipValue();
      Document document = (Document) obj;
      return document.toJson();
    } catch (Exception e) {
      LOGGER.error("Failed to convert document to a String: ", e.getMessage());
      return null;
    }
  }

  // temporary method for MVP
  private static String arrayToString(Object obj, BsonReader reader) {
    try {
      reader.skipValue();
      return obj.toString();
    } catch (Exception e) {
      LOGGER.error("Failed to convert array to a String: ", e.getMessage());
      return null;
    }
  }

}
