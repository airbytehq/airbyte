/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.bigquery.formatter;

import static io.airbyte.integrations.destination.bigquery.formatter.util.FormatterUtil.TYPE_FIELD;

import com.fasterxml.jackson.core.type.TypeReference;
import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.fasterxml.jackson.databind.ObjectReader;
import com.fasterxml.jackson.databind.node.ObjectNode;
import com.fasterxml.jackson.databind.node.TextNode;
import com.google.cloud.bigquery.Field;
import com.google.cloud.bigquery.Field.Builder;
import com.google.cloud.bigquery.Field.Mode;
import com.google.cloud.bigquery.FieldList;
import com.google.cloud.bigquery.LegacySQLTypeName;
import com.google.cloud.bigquery.QueryParameterValue;
import com.google.cloud.bigquery.Schema;
import com.google.cloud.bigquery.StandardSQLTypeName;
import com.google.common.base.Preconditions;
import com.google.common.collect.ImmutableMap;
import io.airbyte.commons.json.Jsons;
import io.airbyte.commons.util.MoreIterators;
import io.airbyte.integrations.base.JavaBaseConstants;
import io.airbyte.integrations.destination.StandardNameTransformer;
import io.airbyte.integrations.destination.bigquery.BigQueryUtils;
import io.airbyte.integrations.destination.bigquery.JsonSchemaFormat;
import io.airbyte.integrations.destination.bigquery.JsonSchemaType;
import io.airbyte.integrations.destination.bigquery.formatter.arrayformater.ArrayFormatter;
import io.airbyte.integrations.destination.bigquery.formatter.arrayformater.DefaultArrayFormatter;
import io.airbyte.protocol.models.v0.AirbyteRecordMessage;
import java.io.IOException;
import java.util.Collections;
import java.util.Comparator;
import java.util.List;
import java.util.UUID;
import java.util.concurrent.TimeUnit;
import java.util.function.Consumer;
import java.util.stream.Collectors;
import org.apache.commons.lang3.StringUtils;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class DefaultBigQueryDenormalizedRecordFormatter extends DefaultBigQueryRecordFormatter {

  private static final Logger LOGGER = LoggerFactory.getLogger(DefaultBigQueryDenormalizedRecordFormatter.class);

  public static final String PROPERTIES_FIELD = "properties";
  private static final String ALL_OF_FIELD = "allOf";
  private static final String ANY_OF_FIELD = "anyOf";
  private static final String FORMAT_FIELD = "format";
  private static final String AIRBYTE_TYPE = "airbyte_type";
  private static final String REF_DEFINITION_KEY = "$ref";
  private static final ObjectMapper mapper = new ObjectMapper();

  protected ArrayFormatter arrayFormatter;

  public DefaultBigQueryDenormalizedRecordFormatter(final JsonNode jsonSchema, final StandardNameTransformer namingResolver) {
    super(jsonSchema, namingResolver);
  }

  private ArrayFormatter getArrayFormatter() {
    if (arrayFormatter == null) {
      arrayFormatter = new DefaultArrayFormatter();
    }
    return arrayFormatter;
  }

  public void setArrayFormatter(final ArrayFormatter arrayFormatter) {
    this.arrayFormatter = arrayFormatter;
    this.jsonSchema = formatJsonSchema(this.originalJsonSchema.deepCopy());
    this.bigQuerySchema = getBigQuerySchema(jsonSchema);
  }

  @Override
  protected JsonNode formatJsonSchema(final JsonNode jsonSchema) {
    final var modifiedJsonSchema = jsonSchema.deepCopy(); // Issue #5912 is reopened (PR #11166) formatAllOfAndAnyOfFields(namingResolver,
                                                          // jsonSchema);
    getArrayFormatter().populateEmptyArrays(modifiedJsonSchema);
    getArrayFormatter().surroundArraysByObjects(modifiedJsonSchema);
    return modifiedJsonSchema;
  }

  @Override
  public JsonNode formatRecord(final AirbyteRecordMessage recordMessage) {
    // Bigquery represents TIMESTAMP to the microsecond precision, so we convert to microseconds then
    // use BQ helpers to string-format correctly.
    Preconditions.checkArgument(recordMessage.getData().isObject());
    final ObjectNode data = (ObjectNode) formatData(getBigQuerySchema().getFields(), recordMessage.getData());
    // replace ObjectNode with TextNode for fields with $ref definition key
    // Do not need to iterate through all JSON Object nodes, only first nesting object.
    if (!fieldsContainRefDefinitionValue.isEmpty()) {
      fieldsContainRefDefinitionValue.forEach(key -> {
        if (data.get(key) != null && !data.get(key).isNull()) {
          data.put(key, data.get(key).toString());
        }
      });
    }
    addAirbyteColumns(data, recordMessage);

    return data;
  }

  protected void addAirbyteColumns(final ObjectNode data, final AirbyteRecordMessage recordMessage) {
    // currently emittedAt time is in millis format from airbyte message
    final long emittedAtMicroseconds = TimeUnit.MICROSECONDS.convert(
        recordMessage.getEmittedAt(), TimeUnit.MILLISECONDS);
    final String formattedEmittedAt = QueryParameterValue.timestamp(emittedAtMicroseconds).getValue();

    data.put(JavaBaseConstants.COLUMN_NAME_AB_ID, UUID.randomUUID().toString());
    data.put(JavaBaseConstants.COLUMN_NAME_EMITTED_AT, formattedEmittedAt);
  }

  private JsonNode formatData(final FieldList fields, final JsonNode root) {
    // handles empty objects and arrays
    if (fields == null) {
      return root;
    }
    final JsonNode formattedData;
    if (root.isObject()) {
      formattedData = getObjectNode(fields, root);
    } else if (root.isArray()) {
      formattedData = getArrayNode(fields, root);
    } else {
      formattedData = root;
    }
    formatDateTimeFields(fields, formattedData);

    return formattedData;
  }

  protected void formatDateTimeFields(final FieldList fields, final JsonNode root) {
    final List<String> dateTimeFields = BigQueryUtils.getDateTimeFieldsFromSchema(fields);
    if (!dateTimeFields.isEmpty() && !root.isNull()) {
      if (root.isArray()) {
        root.forEach(jsonNode -> BigQueryUtils.transformJsonDateTimeToBigDataFormat(dateTimeFields, jsonNode));
      } else {
        BigQueryUtils.transformJsonDateTimeToBigDataFormat(dateTimeFields, root);
      }
    }
  }

  private JsonNode getArrayNode(final FieldList fields, final JsonNode root) {
    // Arrays can have only one field
    final Field arrayField = fields.get(0);
    // If an array of records, we should use subfields
    final FieldList subFields;
    if (arrayField.getSubFields() == null || arrayField.getSubFields().isEmpty()) {
      subFields = fields;
    } else {
      subFields = arrayField.getSubFields();
    }
    final List<JsonNode> arrayItems = MoreIterators.toList(root.elements()).stream()
        .map(p -> formatData(subFields, p))
        .toList();

    return getArrayFormatter().formatArrayItems(arrayItems);
  }

  private JsonNode getObjectNode(final FieldList fields, final JsonNode root) {
    final List<String> fieldNames = fields.stream().map(Field::getName).collect(Collectors.toList());

    fields.stream()
        .filter(f -> f.getType().equals(LegacySQLTypeName.STRING))
        .filter(field -> root.get(field.getName()) != null)
        .filter(f -> root.get(f.getName()).isObject())
        .forEach(f -> {
          final String value = root.get(f.getName()).toString();
          ((ObjectNode) root).remove(f.getName());
          ((ObjectNode) root).put(f.getName(), new TextNode(value));
        });

    return Jsons.jsonNode(Jsons.keys(root).stream()
        .filter(key -> {
          final boolean validKey = fieldNames.contains(namingResolver.getIdentifier(key));
          if (!validKey && !invalidKeys.contains(key)) {
            logFieldFail("Ignoring field as it is not defined in catalog", key);
            invalidKeys.add(key);
          }
          return validKey;
        })
        .collect(Collectors.toMap(namingResolver::getIdentifier,
            key -> formatData(fields.get(namingResolver.getIdentifier(key)).getSubFields(), root.get(key)))));
  }

  @Override
  public Schema getBigQuerySchema(final JsonNode jsonSchema) {
    final List<Field> fieldList = getSchemaFields(namingResolver, jsonSchema);
    if (fieldList.stream().noneMatch(f -> f.getName().equals(JavaBaseConstants.COLUMN_NAME_AB_ID))) {
      fieldList.add(Field.of(JavaBaseConstants.COLUMN_NAME_AB_ID, StandardSQLTypeName.STRING));
    }
    if (fieldList.stream().noneMatch(f -> f.getName().equals(JavaBaseConstants.COLUMN_NAME_EMITTED_AT))) {
      fieldList.add(Field.of(JavaBaseConstants.COLUMN_NAME_EMITTED_AT, StandardSQLTypeName.TIMESTAMP));
    }
    LOGGER.info("Airbyte Schema is transformed from {} to {}.", jsonSchema, fieldList);
    return Schema.of(fieldList);
  }

  private List<Field> getSchemaFields(final StandardNameTransformer namingResolver, final JsonNode jsonSchema) {
    LOGGER.info("getSchemaFields : " + jsonSchema + " namingResolver " + namingResolver);
    Preconditions.checkArgument(jsonSchema.isObject() && jsonSchema.has(PROPERTIES_FIELD));
    final ObjectNode properties = (ObjectNode) jsonSchema.get(PROPERTIES_FIELD);
    final List<Field> tmpFields = Jsons.keys(properties).stream()
        .peek(addToRefList(properties))
        .map(key -> getField(namingResolver, key, properties.get(key))
            .build())
        .collect(Collectors.toList());
    if (!fieldsContainRefDefinitionValue.isEmpty()) {
      LOGGER.warn("Next fields contain \"$ref\" as Definition: {}. They are going to be saved as String Type column",
          fieldsContainRefDefinitionValue);
    }
    return tmpFields;
  }

  /**
   * @param properties - JSON schema with properties
   *        <p>
   *        The method is responsible for population of fieldsContainRefDefinitionValue set with keys
   *        contain $ref definition
   *        <p>
   *        Currently, AirByte doesn't support parsing value by $ref key definition. The issue to
   *        track this <a href="https://github.com/airbytehq/airbyte/issues/7725">7725</a>
   */
  private Consumer<String> addToRefList(final ObjectNode properties) {
    return key -> {
      if (properties.get(key).has(REF_DEFINITION_KEY)) {
        fieldsContainRefDefinitionValue.add(key);
      }
    };
  }

  private static JsonNode getFileDefinition(final JsonNode fieldDefinition) {
    if (fieldDefinition.has(TYPE_FIELD)) {
      return fieldDefinition;
    } else {
      if (fieldDefinition.has(ANY_OF_FIELD) && fieldDefinition.get(ANY_OF_FIELD).isArray()) {
        return allOfAndAnyOfFieldProcessing(ANY_OF_FIELD, fieldDefinition);
      }
      if (fieldDefinition.has(ALL_OF_FIELD) && fieldDefinition.get(ALL_OF_FIELD).isArray()) {
        return allOfAndAnyOfFieldProcessing(ALL_OF_FIELD, fieldDefinition);
      }
    }
    return fieldDefinition;
  }

  private static JsonNode allOfAndAnyOfFieldProcessing(final String fieldName, final JsonNode fieldDefinition) {
    final ObjectReader reader = mapper.readerFor(new TypeReference<List<JsonNode>>() {});
    final List<JsonNode> list;
    try {
      list = reader.readValue(fieldDefinition.get(fieldName));
    } catch (final IOException e) {
      throw new IllegalStateException(
          String.format("Failed to read and process the following field - %s", fieldDefinition));
    }
    final ObjectNode objectNode = mapper.createObjectNode();
    list.forEach(field -> {
      objectNode.set("big_query_" + field.get("type").asText(), field);
    });

    return Jsons.jsonNode(ImmutableMap.builder()
        .put("type", "object")
        .put(PROPERTIES_FIELD, objectNode)
        .put("additionalProperties", false)
        .build());
  }

  private static Builder getField(final StandardNameTransformer namingResolver, final String key, final JsonNode fieldDefinition) {
    final String fieldName = namingResolver.getIdentifier(key);
    final Builder builder = Field.newBuilder(fieldName, StandardSQLTypeName.STRING);
    final JsonNode updatedFileDefinition = getFileDefinition(fieldDefinition);
    final JsonNode type = updatedFileDefinition.get(TYPE_FIELD);
    final JsonNode airbyteType = updatedFileDefinition.get(AIRBYTE_TYPE);
    final List<JsonSchemaType> fieldTypes = getTypes(fieldName, type);
    for (int i = 0; i < fieldTypes.size(); i++) {
      final JsonSchemaType fieldType = fieldTypes.get(i);
      if (fieldType == JsonSchemaType.NULL) {
        builder.setMode(Mode.NULLABLE);
      }
      if (i == 0) {
        // Treat the first type in the list with the widest scope as the primary type
        final JsonSchemaType primaryType = fieldTypes.get(i);
        switch (primaryType) {
          case NULL -> {
            builder.setType(StandardSQLTypeName.STRING);
          }
          case STRING, INTEGER, BOOLEAN -> {
            builder.setType(primaryType.getBigQueryType());
          }
          case NUMBER -> {
            if (airbyteType != null
                && StringUtils.equalsAnyIgnoreCase(airbyteType.asText(),
                    "big_integer", "integer")) {
              builder.setType(StandardSQLTypeName.INT64);
            } else {
              builder.setType(primaryType.getBigQueryType());
            }
          }
          case ARRAY -> {
            final JsonNode items;
            if (updatedFileDefinition.has("items")) {
              items = updatedFileDefinition.get("items");
            } else {
              LOGGER.warn("Source connector provided schema for ARRAY with missed \"items\", will assume that it's a String type");
              // this is handler for case when we get "array" without "items"
              // (https://github.com/airbytehq/airbyte/issues/5486)
              items = getTypeStringSchema();
            }
            return getField(namingResolver, fieldName, items).setMode(Mode.REPEATED);
          }
          case OBJECT -> {
            final JsonNode properties;
            if (updatedFileDefinition.has(PROPERTIES_FIELD)) {
              properties = updatedFileDefinition.get(PROPERTIES_FIELD);
            } else {
              properties = updatedFileDefinition;
            }
            final FieldList fieldList = FieldList.of(Jsons.keys(properties)
                .stream()
                .map(f -> getField(namingResolver, f, properties.get(f)).build())
                .collect(Collectors.toList()));
            if (!fieldList.isEmpty()) {
              builder.setType(StandardSQLTypeName.STRUCT, fieldList);
            } else {
              builder.setType(StandardSQLTypeName.STRING);
            }
          }
          default -> {
            throw new IllegalStateException(
                String.format("Unexpected type for field %s: %s", fieldName, primaryType));
          }
        }
      }
    }

    // If a specific format is defined, use their specific type instead of the JSON's one
    final JsonNode fieldFormat = updatedFileDefinition.get(FORMAT_FIELD);
    if (fieldFormat != null) {
      final JsonSchemaFormat schemaFormat = JsonSchemaFormat.fromJsonSchemaFormat(fieldFormat.asText(),
          (airbyteType != null ? airbyteType.asText() : null));
      if (schemaFormat != null) {
        builder.setType(schemaFormat.getBigQueryType());
      }
    }

    return builder;
  }

  private static JsonNode getTypeStringSchema() {
    return Jsons.deserialize("{\n"
        + "    \"type\": [\n"
        + "      \"string\"\n"
        + "    ]\n"
        + "  }");
  }

  private static List<JsonSchemaType> getTypes(final String fieldName, final JsonNode type) {
    if (type == null) {
      LOGGER.warn("Field {} has no type defined, defaulting to STRING", fieldName);
      return List.of(JsonSchemaType.STRING);
    } else if (type.isArray()) {
      return MoreIterators.toList(type.elements()).stream()
          .map(s -> JsonSchemaType.fromJsonSchemaType(s.asText()))
          // re-order depending to make sure wider scope types are first
          .sorted(Comparator.comparingInt(JsonSchemaType::getOrder))
          .collect(Collectors.toList());
    } else if (type.isTextual()) {
      return Collections.singletonList(JsonSchemaType.fromJsonSchemaType(type.asText()));
    } else {
      throw new IllegalStateException("Unexpected type: " + type);
    }
  }

}
