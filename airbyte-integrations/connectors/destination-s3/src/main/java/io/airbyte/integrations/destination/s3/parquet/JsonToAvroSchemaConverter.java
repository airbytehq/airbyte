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

package io.airbyte.integrations.destination.s3.parquet;

import com.fasterxml.jackson.databind.JsonNode;
import com.google.common.base.Preconditions;
import io.airbyte.commons.util.MoreIterators;
import io.airbyte.integrations.base.JavaBaseConstants;
import io.airbyte.integrations.destination.StandardNameTransformer;
import java.util.ArrayList;
import java.util.Collections;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.stream.Collectors;
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
 * standardize schema names, and keep track of a mapping from the original names to the
 * standardized ones.
 */
public class JsonToAvroSchemaConverter {

  private static final Logger LOGGER = LoggerFactory.getLogger(JsonToAvroSchemaConverter.class);
  public static final Schema UUID_SCHEMA = LogicalTypes.uuid()
      .addToSchema(Schema.create(Type.STRING));
  private static final Schema TIMESTAMP_MILLIS_SCHEMA = LogicalTypes.timestampMillis()
      .addToSchema(Schema.create(Type.LONG));
  private static final StandardNameTransformer NAME_TRANSFORMER = new StandardNameTransformer();

  private final Map<String, String> standardizedNames = new HashMap<>();

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
              S3ParquetConstants.DOC_KEY_ORIGINAL_NAME,
              S3ParquetConstants.DOC_KEY_VALUE_DELIMITER,
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
            S3ParquetConstants.DOC_KEY_ORIGINAL_NAME,
            S3ParquetConstants.DOC_KEY_VALUE_DELIMITER,
            fieldName));
      }
      assembler = fieldBuilder.type(getNullableFieldTypes(fieldName, fieldDefinition)).withDefault(null);
    }

    return assembler.endRecord();
  }

  Schema getSingleFieldType(String fieldName, JsonSchemaType fieldType, JsonNode fieldDefinition) {
    Schema fieldSchema;
    switch (fieldType) {
      case NULL -> throw new IllegalStateException("Null types should have been filtered out");
      case STRING, NUMBER, INTEGER, BOOLEAN -> fieldSchema = Schema.create(fieldType.getAvroType());
      case ARRAY -> {
        JsonNode items = fieldDefinition.get("items");
        Preconditions.checkNotNull(items, "Array field %s misses the items property.", fieldName);
        fieldSchema = Schema
            .createArray(getNullableFieldTypes(String.format("%s.items", fieldName), items));
      }
      case OBJECT -> fieldSchema = getAvroSchema(fieldDefinition, fieldName, null, false);
      default -> throw new IllegalStateException(
          String.format("Unexpected type for field %s: %s", fieldName, fieldType));
    }
    return fieldSchema;
  }

  /**
   * @param fieldDefinition - Json schema field definition. E.g. { type: "number" }.
   */
  Schema getNullableFieldTypes(String fieldName, JsonNode fieldDefinition) {
    List<Schema> nonNullFieldTypes =  getTypes(fieldName, fieldDefinition.get("type")).stream()
        // Filter out null types, which will be added back in the end.
        .filter(fieldType -> fieldType != JsonSchemaType.NULL)
        .map(fieldType -> getSingleFieldType(fieldName, fieldType, fieldDefinition))
        .collect(Collectors.toList());

    if (nonNullFieldTypes.isEmpty()) {
      return Schema.create(Schema.Type.NULL);
    } else {
      // Mark every field as nullable to prevent missing value exceptions from Parquet.
      nonNullFieldTypes.add(0, Schema.create(Schema.Type.NULL));
      return Schema.createUnion(nonNullFieldTypes);
    }
  }

  static List<JsonSchemaType> getTypes(String fieldName, JsonNode type) {
    if (type == null) {
      throw new IllegalStateException(String.format("Field %s has no type", fieldName));
    } else if (type.isArray()) {
      return MoreIterators.toList(type.elements()).stream()
          .map(s -> JsonSchemaType.fromJsonSchemaType(s.asText()))
          .collect(Collectors.toList());
    } else if (type.isTextual()) {
      return Collections.singletonList(JsonSchemaType.fromJsonSchemaType(type.asText()));
    } else {
      throw new IllegalStateException("Unexpected type: " + type);
    }
  }

}
