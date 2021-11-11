/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.s3.avro;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.node.ArrayNode;
import com.google.common.base.Preconditions;
import io.airbyte.commons.util.MoreIterators;
import io.airbyte.integrations.base.JavaBaseConstants;
import java.util.ArrayList;
import java.util.Collections;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.Optional;
import java.util.stream.Collectors;
import java.util.stream.Stream;
import javax.annotation.Nullable;
import org.apache.avro.LogicalTypes;
import org.apache.avro.Schema;
import org.apache.avro.SchemaBuilder;
import org.apache.avro.SchemaBuilder.RecordBuilder;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import tech.allegro.schema.json2avro.converter.AdditionalPropertyField;

/**
 * The main function of this class is to convert a JsonSchema to Avro schema. It can also
 * standardize schema names, and keep track of a mapping from the original names to the standardized
 * ones, which is needed for unit tests.
 * <p>
 * </p>
 * For limitations of this converter, see the README of this connector:
 * https://docs.airbyte.io/integrations/destinations/s3#avro
 */
public class JsonToAvroSchemaConverter {

  private static final Schema UUID_SCHEMA = LogicalTypes.uuid()
      .addToSchema(Schema.create(Schema.Type.STRING));
  private static final Schema NULL_SCHEMA = Schema.create(Schema.Type.NULL);
  private static final Logger LOGGER = LoggerFactory.getLogger(JsonToAvroSchemaConverter.class);
  private static final Schema TIMESTAMP_MILLIS_SCHEMA = LogicalTypes.timestampMillis()
      .addToSchema(Schema.create(Schema.Type.LONG));

  private final Map<String, String> standardizedNames = new HashMap<>();

  static List<JsonSchemaType> getNonNullTypes(final String fieldName, final JsonNode fieldDefinition) {
    return getTypes(fieldName, fieldDefinition).stream()
        .filter(type -> type != JsonSchemaType.NULL).collect(Collectors.toList());
  }

  static List<JsonSchemaType> getTypes(final String fieldName, final JsonNode fieldDefinition) {
    final Optional<JsonNode> combinedRestriction = getCombinedRestriction(fieldDefinition);
    if (combinedRestriction.isPresent()) {
      return Collections.singletonList(JsonSchemaType.COMBINED);
    }

    final JsonNode typeProperty = fieldDefinition.get("type");
    if (typeProperty == null || typeProperty.isNull()) {
      throw new IllegalStateException(String.format("Field %s has no type", fieldName));
    }

    if (typeProperty.isArray()) {
      return MoreIterators.toList(typeProperty.elements()).stream()
          .map(s -> JsonSchemaType.fromJsonSchemaType(s.asText()))
          .collect(Collectors.toList());
    }

    if (typeProperty.isTextual()) {
      return Collections.singletonList(JsonSchemaType.fromJsonSchemaType(typeProperty.asText()));
    }

    throw new IllegalStateException("Unexpected type: " + typeProperty);
  }

  static Optional<JsonNode> getCombinedRestriction(final JsonNode fieldDefinition) {
    if (fieldDefinition.has("anyOf")) {
      return Optional.of(fieldDefinition.get("anyOf"));
    }
    if (fieldDefinition.has("allOf")) {
      return Optional.of(fieldDefinition.get("allOf"));
    }
    if (fieldDefinition.has("oneOf")) {
      return Optional.of(fieldDefinition.get("oneOf"));
    }
    return Optional.empty();
  }

  public Map<String, String> getStandardizedNames() {
    return standardizedNames;
  }

  /**
   * @return - Avro schema based on the input {@code jsonSchema}.
   */
  public Schema getAvroSchema(final JsonNode jsonSchema,
                              final String name,
                              @Nullable final String namespace,
                              final boolean appendAirbyteFields) {
    final String stdName = AvroConstants.NAME_TRANSFORMER.getIdentifier(name);
    RecordBuilder<Schema> builder = SchemaBuilder.record(stdName);
    if (!stdName.equals(name)) {
      standardizedNames.put(name, stdName);
      LOGGER.warn("Schema name contains illegal character(s) and is standardized: {} -> {}", name,
          stdName);
      builder = builder.doc(
          String.format("%s%s%s",
              AvroConstants.DOC_KEY_ORIGINAL_NAME,
              AvroConstants.DOC_KEY_VALUE_DELIMITER,
              name));
    }
    if (namespace != null) {
      builder = builder.namespace(namespace);
    }

    final JsonNode properties = jsonSchema.get("properties");
    // object field with no "properties" will be handled by the default additional properties
    // field during object conversion; so it is fine if there is no "properties"
    final List<String> fieldNames = properties == null
        ? Collections.emptyList()
        : new ArrayList<>(MoreIterators.toList(properties.fieldNames()));

    SchemaBuilder.FieldAssembler<Schema> assembler = builder.fields();

    if (appendAirbyteFields) {
      assembler = assembler.name(JavaBaseConstants.COLUMN_NAME_AB_ID).type(UUID_SCHEMA).noDefault();
      assembler = assembler.name(JavaBaseConstants.COLUMN_NAME_EMITTED_AT)
          .type(TIMESTAMP_MILLIS_SCHEMA).noDefault();
    }

    for (final String fieldName : fieldNames) {
      // ignore additional properties fields, which will be consolidated
      // into one field at the end
      if (AvroConstants.JSON_EXTRA_PROPS_FIELDS.contains(fieldName)) {
        continue;
      }

      final String stdFieldName = AvroConstants.NAME_TRANSFORMER.getIdentifier(fieldName);
      final JsonNode fieldDefinition = properties.get(fieldName);
      SchemaBuilder.FieldBuilder<Schema> fieldBuilder = assembler.name(stdFieldName);
      if (!stdFieldName.equals(fieldName)) {
        standardizedNames.put(fieldName, stdFieldName);
        LOGGER.warn("Field name contains illegal character(s) and is standardized: {} -> {}",
            fieldName, stdFieldName);
        fieldBuilder = fieldBuilder.doc(String.format("%s%s%s",
            AvroConstants.DOC_KEY_ORIGINAL_NAME,
            AvroConstants.DOC_KEY_VALUE_DELIMITER,
            fieldName));
      }
      assembler = fieldBuilder.type(getNullableFieldTypes(fieldName, fieldDefinition))
          .withDefault(null);
    }

    // support additional properties in one field
    assembler = assembler.name(AvroConstants.AVRO_EXTRA_PROPS_FIELD)
        .type(AdditionalPropertyField.FIELD_SCHEMA).withDefault(null);

    return assembler.endRecord();
  }

