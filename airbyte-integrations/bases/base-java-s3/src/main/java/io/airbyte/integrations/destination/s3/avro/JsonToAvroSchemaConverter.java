/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
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
import java.util.LinkedHashMap;
import java.util.LinkedList;
import java.util.List;
import java.util.Map;
import java.util.Optional;
import java.util.stream.Collectors;
import java.util.stream.Stream;
import javax.annotation.Nullable;
import org.apache.avro.LogicalTypes;
import org.apache.avro.Schema;
import org.apache.avro.SchemaBuilder;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import tech.allegro.schema.json2avro.converter.AdditionalPropertyField;

/**
 * The main function of this class is to convert a JsonSchema to Avro schema. It can also
 * standardize schema names, and keep track of a mapping from the original names to the standardized
 * ones, which is needed for unit tests. <br/>
 * For limitations of this converter, see the README of this connector:
 * https://docs.airbyte.io/integrations/destinations/s3#avro
 */
public class JsonToAvroSchemaConverter {

  private static final String REFERENCE_TYPE = "$ref";
  private static final String TYPE = "type";
  private static final String AIRBYTE_TYPE = "airbyte_type";
  private static final Schema UUID_SCHEMA = LogicalTypes.uuid()
      .addToSchema(Schema.create(Schema.Type.STRING));
  private static final Schema NULL_SCHEMA = Schema.create(Schema.Type.NULL);
  private static final Schema STRING_SCHEMA = Schema.create(Schema.Type.STRING);
  private static final Logger LOGGER = LoggerFactory.getLogger(JsonToAvroSchemaConverter.class);
  private static final Schema TIMESTAMP_MILLIS_SCHEMA = LogicalTypes.timestampMillis()
      .addToSchema(Schema.create(Schema.Type.LONG));

  private final Map<String, String> standardizedNames = new HashMap<>();

  static List<JsonSchemaType> getNonNullTypes(final String fieldName, final JsonNode fieldDefinition) {
    return getTypes(fieldName, fieldDefinition).stream()
        .filter(type -> type != JsonSchemaType.NULL).collect(Collectors.toList());
  }

  /**
   * When no type or $ref are specified, it will default to string.
   */
  static List<JsonSchemaType> getTypes(final String fieldName, final JsonNode fieldDefinition) {
    final Optional<JsonNode> combinedRestriction = getCombinedRestriction(fieldDefinition);
    if (combinedRestriction.isPresent()) {
      return Collections.singletonList(JsonSchemaType.COMBINED);
    }

    final JsonNode typeProperty = fieldDefinition.get(TYPE);
    final JsonNode referenceType = fieldDefinition.get(REFERENCE_TYPE);

    final JsonNode airbyteTypeProperty = fieldDefinition.get(AIRBYTE_TYPE);
    final String airbyteType = airbyteTypeProperty == null ? null : airbyteTypeProperty.asText();

    if (typeProperty != null && typeProperty.isArray()) {
      return MoreIterators.toList(typeProperty.elements()).stream()
          .map(s -> JsonSchemaType.fromJsonSchemaType(s.asText()))
          .collect(Collectors.toList());
    }

    if (hasTextValue(typeProperty)) {
      return Collections.singletonList(JsonSchemaType.fromJsonSchemaType(typeProperty.asText(), airbyteType));
    }

    if (hasTextValue(referenceType)) {
      return Collections.singletonList(JsonSchemaType.fromJsonSchemaType(referenceType.asText(), airbyteType));
    }

    LOGGER.warn("Field \"{}\" has unexpected type {}. It will default to string.", fieldName, referenceType);
    return Collections.singletonList(JsonSchemaType.STRING_V1);
  }

