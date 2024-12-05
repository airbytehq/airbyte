/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.mongodb.cdc;

import static io.airbyte.integrations.source.mongodb.cdc.MongoDbDebeziumConstants.Configuration.SCHEMALESS_MODE_DATA_FIELD;
import static io.airbyte.integrations.source.mongodb.cdc.MongoDbDebeziumConstants.Configuration.SCHEMA_ENFORCED_CONFIGURATION_KEY;
import static java.util.Arrays.asList;
import static org.bson.BsonType.ARRAY;
import static org.bson.BsonType.DOCUMENT;
import static org.bson.codecs.configuration.CodecRegistries.fromProviders;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.node.ObjectNode;
import com.google.common.collect.ImmutableMap;
import com.google.common.collect.Lists;
import com.mongodb.DBRefCodecProvider;
import io.airbyte.cdk.db.DataTypeUtils;
import io.airbyte.commons.json.Jsons;
import io.airbyte.commons.util.MoreIterators;
import java.util.Collections;
import java.util.Map;
import java.util.Optional;
import java.util.Set;
import org.apache.commons.lang3.StringUtils;
import org.bson.BsonBinary;
import org.bson.BsonDocument;
import org.bson.BsonDocumentReader;
import org.bson.BsonReader;
import org.bson.BsonRegularExpression;
import org.bson.BsonType;
import org.bson.Document;
import org.bson.UuidRepresentation;
import org.bson.codecs.BsonCodecProvider;
import org.bson.codecs.BsonValueCodecProvider;
import org.bson.codecs.DocumentCodecProvider;
import org.bson.codecs.IterableCodecProvider;
import org.bson.codecs.JsonObjectCodecProvider;
import org.bson.codecs.MapCodecProvider;
import org.bson.codecs.UuidCodecProvider;
import org.bson.codecs.ValueCodecProvider;
import org.bson.codecs.configuration.CodecRegistry;
import org.bson.codecs.jsr310.Jsr310CodecProvider;
import org.bson.types.Decimal128;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

/**
 * Collection of utility methods that are used to transform CDC events.
 */
public class MongoDbCdcEventUtils {

  private static final Logger LOGGER = LoggerFactory.getLogger(MongoDbCdcEventUtils.class);

  public static final String AIRBYTE_SUFFIX = "_aibyte_transform";
  public static final String DOCUMENT_OBJECT_ID_FIELD = "_id";
  public static final String ID_FIELD = "id";
  public static final String OBJECT_ID_FIELD = "$oid";
  public static final String OBJECT_ID_FIELD_PATTERN = "\\" + OBJECT_ID_FIELD;

  /**
   * Generates a JSON document with only the {@link #DOCUMENT_OBJECT_ID_FIELD} property. The value is
   * extracted from the provided Debezium event key. The result is the following JSON document:
   * <p/>
   * <p/>
   * <code>
   *     { "_id" : "&lt;the object ID as a String&gt;" }
   * </code>
   *
   * @param debeziumEventKey The Debezium change event key as a JSON document.
   * @return The modified JSON document with the ID value extracted from the Debezium change event
   *         key.
   */
  public static String generateObjectIdDocument(final JsonNode debeziumEventKey) {
    final String idField = debeziumEventKey.get(ID_FIELD).asText();
    if (StringUtils.contains(idField, OBJECT_ID_FIELD)) {
      return idField.replaceAll(OBJECT_ID_FIELD_PATTERN, DOCUMENT_OBJECT_ID_FIELD);
    } else {
      return Jsons.serialize(Jsons.jsonNode(Map.of(DOCUMENT_OBJECT_ID_FIELD, idField.replaceAll("^\"|\"$", ""))));
    }
  }

  /**
   * Normalizes the document's object ID value stored in the change event to match the raw data
   * produced by the initial snapshot.
   * <p/>
   * <p/>
   * We need to unpack the object ID from the event data in order for it to match up with the data
   * produced by the initial snapshot. The event contains the object ID in a nested object:
   * <p/>
   * <p/>
   * <code>
   * {\"_id\": {\"$oid\": \"64f24244f95155351c4185b1\"}, ...}
   * </code>
   * <p/>
   * <p/>
   * In order to match the data produced by the initial snapshot, this must be translated into:
   * <p/>
   * <p/>
   * <code>
   * {\"_id\": \"64f24244f95155351c4185b1\", ...}
   * </code>
   *
   * @param data The {@link ObjectNode} that contains the record data extracted from the change event.
   * @return The updated record data with the document object ID normalized.
   */
  public static ObjectNode normalizeObjectId(final ObjectNode data) {
    if (data.has(DOCUMENT_OBJECT_ID_FIELD) && data.get(DOCUMENT_OBJECT_ID_FIELD).has(OBJECT_ID_FIELD)) {
      final String objectId = data.get(DOCUMENT_OBJECT_ID_FIELD).get(OBJECT_ID_FIELD).asText();
      data.put(DOCUMENT_OBJECT_ID_FIELD, objectId);
    }
    return data;
  }

