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

package io.airbyte.integrations.destination.s3.avro;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.node.ArrayNode;
import com.google.common.base.Preconditions;
import io.airbyte.commons.util.MoreIterators;
import io.airbyte.integrations.base.JavaBaseConstants;
import io.airbyte.integrations.destination.s3.S3NameTransformer;
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
import org.apache.avro.Schema.Type;
import org.apache.avro.SchemaBuilder;
import org.apache.avro.SchemaBuilder.RecordBuilder;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

/**
 * The main function of this class is to convert a JsonSchema to Avro schema. It can also
 * standardize schema names, and keep track of a mapping from the original names to the standardized
 * ones.
 * <p/>
 * For limitations of this converter, see the README of this connector:
 * https://docs.airbyte.io/integrations/destinations/s3#avro
 */
public class JsonToAvroSchemaConverter {

  public static final Schema UUID_SCHEMA = LogicalTypes.uuid()
      .addToSchema(Schema.create(Type.STRING));
  private static final Logger LOGGER = LoggerFactory.getLogger(JsonToAvroSchemaConverter.class);
  private static final Schema TIMESTAMP_MILLIS_SCHEMA = LogicalTypes.timestampMillis()
      .addToSchema(Schema.create(Type.LONG));
  private static final S3NameTransformer NAME_TRANSFORMER = new S3NameTransformer();

  private final Map<String, String> standardizedNames = new HashMap<>();

  static List<JsonSchemaType> getNonNullTypes(String fieldName, JsonNode fieldDefinition) {
    return getTypes(fieldName, fieldDefinition).stream()
        .filter(type -> type != JsonSchemaType.NULL).collect(Collectors.toList());
  }

  static List<JsonSchemaType> getTypes(String fieldName, JsonNode fieldDefinition) {
    Optional<JsonNode> combinedRestriction = getCombinedRestriction(fieldDefinition);
    if (combinedRestriction.isPresent()) {
      return Collections.singletonList(JsonSchemaType.COMBINED);
    }

    JsonNode typeProperty = fieldDefinition.get("type");
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

  static Optional<JsonNode> getCombinedRestriction(JsonNode fieldDefinition) {
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
  public Schema getAvroSchema(JsonNode jsonSchema,
                              String name,
                              @Nullable String namespace,
                              boolean appendAirbyteFields) {
    String stdName = NAME_TRANSFORMER.getIdentifier(name);
    RecordBuilder<Schema> builder = SchemaBuilder.record(stdName);
    if (!stdName.equals(name)) {
      standardizedNames.put(name, stdName);
      LOGGER.warn("Schema name contains illegal character(s) and is standardized: {} -> {}", name,
          stdName);
      builder = builder.doc(
          String.format("%s%s%s",
              S3AvroConstants.DOC_KEY_ORIGINAL_NAME,
              S3AvroConstants.DOC_KEY_VALUE_DELIMITER,
              name));
    }
    if (namespace != null) {
      builder = builder.namespace(namespace);
    }

    JsonNode properties = jsonSchema.get("properties");
    List<String> fieldNames = new ArrayList<>(MoreIterators.toList(properties.fieldNames()));

    SchemaBuilder.FieldAssembler<Schema> assembler = builder.fields();

    if (appendAirbyteFields) {
      assembler = assembler.name(JavaBaseConstants.COLUMN_NAME_AB_ID).type(UUID_SCHEMA).noDefault();
      assembler = assembler.name(JavaBaseConstants.COLUMN_NAME_EMITTED_AT)
          .type(TIMESTAMP_MILLIS_SCHEMA).noDefault();
    }

    for (String fieldName : fieldNames) {
      String stdFieldName = NAME_TRANSFORMER.getIdentifier(fieldName);
      JsonNode fieldDefinition = properties.get(fieldName);
      SchemaBuilder.FieldBuilder<Schema> fieldBuilder = assembler.name(stdFieldName);
      if (!stdFieldName.equals(fieldName)) {
        standardizedNames.put(fieldName, stdFieldName);
        LOGGER.warn("Field name contains illegal character(s) and is standardized: {} -> {}",
            fieldName, stdFieldName);
        fieldBuilder = fieldBuilder.doc(String.format("%s%s%s",
            S3AvroConstants.DOC_KEY_ORIGINAL_NAME,
            S3AvroConstants.DOC_KEY_VALUE_DELIMITER,
            fieldName));
      }
      assembler = fieldBuilder.type(getNullableFieldTypes(fieldName, fieldDefinition))
          .withDefault(null);
    }

    return assembler.endRecord();
  }

  Schema getSingleFieldType(String fieldName, JsonSchemaType fieldType, JsonNode fieldDefinition) {
    Preconditions
        .checkState(fieldType != JsonSchemaType.NULL, "Null types should have been filtered out");

    Schema fieldSchema;
    switch (fieldType) {
      case STRING, NUMBER, INTEGER, BOOLEAN -> fieldSchema = Schema.create(fieldType.getAvroType());
      case COMBINED -> {
        Optional<JsonNode> combinedRestriction = getCombinedRestriction(fieldDefinition);
        List<Schema> unionTypes = getSchemasFromTypes(fieldName, (ArrayNode) combinedRestriction.get());
        fieldSchema = Schema.createUnion(unionTypes);
      }
      case ARRAY -> {
        JsonNode items = fieldDefinition.get("items");
        Preconditions.checkNotNull(items, "Array field %s misses the items property.", fieldName);

        if (items.isObject()) {
          fieldSchema = Schema.createArray(getNullableFieldTypes(String.format("%s.items", fieldName), items));
        } else if (items.isArray()) {
          List<Schema> arrayElementTypes = getSchemasFromTypes(fieldName, (ArrayNode) items);
          arrayElementTypes.add(0, Schema.create(Type.NULL));
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

  List<Schema> getSchemasFromTypes(String fieldName, ArrayNode types) {
    return MoreIterators.toList(types.elements())
        .stream()
        .flatMap(definition -> getNonNullTypes(fieldName, definition).stream().flatMap(type -> {
          Schema singleFieldSchema = getSingleFieldType(fieldName, type, definition);
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
  Schema getNullableFieldTypes(String fieldName, JsonNode fieldDefinition) {
    // Filter out null types, which will be added back in the end.
    List<Schema> nonNullFieldTypes = getNonNullTypes(fieldName, fieldDefinition)
        .stream()
        .flatMap(fieldType -> {
          Schema singleFieldSchema = getSingleFieldType(fieldName, fieldType, fieldDefinition);
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
      nonNullFieldTypes.add(0, Schema.create(Schema.Type.NULL));
      return Schema.createUnion(nonNullFieldTypes);
    }
  }

}