  private static boolean hasTextValue(JsonNode value) {
    return value != null && !value.isNull() && value.isTextual();
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
   * @return Avro schema based on the input {@code jsonSchema}.
   */
  public Schema getAvroSchema(final JsonNode jsonSchema,
                              final String streamName,
                              @Nullable final String namespace) {
    return getAvroSchema(jsonSchema, streamName, namespace, true, true, true, true);
  }

  /**
   * @param appendAirbyteFields Add default airbyte fields (e.g. _airbyte_id) to the output Avro
   *        schema.
   * @param appendExtraProps Add default additional property field to the output Avro schema.
   * @param addStringToLogicalTypes Default logical type field to string.
   * @param isRootNode Whether it is the root field in the input Json schema.
   * @return Avro schema based on the input {@code jsonSchema}.
   */
  public Schema getAvroSchema(final JsonNode jsonSchema,
                              final String fieldName,
                              @Nullable final String fieldNamespace,
                              final boolean appendAirbyteFields,
                              final boolean appendExtraProps,
                              final boolean addStringToLogicalTypes,
                              final boolean isRootNode) {
    final String stdName = AvroConstants.NAME_TRANSFORMER.getIdentifier(fieldName);
    final String stdNamespace = AvroConstants.NAME_TRANSFORMER.getNamespace(fieldNamespace);
    final SchemaBuilder.RecordBuilder<Schema> builder = SchemaBuilder.record(stdName);
    if (!stdName.equals(fieldName)) {
      standardizedNames.put(fieldName, stdName);
      LOGGER.warn("Schema name \"{}\" contains illegal character(s) and is standardized to \"{}\"", fieldName,
          stdName);
      builder.doc(
          String.format("%s%s%s",
              AvroConstants.DOC_KEY_ORIGINAL_NAME,
              AvroConstants.DOC_KEY_VALUE_DELIMITER,
              fieldName));
    }
    if (stdNamespace != null) {
      builder.namespace(stdNamespace);
    }

    final JsonNode properties = jsonSchema.get("properties");
    // object field with no "properties" will be handled by the default additional properties
    // field during object conversion; so it is fine if there is no "properties"
    final List<String> subfieldNames = properties == null
        ? Collections.emptyList()
        : new ArrayList<>(MoreIterators.toList(properties.fieldNames()));

    final SchemaBuilder.FieldAssembler<Schema> assembler = builder.fields();

    if (appendAirbyteFields) {
      assembler.name(JavaBaseConstants.COLUMN_NAME_AB_ID).type(UUID_SCHEMA).noDefault();
      assembler.name(JavaBaseConstants.COLUMN_NAME_EMITTED_AT)
          .type(TIMESTAMP_MILLIS_SCHEMA).noDefault();
    }

    for (final String subfieldName : subfieldNames) {
      // ignore additional properties fields, which will be consolidated
      // into one field at the end
      if (AvroConstants.JSON_EXTRA_PROPS_FIELDS.contains(subfieldName)) {
        continue;
      }

      final String stdFieldName = AvroConstants.NAME_TRANSFORMER.getIdentifier(subfieldName);
      final JsonNode subfieldDefinition = properties.get(subfieldName);
      final SchemaBuilder.FieldBuilder<Schema> fieldBuilder = assembler.name(stdFieldName);
      if (!stdFieldName.equals(subfieldName)) {
        standardizedNames.put(subfieldName, stdFieldName);
        LOGGER.warn("Field name \"{}\" contains illegal character(s) and is standardized to \"{}\"",
            subfieldName, stdFieldName);
        fieldBuilder.doc(String.format("%s%s%s",
            AvroConstants.DOC_KEY_ORIGINAL_NAME,
            AvroConstants.DOC_KEY_VALUE_DELIMITER,
            subfieldName));
      }
      final String subfieldNamespace = isRootNode
          // Omit the namespace for root level fields, because it is directly assigned in the builder above.
          // This may not be the correct choice.
          ? null
          : (stdNamespace == null ? stdName : (stdNamespace + "." + stdName));
      fieldBuilder.type(parseJsonField(subfieldName, subfieldNamespace, subfieldDefinition, appendExtraProps, addStringToLogicalTypes))
          .withDefault(null);
    }

    if (appendExtraProps) {
      // support additional properties in one field
      assembler.name(AvroConstants.AVRO_EXTRA_PROPS_FIELD)
          .type(AdditionalPropertyField.FIELD_SCHEMA).withDefault(null);
    }

    return assembler.endRecord();
  }

  /**
   * Generate Avro schema for a single Json field type. For example:
   *
   * <pre>
   * "number" -> ["double"]
   * </pre>
   */
  Schema parseSingleType(final String fieldName,
                         @Nullable final String fieldNamespace,
                         final JsonSchemaType fieldType,
                         final JsonNode fieldDefinition,
                         final boolean appendExtraProps,
                         final boolean addStringToLogicalTypes) {
    Preconditions
        .checkState(fieldType != JsonSchemaType.NULL, "Null types should have been filtered out");

    // the additional properties fields are filtered out and never passed into this method;
    // but this method is able to handle them for completeness
    if (AvroConstants.JSON_EXTRA_PROPS_FIELDS.contains(fieldName)) {
      return AdditionalPropertyField.FIELD_SCHEMA;
    }

    final Schema fieldSchema;
    switch (fieldType) {
      case INTEGER_V1, NUMBER_V1, BOOLEAN_V1, STRING_V1, TIME_WITH_TIMEZONE_V1, BINARY_DATA_V1 -> fieldSchema =
          Schema.create(fieldType.getAvroType());
      case DATE_V1 -> fieldSchema = LogicalTypes.date().addToSchema(Schema.create(Schema.Type.INT));
      case TIMESTAMP_WITH_TIMEZONE_V1, TIMESTAMP_WITHOUT_TIMEZONE_V1 -> fieldSchema = LogicalTypes.timestampMicros()
          .addToSchema(Schema.create(Schema.Type.LONG));
      case TIME_WITHOUT_TIMEZONE_V1 -> fieldSchema = LogicalTypes.timeMicros().addToSchema(Schema.create(Schema.Type.LONG));
      case INTEGER_V0, NUMBER_V0, NUMBER_INT_V0, NUMBER_BIGINT_V0, NUMBER_FLOAT_V0, BOOLEAN_V0 -> fieldSchema =
          Schema.create(fieldType.getAvroType());
      case STRING_V0 -> {
        if (fieldDefinition.has("format")) {
          final String format = fieldDefinition.get("format").asText();
          fieldSchema = switch (format) {
            case "date-time" -> LogicalTypes.timestampMicros().addToSchema(Schema.create(Schema.Type.LONG));
            case "date" -> LogicalTypes.date().addToSchema(Schema.create(Schema.Type.INT));
            case "time" -> LogicalTypes.timeMicros().addToSchema(Schema.create(Schema.Type.LONG));
            default -> Schema.create(fieldType.getAvroType());
          };
        } else {
          fieldSchema = Schema.create(fieldType.getAvroType());
        }
      }
      case COMBINED -> {
        final Optional<JsonNode> combinedRestriction = getCombinedRestriction(fieldDefinition);
        final List<Schema> unionTypes =
            parseJsonTypeUnion(fieldName, fieldNamespace, (ArrayNode) combinedRestriction.get(), appendExtraProps, addStringToLogicalTypes);
        fieldSchema = Schema.createUnion(unionTypes);
      }
      case ARRAY -> {
        final JsonNode items = fieldDefinition.get("items");
        if (items == null) {
          LOGGER.warn("Array field \"{}\" does not specify the items type. It will default to an array of strings", fieldName);
          fieldSchema = Schema.createArray(Schema.createUnion(NULL_SCHEMA, STRING_SCHEMA));
        } else if (items.isObject()) {
          if ((items.has("type") && !items.get("type").isNull()) ||
              items.has("$ref") && !items.get("$ref").isNull()) {
            // Objects inside Json array has no names. We name it with the ".items" suffix.
            final String elementFieldName = fieldName + ".items";
            fieldSchema = Schema.createArray(parseJsonField(elementFieldName, fieldNamespace, items, appendExtraProps, addStringToLogicalTypes));
          } else {
            LOGGER.warn("Array field \"{}\" does not specify the items type. it will default to an array of strings", fieldName);
            fieldSchema = Schema.createArray(Schema.createUnion(NULL_SCHEMA, STRING_SCHEMA));
          }
        } else if (items.isArray()) {
          final List<Schema> arrayElementTypes =
              parseJsonTypeUnion(fieldName, fieldNamespace, (ArrayNode) items, appendExtraProps, addStringToLogicalTypes);
          arrayElementTypes.add(0, NULL_SCHEMA);
          fieldSchema = Schema.createArray(Schema.createUnion(arrayElementTypes));
        } else {
          LOGGER.warn("Array field \"{}\" has invalid items specification: {}. It will default to an array of strings.", fieldName, items);
          fieldSchema = Schema.createArray(Schema.createUnion(NULL_SCHEMA, STRING_SCHEMA));
        }
      }
      case OBJECT -> fieldSchema =
          getAvroSchema(fieldDefinition, fieldName, fieldNamespace, false, appendExtraProps, addStringToLogicalTypes, false);
      default -> {
        LOGGER.warn("Field \"{}\" has invalid type definition: {}. It will default to string.", fieldName, fieldDefinition);
        fieldSchema = Schema.createUnion(NULL_SCHEMA, STRING_SCHEMA);
      }
    }
    return fieldSchema;
  }

  /**
   * Take in a union of Json field definitions, and generate Avro field schema unions. For example:
   *
   * <pre>
   * ["number", { ... }] -> ["double", { ... }]
   * </pre>
   */
  List<Schema> parseJsonTypeUnion(final String fieldName,
                                  @Nullable final String fieldNamespace,
                                  final ArrayNode types,
                                  final boolean appendExtraProps,
                                  final boolean addStringToLogicalTypes) {
    final List<Schema> schemas = MoreIterators.toList(types.elements())
        .stream()
        .flatMap(definition -> getNonNullTypes(fieldName, definition).stream().flatMap(type -> {
          final String namespace = fieldNamespace == null
              ? fieldName
              : fieldNamespace + "." + fieldName;
          final Schema singleFieldSchema = parseSingleType(fieldName, namespace, type, definition, appendExtraProps, addStringToLogicalTypes);

          if (singleFieldSchema.isUnion()) {
            return singleFieldSchema.getTypes().stream();
          } else {
            return Stream.of(singleFieldSchema);
          }
        }))
        .distinct()
        .collect(Collectors.toList());

    return mergeRecordSchemas(fieldName, fieldNamespace, schemas, appendExtraProps);
  }

  /**
   * If there are multiple object fields, those fields are combined into one Avro record. This is
   * because Avro does not allow specifying a tuple of types (i.e. the first element is type x, the
   * second element is type y, and so on). For example, the following Json field types:
   *
   * <pre>
   * [
   *   {
   *     "type": "object",
   *     "properties": {
   *       "id": { "type": "integer" }
   *     }
   *   },
   *   {
   *     "type": "object",
   *     "properties": {
   *       "id": { "type": "string" }
   *       "message": { "type": "string" }
   *     }
   *   }
   * ]
   * </pre>
   *
   * is converted to this Avro schema:
   *
   * <pre>
   * {
   *   "type": "record",
   *   "fields": [
   *     { "name": "id", "type": ["int", "string"] },
   *     { "name": "message", "type": "string" }
   *   ]
   * }
   * </pre>
   */
  List<Schema> mergeRecordSchemas(final String fieldName,
                                  @Nullable final String fieldNamespace,
                                  final List<Schema> schemas,
                                  final boolean appendExtraProps) {
    final LinkedHashMap<String, List<Schema>> recordFieldSchemas = new LinkedHashMap<>();
    final Map<String, List<String>> recordFieldDocs = new HashMap<>();

    final List<Schema> mergedSchemas = schemas.stream()
        // gather record schemas to construct a single record schema later on
        .peek(schema -> {
          if (schema.getType() == Schema.Type.RECORD) {
            for (final Schema.Field field : schema.getFields()) {
              recordFieldSchemas.putIfAbsent(field.name(), new LinkedList<>());
              recordFieldSchemas.get(field.name()).add(field.schema());
              if (field.doc() != null) {
                recordFieldDocs.putIfAbsent(field.name(), new LinkedList<>());
                recordFieldDocs.get(field.name()).add(field.doc());
              }
            }
          }
        })
        // remove record schemas because they will be merged into one
        .filter(schema -> schema.getType() != Schema.Type.RECORD)
        .collect(Collectors.toList());

    // create one record schema from all the record fields
    if (!recordFieldSchemas.isEmpty()) {
      final SchemaBuilder.RecordBuilder<Schema> builder = SchemaBuilder.record(fieldName);
      if (fieldNamespace != null) {
        builder.namespace(fieldNamespace);
      }

      final SchemaBuilder.FieldAssembler<Schema> assembler = builder.fields();

      for (final Map.Entry<String, List<Schema>> entry : recordFieldSchemas.entrySet()) {
        final String subfieldName = entry.getKey();
        // ignore additional properties fields, which will be consolidated
        // into one field at the end
        if (AvroConstants.JSON_EXTRA_PROPS_FIELDS.contains(subfieldName)) {
          continue;
        }

        final SchemaBuilder.FieldBuilder<Schema> subfieldBuilder = assembler.name(subfieldName);
        final List<String> subfieldDocs = recordFieldDocs.getOrDefault(subfieldName, Collections.emptyList());
        if (!subfieldDocs.isEmpty()) {
          subfieldBuilder.doc(String.join("; ", subfieldDocs));
        }
        final List<Schema> subfieldSchemas = entry.getValue().stream()
            .flatMap(schema -> schema.getTypes().stream()
                // filter out null and add it later on as the first element
                .filter(s -> !s.equals(NULL_SCHEMA)))
            .distinct()
            .collect(Collectors.toList());
        final String subfieldNamespace = fieldNamespace == null ? fieldName : (fieldNamespace + "." + fieldName);
        // recursively merge schemas of a subfield because they may include multiple record schemas as well
        final List<Schema> mergedSubfieldSchemas = mergeRecordSchemas(subfieldName, subfieldNamespace, subfieldSchemas, appendExtraProps);
        mergedSubfieldSchemas.add(0, NULL_SCHEMA);
        subfieldBuilder.type(Schema.createUnion(mergedSubfieldSchemas)).withDefault(null);
      }

      if (appendExtraProps) {
        // add back additional properties
        assembler.name(AvroConstants.AVRO_EXTRA_PROPS_FIELD)
            .type(AdditionalPropertyField.FIELD_SCHEMA).withDefault(null);
      }
      mergedSchemas.add(assembler.endRecord());
    }

    return mergedSchemas;
  }

  /**
   * Take in a Json field definition, and generate a nullable Avro field schema. For example:
   *
   * <pre>
   * {"type": ["number", { ... }]} -> ["null", "double", { ... }]
   * </pre>
   */
  Schema parseJsonField(final String fieldName,
                        @Nullable final String fieldNamespace,
                        final JsonNode fieldDefinition,
                        final boolean appendExtraProps,
                        final boolean addStringToLogicalTypes) {
    // Filter out null types, which will be added back in the end.
    final List<Schema> nonNullFieldTypes = getNonNullTypes(fieldName, fieldDefinition)
        .stream()
        .flatMap(fieldType -> {
          final Schema singleFieldSchema =
              parseSingleType(fieldName, fieldNamespace, fieldType, fieldDefinition, appendExtraProps, addStringToLogicalTypes);
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
      // Logical types are converted to a union of logical type itself and string. The purpose is to
      // default the logical type field to a string, if the value of the logical type field is invalid and
      // cannot be properly processed.
      if ((nonNullFieldTypes
          .stream().anyMatch(schema -> schema.getLogicalType() != null)) &&
          (!nonNullFieldTypes.contains(STRING_SCHEMA)) && addStringToLogicalTypes) {
        nonNullFieldTypes.add(STRING_SCHEMA);
      }
      return Schema.createUnion(nonNullFieldTypes);
    }
  }

}