  public static ObjectNode normalizeObjectIdNoSchema(final ObjectNode data) {
    normalizeObjectId(data);
    // normalize _id in "data" if key exists
    final Optional<JsonNode> maybeDataField = Optional.ofNullable(data.get(SCHEMALESS_MODE_DATA_FIELD));
    maybeDataField.ifPresent(d -> normalizeObjectId((ObjectNode) d));
    return data;
  }

  /**
   * Transforms the Debezium event data to ensure that all data types are consistent with those in
   * documents generated by initial snapshots.
   *
   * @param json The Debezium event data as JSON.
   * @return The transformed Debezium event data as JSON.
   */
  public static ObjectNode transformDataTypes(final String json, final Set<String> configuredFields) {
    final ObjectNode objectNode = (ObjectNode) Jsons.jsonNode(Collections.emptyMap());
    final Document document = Document.parse(json);
    formatDocument(document, objectNode, configuredFields);
    return normalizeObjectId(objectNode);
  }

  public static ObjectNode transformDataTypesNoSchema(final String json) {
    final ObjectNode objectNode = (ObjectNode) Jsons.jsonNode(Collections.emptyMap());
    final Document document = Document.parse(json);
    formatDocumentNoSchema(document, objectNode);
    return normalizeObjectIdNoSchema(objectNode);
  }

  public static JsonNode toJsonNode(final Document document, final Set<String> columnNames) {
    final ObjectNode objectNode = (ObjectNode) Jsons.jsonNode(Collections.emptyMap());
    formatDocument(document, objectNode, columnNames);
    return normalizeObjectId(objectNode);
  }

  public static JsonNode toJsonNodeNoSchema(final Document document) {
    final ObjectNode objectNode = (ObjectNode) Jsons.jsonNode(Collections.emptyMap());
    formatDocumentNoSchema(document, objectNode);
    return normalizeObjectIdNoSchema(objectNode);
  }

  private static void formatDocument(final Document document, final ObjectNode objectNode, final Set<String> columnNames) {
    final BsonDocument bsonDocument = toBsonDocument(document);
    try (final BsonReader reader = new BsonDocumentReader(bsonDocument)) {
      readDocument(reader, objectNode, columnNames, false);
    } catch (final Exception e) {
      LOGGER.error("Exception while parsing BsonDocument: {}", e.getMessage());
      throw new RuntimeException(e);
    }
  }

  private static void formatDocumentNoSchema(final Document document, final ObjectNode objectNode) {
    objectNode.set(SCHEMALESS_MODE_DATA_FIELD, Jsons.jsonNode(Collections.emptyMap()));
    final BsonDocument bsonDocument = toBsonDocument(document);
    try (final BsonReader reader = new BsonDocumentReader(bsonDocument)) {
      readDocument(reader, (ObjectNode) objectNode.get(SCHEMALESS_MODE_DATA_FIELD), Collections.emptySet(), true);
      final Optional<JsonNode> maybeId = Optional.ofNullable(objectNode.get(SCHEMALESS_MODE_DATA_FIELD).get(DOCUMENT_OBJECT_ID_FIELD));
      maybeId.ifPresent(id -> objectNode.set(DOCUMENT_OBJECT_ID_FIELD, id));
    } catch (final Exception e) {
      LOGGER.error("Exception while parsing BsonDocument: {}", e.getMessage());
      throw new RuntimeException(e);
    }
  }

  private static ObjectNode readDocument(final BsonReader reader,
                                         final ObjectNode jsonNodes,
                                         final Set<String> includedFields,
                                         final boolean allowAllFields) {
    reader.readStartDocument();
    while (reader.readBsonType() != BsonType.END_OF_DOCUMENT) {
      final var fieldName = reader.readName();
      final var fieldType = reader.getCurrentBsonType();

      if (shouldIncludeField(fieldName, includedFields, allowAllFields)) {
        if (DOCUMENT.equals(fieldType)) {
          /*
           * Recursion in used to parse inner documents. Pass the allow all column name so all nested fields
           * are processed.
           */
          jsonNodes.set(fieldName, readDocument(reader, (ObjectNode) Jsons.jsonNode(Collections.emptyMap()), Set.of(), true));
        } else if (ARRAY.equals(fieldType)) {
          jsonNodes.set(fieldName, readArray(reader, includedFields, fieldName));
        } else {
          readField(reader, jsonNodes, fieldName, fieldType);
        }
        transformToStringIfMarked(jsonNodes, includedFields, fieldName);
      } else {
        reader.skipValue();
      }
    }
    reader.readEndDocument();

    return jsonNodes;
  }

