/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.db.mongodb;

import static java.util.Arrays.asList;
import static org.bson.BsonType.ARRAY;
import static org.bson.BsonType.DATE_TIME;
import static org.bson.BsonType.DECIMAL128;
import static org.bson.BsonType.DOCUMENT;
import static org.bson.BsonType.DOUBLE;
import static org.bson.BsonType.INT32;
import static org.bson.BsonType.INT64;
import static org.bson.BsonType.OBJECT_ID;
import static org.bson.BsonType.STRING;
import static org.bson.BsonType.TIMESTAMP;
import static org.bson.codecs.configuration.CodecRegistries.fromProviders;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.node.ObjectNode;
import com.google.api.client.util.DateTime;
import com.google.common.collect.ImmutableMap;
import com.google.common.collect.Lists;
import com.mongodb.DBRefCodecProvider;
import com.mongodb.client.AggregateIterable;
import com.mongodb.client.MongoCollection;
import io.airbyte.commons.json.Jsons;
import io.airbyte.commons.util.MoreIterators;
import io.airbyte.db.DataTypeUtils;
import io.airbyte.db.jdbc.JdbcUtils;
import io.airbyte.protocol.models.CommonField;
import io.airbyte.protocol.models.JsonSchemaType;
import io.airbyte.protocol.models.TreeNode;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.Collections;
import java.util.HashSet;
import java.util.List;
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
import org.bson.codecs.*;
import org.bson.codecs.configuration.CodecRegistry;
import org.bson.codecs.jsr310.Jsr310CodecProvider;
import org.bson.types.Decimal128;
import org.bson.types.ObjectId;
import org.bson.types.Symbol;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class MongoUtils {

  private static final Logger LOGGER = LoggerFactory.getLogger(MongoUtils.class);

  // Shared constants
  public static final String MONGODB_SERVER_URL = "mongodb://%s%s:%s/%s?authSource=admin&ssl=%s";
  public static final String MONGODB_CLUSTER_URL = "mongodb+srv://%s%s/%s?retryWrites=true&w=majority&tls=true";
  public static final String MONGODB_REPLICA_URL = "mongodb://%s%s/%s?authSource=admin&directConnection=false&ssl=true";
  public static final String USER = "user";
  public static final String INSTANCE_TYPE = "instance_type";
  public static final String INSTANCE = "instance";
  public static final String CLUSTER_URL = "cluster_url";
  public static final String SERVER_ADDRESSES = "server_addresses";
  public static final String REPLICA_SET = "replica_set";

  // MongodbDestination specific constants
  public static final String AUTH_TYPE = "auth_type";
  public static final String AUTHORIZATION = "authorization";
  public static final String LOGIN_AND_PASSWORD = "login/password";
  public static final String AIRBYTE_DATA_HASH = "_airbyte_data_hash";

  // MongodbSource specific constants
  public static final String AUTH_SOURCE = "auth_source";
  public static final String PRIMARY_KEY = "_id";
  public static final Set<BsonType> ALLOWED_CURSOR_TYPES = Set.of(DOUBLE, STRING, DOCUMENT, OBJECT_ID, DATE_TIME,
      INT32, TIMESTAMP, INT64, DECIMAL128);

  private static final String MISSING_TYPE = "missing";
  private static final String NULL_TYPE = "null";
  public static final String AIRBYTE_SUFFIX = "_aibyte_transform";
  private static final int DISCOVER_LIMIT = 10000;
  private static final String ID = "_id";

  public static JsonSchemaType getType(final BsonType dataType) {
    return switch (dataType) {
      case BOOLEAN -> JsonSchemaType.BOOLEAN;
      case INT32, INT64, DOUBLE, DECIMAL128 -> JsonSchemaType.NUMBER;
      case STRING, SYMBOL, BINARY, DATE_TIME, TIMESTAMP, OBJECT_ID, REGULAR_EXPRESSION, JAVASCRIPT -> JsonSchemaType.STRING;
      case ARRAY -> JsonSchemaType.ARRAY;
      case DOCUMENT, JAVASCRIPT_WITH_SCOPE -> JsonSchemaType.OBJECT;
      default -> JsonSchemaType.STRING;
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
        case TIMESTAMP -> new BsonTimestamp(new DateTime(value).getValue());
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

  public static CommonField<BsonType> nodeToCommonField(final TreeNode<CommonField<BsonType>> node) {
    final CommonField<BsonType> field = node.getData();
    if (node.hasChildren()) {
      final List<CommonField<BsonType>> subFields = node.getChildren().stream().map(MongoUtils::nodeToCommonField).toList();
      return new CommonField<>(field.getName(), field.getType(), subFields);
    } else {
      return new CommonField<>(field.getName(), field.getType());
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

  /**
   * Determines whether TLS/SSL should be enabled for a standalone instance of MongoDB.
   */
  public static boolean tlsEnabledForStandaloneInstance(final JsonNode config, final JsonNode instanceConfig) {
    return config.has(JdbcUtils.TLS_KEY) ? config.get(JdbcUtils.TLS_KEY).asBoolean()
        : (instanceConfig.has(JdbcUtils.TLS_KEY) ? instanceConfig.get(JdbcUtils.TLS_KEY).asBoolean() : true);
  }

  public static void transformToStringIfMarked(final ObjectNode jsonNodes, final List<String> columnNames, final String fieldName) {
    if (columnNames.contains(fieldName + AIRBYTE_SUFFIX)) {
      final JsonNode data = jsonNodes.get(fieldName);
      if (data != null) {
        jsonNodes.remove(fieldName);
        jsonNodes.put(fieldName + AIRBYTE_SUFFIX, data.isTextual() ? data.asText() : data.toString());
      } else {
        LOGGER.debug("WARNING Field list out of sync, Document doesn't contain field: {}", fieldName);
      }
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
      case DATE_TIME -> o.put(fieldName, DataTypeUtils.toISO8601StringWithMilliseconds(reader.readDateTime()));
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
  public static List<TreeNode<CommonField<BsonType>>> getUniqueFields(final MongoCollection<Document> collection) {
    final var allkeys = new HashSet<>(getFieldsName(collection));

    return allkeys.stream().map(key -> {
      final var types = getTypes(collection, key);
      final var type = getUniqueType(types);
      final var fieldNode = new TreeNode<>(new CommonField<>(transformName(types, key), type));
      if (type.equals(DOCUMENT)) {
        setSubFields(collection, fieldNode, key);
      }
      return fieldNode;
    }).toList();
  }

  /**
   * If one field has different types in 2 and more documents, the name is transformed to
   * 'name_aibyte_transform'.
   *
   * @param types list with field types
   * @param name field name
   * @return name
   */
  private static String transformName(final List<String> types, final String name) {
    return types.size() != 1 ? name + AIRBYTE_SUFFIX : name;
  }

  private static void setSubFields(final MongoCollection<Document> collection,
                                   final TreeNode<CommonField<BsonType>> parentNode,
                                   final String pathToField) {
    final var nestedKeys = getFieldsName(collection, pathToField);
    nestedKeys.forEach(key -> {
      final var types = getTypes(collection, pathToField + "." + key);
      final var nestedType = getUniqueType(types);
      final var childNode = parentNode.addChild(new CommonField<>(transformName(types, key), nestedType));
      if (nestedType.equals(DOCUMENT)) {
        setSubFields(collection, childNode, pathToField + "." + key);
      }
    });
  }

  private static List<String> getFieldsName(final MongoCollection<Document> collection) {
    return getFieldsName(collection, "$ROOT");
  }

  private static List<String> getFieldsName(final MongoCollection<Document> collection, final String fieldName) {
    final AggregateIterable<Document> output = collection.aggregate(Arrays.asList(
        new Document("$limit", DISCOVER_LIMIT),
        new Document("$project", new Document("arrayofkeyvalue", new Document("$objectToArray", "$" + fieldName))),
        new Document("$unwind", "$arrayofkeyvalue"),
        new Document("$group", new Document(ID, null).append("allkeys", new Document("$addToSet", "$arrayofkeyvalue.k")))));
    if (output.cursor().hasNext()) {
      return (List) output.cursor().next().get("allkeys");
    } else {
      return Collections.emptyList();
    }
  }

  private static List<String> getTypes(final MongoCollection<Document> collection, final String name) {
    final var fieldName = "$" + name;
    final AggregateIterable<Document> output = collection.aggregate(Arrays.asList(
        new Document("$limit", DISCOVER_LIMIT),
        new Document("$project", new Document(ID, 0).append("fieldType", new Document("$type", fieldName))),
        new Document("$group", new Document(ID, new Document("fieldType", "$fieldType"))
            .append("count", new Document("$sum", 1)))));
    final var listOfTypes = new ArrayList<String>();
    final var cursor = output.cursor();
    while (cursor.hasNext()) {
      final var type = ((Document) cursor.next().get(ID)).get("fieldType").toString();
      if (!MISSING_TYPE.equals(type) && !NULL_TYPE.equals(type)) {
        listOfTypes.add(type);
      }
    }
    if (listOfTypes.isEmpty()) {
      listOfTypes.add(NULL_TYPE);
    }
    return listOfTypes;
  }

  @SuppressWarnings("PMD.AvoidLiteralsInIfCondition")
  private static BsonType getUniqueType(final List<String> types) {
    if (types.size() != 1) {
      return BsonType.STRING;
    } else {
      final var type = types.get(0);
      return getBsonTypeByTypeAlias(type);
    }
  }

  private static BsonType getBsonTypeByTypeAlias(final String typeAlias) {
    return switch (typeAlias) {
      case "object" -> BsonType.DOCUMENT;
      case "double" -> BsonType.DOUBLE;
      case "string" -> BsonType.STRING;
      case "objectId" -> BsonType.OBJECT_ID;
      case "array" -> BsonType.ARRAY;
      case "binData" -> BsonType.BINARY;
      case "bool" -> BsonType.BOOLEAN;
      case "date" -> BsonType.DATE_TIME;
      case "null" -> BsonType.NULL;
      case "regex" -> BsonType.REGULAR_EXPRESSION;
      case "dbPointer" -> BsonType.DB_POINTER;
      case "javascript" -> BsonType.JAVASCRIPT;
      case "symbol" -> BsonType.SYMBOL;
      case "javascriptWithScope" -> BsonType.JAVASCRIPT_WITH_SCOPE;
      case "int" -> BsonType.INT32;
      case "timestamp" -> BsonType.TIMESTAMP;
      case "long" -> BsonType.INT64;
      case "decimal" -> BsonType.DECIMAL128;
      default -> BsonType.STRING;
    };
  }

  private static BsonDocument toBsonDocument(final Document document) {
    try {
      final CodecRegistry customCodecRegistry =
          fromProviders(asList(
              new ValueCodecProvider(),
              new BsonValueCodecProvider(),
              new DocumentCodecProvider(),
              new IterableCodecProvider(),
              new MapCodecProvider(),
              new Jsr310CodecProvider(),
              new JsonObjectCodecProvider(),
              new BsonCodecProvider(),
              new DBRefCodecProvider()));

      // Override the default codec registry
      return document.toBsonDocument(BsonDocument.class, customCodecRegistry);
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

  private static void readJavaScriptWithScope(final ObjectNode o, final BsonReader reader, final String fieldName, final List<String> columnNames) {
    final var code = reader.readJavaScriptWithScope();
    final var scope = readDocument(reader, (ObjectNode) Jsons.jsonNode(Collections.emptyMap()), columnNames);
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
