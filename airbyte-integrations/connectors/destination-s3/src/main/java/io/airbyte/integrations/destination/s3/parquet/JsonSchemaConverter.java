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

public class JsonSchemaConverter {

  public static final Schema UUID_SCHEMA = LogicalTypes.uuid()
      .addToSchema(Schema.create(Type.STRING));
  private static final Logger LOGGER = LoggerFactory.getLogger(JsonSchemaConverter.class);
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
  public Schema getAvroSchema(JsonNode jsonSchema, String name, @Nullable String namespace,
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
              name
          )
      );
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
            fieldName
        ));
      }
      assembler = fieldBuilder.type(getFieldSchema(fieldName, fieldDefinition)).withDefault(null);
    }

    return assembler.endRecord();
  }

  /**
   * @param fieldDefinition - Json schema field definition. E.g. { type: "number" }.
   */
  Schema getFieldSchema(String fieldName, JsonNode fieldDefinition) {
    List<JsonSchemaType> fieldTypes = getTypes(fieldName, fieldDefinition.get("type"));
    // Currently we assume there are at most two type specifications for each field.
    // So the primary type is the last element in the "type" property.
    JsonSchemaType primaryType = fieldTypes.get(fieldTypes.size() - 1);
    Schema fieldSchema;
    switch (primaryType) {
      case STRING, NUMBER, INTEGER, BOOLEAN, NULL -> {
        fieldSchema = Schema.create(primaryType.getAvroType());
      }
      case ARRAY -> {
        JsonNode items = fieldDefinition.get("items");
        Preconditions.checkNotNull(items, "Array field %s misses the items property.", fieldName);
        fieldSchema = Schema
            .createArray(getFieldSchema(String.format("%s.items", fieldName), items));
      }
      case OBJECT -> {
        fieldSchema = getAvroSchema(fieldDefinition, fieldName, null, false);
      }
      default -> {
        throw new IllegalStateException(
            String.format("Unexpected type for field %s: %s", fieldName, primaryType));
      }
    }
    // Mark every field as nullable to prevent missing value exceptions from Parquet.
    return Schema.createUnion(Schema.create(Schema.Type.NULL), fieldSchema);
  }

  /**
   * Currently this method assumes that there are at most two type specification.
   * E.g. ["null", "number"]. Fields like "allOf", "anyOf", "oneOf" are not supported.
   */
  static List<JsonSchemaType> getTypes(String fieldName, JsonNode type) {
    if (type == null) {
      throw new IllegalStateException(String.format("Field %s has no type", fieldName));
    } else if (type.isArray()) {
      List<JsonSchemaType> types = MoreIterators.toList(type.elements()).stream()
          .map(s -> JsonSchemaType.fromJsonSchemaType(s.asText()))
          .collect(Collectors.toList());
      Preconditions.checkState(type.size() <= 2, "Unsupported types: " + types);
      return types;
    } else if (type.isTextual()) {
      return Collections.singletonList(JsonSchemaType.fromJsonSchemaType(type.asText()));
    } else {
      throw new IllegalStateException("Unexpected type: " + type);
    }
  }

}