  private static JsonNode readArray(final BsonReader reader, final Set<String> columnNames, final String fieldName) {
    reader.readStartArray();
    final var elements = Lists.newArrayList();

    while (reader.readBsonType() != BsonType.END_OF_DOCUMENT) {
      final var currentBsonType = reader.getCurrentBsonType();
      if (DOCUMENT.equals(currentBsonType)) {
        // recursion is used to read inner doc
        elements.add(readDocument(reader, (ObjectNode) Jsons.jsonNode(Collections.emptyMap()), columnNames, true));
      } else if (ARRAY.equals(currentBsonType)) {
        // recursion is used to read inner array
        elements.add(readArray(reader, columnNames, fieldName));
      } else {
        final var element = readField(reader, (ObjectNode) Jsons.jsonNode(Collections.emptyMap()), fieldName, currentBsonType);
        elements.add(element.get(fieldName));
      }
    }
    reader.readEndArray();
    return Jsons.jsonNode(MoreIterators.toList(elements.iterator()));
  }

  private static ObjectNode readField(final BsonReader reader,
                                      final ObjectNode o,
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
      case JAVASCRIPT_WITH_SCOPE -> readJavaScriptWithScope(o, reader, fieldName);
      case REGULAR_EXPRESSION -> o.put(fieldName, readRegularExpression(reader.readRegularExpression()));
      case NULL -> readNull(o, reader, fieldName);
      default -> reader.skipValue();
    }

    return o;
  }

  private static BsonDocument toBsonDocument(final Document document) {
    try {
      final CodecRegistry customCodecRegistry =
          fromProviders(asList(
              new UuidCodecProvider(UuidRepresentation.STANDARD),
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

  private static void readNull(final ObjectNode o, final BsonReader reader, final String fieldName) {
    o.putNull(fieldName);
    reader.readNull();
  }

  private static void readJavaScriptWithScope(final ObjectNode o, final BsonReader reader, final String fieldName) {
    final var code = reader.readJavaScriptWithScope();
    final var scope = readDocument(reader, (ObjectNode) Jsons.jsonNode(Collections.emptyMap()), Set.of("scope"), false);
    o.set(fieldName, Jsons.jsonNode(ImmutableMap.of("code", code, "scope", scope)));
  }

  private static String readRegularExpression(final BsonRegularExpression regularExpression) {
    if (regularExpression != null) {
      final String options = regularExpression.getOptions();
      final String pattern = regularExpression.getPattern();
      return (StringUtils.isNotBlank(options)) ? "(" + options + ")" + pattern : pattern;
    } else {
      return null;
    }
  }

  public static void transformToStringIfMarked(final ObjectNode jsonNodes, final Set<String> columnNames, final String fieldName) {
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

  /**
   * Test if the current field that is included in the configured set of discovered fields. In order
   * to support the fields of nested document fields that pass the initial filter, the
   * {@code allowAll} flag may be included in the as a way to allow the fields of the nested document
   * to be processed.
   *
   * @param fieldName The name of the current field.
   * @param includedFields The discovered fields.
   * @param allowAll Flag that overrides the field inclusion comparison.
   * @return {@code true} if the current field should be included for processing or {@code false}
   *         otherwise.
   */
  private static boolean shouldIncludeField(final String fieldName, final Set<String> includedFields, final boolean allowAll) {
    return allowAll || includedFields.contains(fieldName);
  }

  /**
   * Parses source-mongodbv2 configuration json for the value of schema_enforced.
   *
   * @param config config json
   * @return true unless a schema_enforced configured to false
   */
  public static boolean isEnforceSchema(final JsonNode config) {
    return config == null || !config.has(SCHEMA_ENFORCED_CONFIGURATION_KEY)
        || (config.has(SCHEMA_ENFORCED_CONFIGURATION_KEY) && config.get(
            SCHEMA_ENFORCED_CONFIGURATION_KEY).asBoolean(true));

  }

}