  Schema getSingleFieldType(final String fieldName, final JsonSchemaType fieldType, final JsonNode fieldDefinition) {
    Preconditions
        .checkState(fieldType != JsonSchemaType.NULL, "Null types should have been filtered out");

    // the additional properties fields are filtered out and never passed into this method;
    // but this method is able to handle them for completeness
    if (AvroConstants.JSON_EXTRA_PROPS_FIELDS.contains(fieldName)) {
      return AdditionalPropertyField.FIELD_SCHEMA;
    }

    final Schema fieldSchema;
    switch (fieldType) {
      case STRING, NUMBER, INTEGER, BOOLEAN -> fieldSchema = Schema.create(fieldType.getAvroType());
      case COMBINED -> {
        final Optional<JsonNode> combinedRestriction = getCombinedRestriction(fieldDefinition);
        final List<Schema> unionTypes = getSchemasFromTypes(fieldName, (ArrayNode) combinedRestriction.get());
        fieldSchema = Schema.createUnion(unionTypes);
      }
      case ARRAY -> {
        final JsonNode items = fieldDefinition.get("items");
        Preconditions.checkNotNull(items, "Array field %s misses the items property.", fieldName);

        if (items.isObject()) {
          fieldSchema = Schema.createArray(getNullableFieldTypes(String.format("%s.items", fieldName), items));
        } else if (items.isArray()) {
          final List<Schema> arrayElementTypes = getSchemasFromTypes(fieldName, (ArrayNode) items);
          arrayElementTypes.add(0, NULL_SCHEMA);
          fieldSchema = Schema.createArray(Schema.createUnion(arrayElementTypes));
        } else {
          throw new IllegalStateException(
              String.format("Array field %s has invalid items property: %s", fieldName, items));
        }
      }
      case OBJECT -> fieldSchema = getAvroSchema(fieldDefinition, fieldName, null, false);
      default -> throw new IllegalStateException(
          String.format("Unexpected type for field %s: %s", fieldName, fieldType));
    }
    return fieldSchema;
  }

  List<Schema> getSchemasFromTypes(final String fieldName, final ArrayNode types) {
    return MoreIterators.toList(types.elements())
        .stream()
        .flatMap(definition -> getNonNullTypes(fieldName, definition).stream().flatMap(type -> {
          final Schema singleFieldSchema = getSingleFieldType(fieldName, type, definition);
          if (singleFieldSchema.isUnion()) {
            return singleFieldSchema.getTypes().stream();
          } else {
            return Stream.of(singleFieldSchema);
          }
        }))
        .distinct()
        .collect(Collectors.toList());
  }

  /**
   * @param fieldDefinition - Json schema field definition. E.g. { type: "number" }.
   */
  Schema getNullableFieldTypes(final String fieldName, final JsonNode fieldDefinition) {
    // Filter out null types, which will be added back in the end.
    final List<Schema> nonNullFieldTypes = getNonNullTypes(fieldName, fieldDefinition)
        .stream()
        .flatMap(fieldType -> {
          final Schema singleFieldSchema = getSingleFieldType(fieldName, fieldType, fieldDefinition);
          if (singleFieldSchema.isUnion()) {
            return singleFieldSchema.getTypes().stream();
          } else {
            return Stream.of(singleFieldSchema);
          }
        })
        .distinct()
        .collect(Collectors.toList());

    if (nonNullFieldTypes.isEmpty()) {
      return Schema.create(Schema.Type.NULL);
    } else {
      // Mark every field as nullable to prevent missing value exceptions from Avro / Parquet.
      if (!nonNullFieldTypes.contains(NULL_SCHEMA)) {
        nonNullFieldTypes.add(0, NULL_SCHEMA);
      }
      return Schema.createUnion(nonNullFieldTypes);
    }
  }

}
