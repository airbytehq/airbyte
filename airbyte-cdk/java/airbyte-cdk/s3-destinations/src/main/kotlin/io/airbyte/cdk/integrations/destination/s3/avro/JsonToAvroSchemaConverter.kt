/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.integrations.destination.s3.avro

import com.fasterxml.jackson.databind.JsonNode
import com.fasterxml.jackson.databind.node.ArrayNode
import com.google.common.base.Preconditions
import io.airbyte.cdk.integrations.base.JavaBaseConstants
import io.airbyte.commons.util.MoreIterators
import io.github.oshai.kotlinlogging.KotlinLogging
import java.util.LinkedList
import java.util.Objects
import java.util.Optional
import java.util.function.Predicate
import org.apache.avro.LogicalTypes
import org.apache.avro.Schema
import org.apache.avro.SchemaBuilder
import tech.allegro.schema.json2avro.converter.AdditionalPropertyField

private val logger = KotlinLogging.logger {}

/**
 * The main function of this class is to convert a JsonSchema to Avro schema. It can also
 * standardize schema names, and keep track of a mapping from the original names to the standardized
 * ones, which is needed for unit tests. <br></br> For limitations of this converter, see the README
 * of this connector: https://docs.airbyte.io/integrations/destinations/s3#avro
 */
class JsonToAvroSchemaConverter {
    private val standardizedNames: MutableMap<String, String> = HashMap()

    fun getStandardizedNames(): Map<String, String> {
        return standardizedNames
    }

    /** @return Avro schema based on the input `jsonSchema`. */
    fun getAvroSchema(jsonSchema: JsonNode, streamName: String, namespace: String?): Schema {
        return getAvroSchema(
            jsonSchema,
            streamName,
            namespace,
            appendAirbyteFields = true,
            appendExtraProps = true,
            addStringToLogicalTypes = true,
            isRootNode = true
        )
    }

    /**
     * @param appendAirbyteFields Add default airbyte fields (e.g. _airbyte_id) to the output Avro
     * schema.
     * @param appendExtraProps Add default additional property field to the output Avro schema.
     * @param addStringToLogicalTypes Default logical type field to string.
     * @param isRootNode Whether it is the root field in the input Json schema.
     * @return Avro schema based on the input `jsonSchema`.
     */
    fun getAvroSchema(
        jsonSchema: JsonNode,
        fieldName: String,
        fieldNamespace: String?,
        appendAirbyteFields: Boolean,
        appendExtraProps: Boolean,
        addStringToLogicalTypes: Boolean,
        isRootNode: Boolean
    ): Schema {
        val stdName: String = AvroConstants.NAME_TRANSFORMER.getIdentifier(fieldName)
        val stdNamespace: String? =
            if (fieldNamespace != null) AvroConstants.NAME_TRANSFORMER.getNamespace(fieldNamespace)
            else null
        val builder: SchemaBuilder.RecordBuilder<Schema> = SchemaBuilder.record(stdName)
        if (stdName != fieldName) {
            standardizedNames[fieldName] = stdName
            logger.warn {
                "Schema name \"$fieldName\" contains illegal character(s) and is standardized to \"$stdName\""
            }
            builder.doc(
                "${AvroConstants.DOC_KEY_ORIGINAL_NAME}${AvroConstants.DOC_KEY_VALUE_DELIMITER}$fieldName"
            )
        }
        if (stdNamespace != null) {
            builder.namespace(stdNamespace)
        }

        val properties: JsonNode? = jsonSchema.get("properties")
        // object field with no "properties" will be handled by the default additional properties
        // field during object conversion; so it is fine if there is no "properties"
        val subfieldNames: List<String> =
            if (properties == null) emptyList()
            else ArrayList(MoreIterators.toList(properties.fieldNames()))

        val assembler: SchemaBuilder.FieldAssembler<Schema> = builder.fields()

        if (appendAirbyteFields) {
            assembler
                .name(JavaBaseConstants.COLUMN_NAME_AB_ID)
                .type(
                    UUID_SCHEMA,
                )
                .noDefault()
            assembler
                .name(JavaBaseConstants.COLUMN_NAME_EMITTED_AT)
                .type(TIMESTAMP_MILLIS_SCHEMA)
                .noDefault()
        }

        for (subfieldName: String in subfieldNames) {
            // ignore additional properties fields, which will be consolidated
            // into one field at the end
            if (AvroConstants.JSON_EXTRA_PROPS_FIELDS.contains(subfieldName)) {
                continue
            }

            val stdFieldName: String = AvroConstants.NAME_TRANSFORMER.getIdentifier(subfieldName)
            val subfieldDefinition: JsonNode = properties!!.get(subfieldName)
            val fieldBuilder: SchemaBuilder.FieldBuilder<Schema> = assembler.name(stdFieldName)
            if (stdFieldName != subfieldName) {
                standardizedNames[subfieldName] = stdFieldName
                logger.warn {
                    "Field name \"$subfieldName\" contains illegal character(s) and is standardized to \"$stdFieldName\""
                }
                fieldBuilder.doc(
                    "${AvroConstants.DOC_KEY_ORIGINAL_NAME}${AvroConstants.DOC_KEY_VALUE_DELIMITER}$subfieldName"
                )
            }
            val subfieldNamespace: String? =
                if (
                    isRootNode // Omit the namespace for root level fields, because it is directly
                // assigned in the builder above.
                // This may not be the correct choice.
                ) null
                else (if (stdNamespace == null) stdName else ("$stdNamespace.$stdName"))
            fieldBuilder
                .type(
                    parseJsonField(
                        subfieldName,
                        subfieldNamespace,
                        subfieldDefinition,
                        appendExtraProps,
                        addStringToLogicalTypes,
                    ),
                )
                .withDefault(null)
        }

        if (appendExtraProps) {
            // support additional properties in one field
            assembler
                .name(AvroConstants.AVRO_EXTRA_PROPS_FIELD)
                .type(AdditionalPropertyField.FIELD_SCHEMA)
                .withDefault(null)
        }

        return assembler.endRecord()
    }

    /**
     * Generate Avro schema for a single Json field type. For example:
     *
     * <pre> "number" -> ["double"] </pre> *
     */
    @Suppress("DEPRECATION")
    private fun parseSingleType(
        fieldName: String,
        fieldNamespace: String?,
        fieldType: JsonSchemaType,
        fieldDefinition: JsonNode,
        appendExtraProps: Boolean,
        addStringToLogicalTypes: Boolean
    ): Schema {
        Preconditions.checkState(
            fieldType != JsonSchemaType.NULL,
            "Null types should have been filtered out",
        )

        // the additional properties fields are filtered out and never passed into this method;
        // but this method is able to handle them for completeness
        if (AvroConstants.JSON_EXTRA_PROPS_FIELDS.contains(fieldName)) {
            return AdditionalPropertyField.FIELD_SCHEMA
        }

        val fieldSchema: Schema
        when (fieldType) {
            JsonSchemaType.INTEGER_V1,
            JsonSchemaType.NUMBER_V1,
            JsonSchemaType.BOOLEAN_V1,
            JsonSchemaType.STRING_V1,
            JsonSchemaType.TIME_WITH_TIMEZONE_V1,
            JsonSchemaType.BINARY_DATA_V1 -> fieldSchema = Schema.create(fieldType.avroType)
            JsonSchemaType.DATE_V1 ->
                fieldSchema =
                    LogicalTypes.date()
                        .addToSchema(
                            Schema.create(
                                Schema.Type.INT,
                            ),
                        )
            JsonSchemaType.TIMESTAMP_WITH_TIMEZONE_V1,
            JsonSchemaType.TIMESTAMP_WITHOUT_TIMEZONE_V1 ->
                fieldSchema =
                    LogicalTypes.timestampMicros().addToSchema(Schema.create(Schema.Type.LONG))
            JsonSchemaType.TIME_WITHOUT_TIMEZONE_V1 ->
                fieldSchema =
                    LogicalTypes.timeMicros()
                        .addToSchema(
                            Schema.create(Schema.Type.LONG),
                        )
            JsonSchemaType.INTEGER_V0,
            JsonSchemaType.NUMBER_V0,
            JsonSchemaType.NUMBER_INT_V0,
            JsonSchemaType.NUMBER_BIGINT_V0,
            JsonSchemaType.NUMBER_FLOAT_V0,
            JsonSchemaType.BOOLEAN_V0 -> fieldSchema = Schema.create(fieldType.avroType)
            JsonSchemaType.STRING_V0 -> {
                if (fieldDefinition.has("format")) {
                    val format: String = fieldDefinition.get("format").asText()
                    fieldSchema =
                        when (format) {
                            "date-time" ->
                                LogicalTypes.timestampMicros()
                                    .addToSchema(
                                        Schema.create(Schema.Type.LONG),
                                    )
                            "date" ->
                                LogicalTypes.date().addToSchema(Schema.create(Schema.Type.INT))
                            "time" ->
                                LogicalTypes.timeMicros()
                                    .addToSchema(Schema.create(Schema.Type.LONG))
                            else -> Schema.create(fieldType.avroType)
                        }
                } else {
                    fieldSchema = Schema.create(fieldType.avroType)
                }
            }
            JsonSchemaType.COMBINED -> {
                val combinedRestriction: Optional<JsonNode> =
                    getCombinedRestriction(fieldDefinition)
                val unionTypes: List<Schema> =
                    parseJsonTypeUnion(
                        fieldName,
                        fieldNamespace,
                        combinedRestriction.get() as ArrayNode,
                        appendExtraProps,
                        addStringToLogicalTypes,
                    )
                fieldSchema = createUnionAndCheckLongTypesDuplications(unionTypes)
            }
            JsonSchemaType.ARRAY -> {
                val items: JsonNode? = fieldDefinition.get("items")
                if (items == null) {
                    logger.warn {
                        "Array field \"$fieldName\" does not specify the items type. It will default to an array of strings"
                    }
                    fieldSchema =
                        Schema.createArray(
                            Schema.createUnion(
                                NULL_SCHEMA,
                                STRING_SCHEMA,
                            ),
                        )
                } else if (items.isObject) {
                    if (
                        (items.has("type") && !items.get("type").isNull) ||
                            items.has("\$ref") && !items.get("\$ref").isNull
                    ) {
                        // Objects inside Json array has no names. We name it with the ".items"
                        // suffix.
                        val elementFieldName: String = "$fieldName.items"
                        fieldSchema =
                            Schema.createArray(
                                parseJsonField(
                                    elementFieldName,
                                    fieldNamespace,
                                    items,
                                    appendExtraProps,
                                    addStringToLogicalTypes,
                                ),
                            )
                    } else {
                        logger.warn {
                            "Array field \"$fieldName\" does not specify the items type. it will default to an array of strings"
                        }
                        fieldSchema =
                            Schema.createArray(
                                Schema.createUnion(
                                    NULL_SCHEMA,
                                    STRING_SCHEMA,
                                ),
                            )
                    }
                } else if (items.isArray) {
                    val arrayElementTypes: MutableList<Schema> =
                        parseJsonTypeUnion(
                            fieldName,
                            fieldNamespace,
                            items as ArrayNode,
                            appendExtraProps,
                            addStringToLogicalTypes,
                        )
                    arrayElementTypes.add(0, NULL_SCHEMA)
                    fieldSchema = Schema.createArray(Schema.createUnion(arrayElementTypes))
                } else {
                    logger.warn {
                        "Array field \"$fieldName\" has invalid items specification: $items. It will default to an array of strings."
                    }
                    fieldSchema =
                        Schema.createArray(
                            Schema.createUnion(
                                NULL_SCHEMA,
                                STRING_SCHEMA,
                            ),
                        )
                }
            }
            JsonSchemaType.OBJECT ->
                fieldSchema =
                    getAvroSchema(
                        fieldDefinition,
                        fieldName,
                        fieldNamespace,
                        false,
                        appendExtraProps,
                        addStringToLogicalTypes,
                        false,
                    )
            else -> {
                logger.warn {
                    "Field \"$fieldName\" has invalid type definition: $fieldDefinition. It will default to string."
                }
                fieldSchema = Schema.createUnion(NULL_SCHEMA, STRING_SCHEMA)
            }
        }
        return fieldSchema
    }

    /**
     * Take in a union of Json field definitions, and generate Avro field schema unions. For
     * example:
     *
     * <pre> ["number", { ... }] -> ["double", { ... }] </pre> *
     */
    private fun parseJsonTypeUnion(
        fieldName: String,
        fieldNamespace: String?,
        types: ArrayNode,
        appendExtraProps: Boolean,
        addStringToLogicalTypes: Boolean
    ): MutableList<Schema> {
        val schemas: List<Schema> =
            MoreIterators.toList(types.elements())
                .flatMap { definition: JsonNode ->
                    getSchemas(
                        fieldName = fieldName,
                        fieldNamespace = fieldNamespace,
                        definition = definition,
                        appendExtraProps = appendExtraProps,
                        addStringToLogicalTypes = addStringToLogicalTypes
                    )
                }
                .distinct()
                .toList()

        return mergeRecordSchemas(fieldName, fieldNamespace, schemas, appendExtraProps)
    }

    private fun getSchemas(
        fieldName: String,
        fieldNamespace: String?,
        definition: JsonNode,
        appendExtraProps: Boolean,
        addStringToLogicalTypes: Boolean
    ): List<Schema> {
        return getNonNullTypes(fieldName, definition).flatMap { type: JsonSchemaType ->
            getSchema(
                fieldName = fieldName,
                fieldNamespace = fieldNamespace,
                type = type,
                definition = definition,
                appendExtraProps = appendExtraProps,
                addStringToLogicalTypes = addStringToLogicalTypes
            )
        }
    }

    private fun getSchema(
        fieldName: String,
        fieldNamespace: String?,
        type: JsonSchemaType,
        definition: JsonNode,
        appendExtraProps: Boolean,
        addStringToLogicalTypes: Boolean
    ): List<Schema> {
        val namespace: String =
            if (fieldNamespace == null) fieldName else "$fieldNamespace.$fieldName"
        val singleFieldSchema: Schema =
            parseSingleType(
                fieldName,
                namespace,
                type,
                definition,
                appendExtraProps,
                addStringToLogicalTypes,
            )
        if (singleFieldSchema.isUnion) {
            return singleFieldSchema.types
        } else {
            return listOf(
                singleFieldSchema,
            )
        }
    }

    /**
     * If there are multiple object fields, those fields are combined into one Avro record. This is
     * because Avro does not allow specifying a tuple of types (i.e. the first element is type x,
     * the second element is type y, and so on). For example, the following Json field types:
     *
     * <pre> [ { "type": "object", "properties": { "id": { "type": "integer" } } }, { "type":
     * "object", "properties": { "id": { "type": "string" } "message": { "type": "string" } } } ]
     * </pre> *
     *
     * is converted to this Avro schema:
     *
     * <pre> { "type": "record", "fields": [ { "name": "id", "type": ["int", "string"] }, { "name":
     * "message", "type": "string" } ] } </pre> *
     */
    private fun mergeRecordSchemas(
        fieldName: String,
        fieldNamespace: String?,
        schemas: List<Schema>,
        appendExtraProps: Boolean
    ): MutableList<Schema> {
        val recordFieldSchemas: LinkedHashMap<String, MutableList<Schema>> = LinkedHashMap()
        val recordFieldDocs: MutableMap<String, MutableList<String>> = HashMap()

        val mergedSchemas: MutableList<Schema> =
            schemas

                // gather record schemas to construct a single record schema later on
                .onEach { schema: Schema ->
                    if (schema.type == Schema.Type.RECORD) {
                        for (field: Schema.Field in schema.fields) {
                            recordFieldSchemas.putIfAbsent(
                                field.name(),
                                LinkedList(),
                            )
                            recordFieldSchemas[field.name()]!!.add(field.schema())
                            if (field.doc() != null) {
                                recordFieldDocs.putIfAbsent(
                                    field.name(),
                                    LinkedList(),
                                )
                                recordFieldDocs[field.name()]!!.add(field.doc())
                            }
                        }
                    }
                } // remove record schemas because they will be merged into one
                .filter { schema: Schema -> schema.type != Schema.Type.RECORD }
                .toMutableList()
        // create one record schema from all the record fields
        if (recordFieldSchemas.isNotEmpty()) {
            val builder: SchemaBuilder.RecordBuilder<Schema> = SchemaBuilder.record(fieldName)
            if (fieldNamespace != null) {
                builder.namespace(fieldNamespace)
            }

            val assembler: SchemaBuilder.FieldAssembler<Schema> = builder.fields()

            for (entry: Map.Entry<String, List<Schema>> in recordFieldSchemas.entries) {
                val subfieldName: String = entry.key
                // ignore additional properties fields, which will be consolidated
                // into one field at the end
                if (AvroConstants.JSON_EXTRA_PROPS_FIELDS.contains(subfieldName)) {
                    continue
                }

                val subfieldBuilder: SchemaBuilder.FieldBuilder<Schema> =
                    assembler.name(subfieldName)
                val subfieldDocs: List<String> =
                    recordFieldDocs.getOrDefault(subfieldName, emptyList())
                if (subfieldDocs.isNotEmpty()) {
                    subfieldBuilder.doc(subfieldDocs.joinToString(separator = "; "))
                }
                val subfieldSchemas: List<Schema> =
                    entry.value
                        .flatMap { schema: Schema ->
                            schema.types
                                // filter out null and add it later on as the first
                                // element
                                .filter { s: Schema -> s != NULL_SCHEMA }
                        }
                        .distinct()
                        .toList()
                val subfieldNamespace: String =
                    if (fieldNamespace == null) fieldName else ("$fieldNamespace.$fieldName")
                // recursively merge schemas of a subfield because they may include multiple record
                // schemas as well
                val mergedSubfieldSchemas: MutableList<Schema> =
                    mergeRecordSchemas(
                        subfieldName,
                        subfieldNamespace,
                        subfieldSchemas,
                        appendExtraProps,
                    )
                mergedSubfieldSchemas.add(0, NULL_SCHEMA)
                subfieldBuilder.type(Schema.createUnion(mergedSubfieldSchemas)).withDefault(null)
            }

            if (appendExtraProps) {
                // add back additional properties
                assembler
                    .name(AvroConstants.AVRO_EXTRA_PROPS_FIELD)
                    .type(AdditionalPropertyField.FIELD_SCHEMA)
                    .withDefault(null)
            }
            mergedSchemas.add(assembler.endRecord())
        }

        return mergedSchemas
    }

    /**
     * Take in a Json field definition, and generate a nullable Avro field schema. For example:
     *
     * <pre> {"type": ["number", { ... }]} -> ["null", "double", { ... }] </pre> *
     */
    fun parseJsonField(
        fieldName: String,
        fieldNamespace: String?,
        fieldDefinition: JsonNode,
        appendExtraProps: Boolean,
        addStringToLogicalTypes: Boolean
    ): Schema {
        // Filter out null types, which will be added back in the end.
        val nonNullFieldTypes: MutableList<Schema> =
            getNonNullTypes(fieldName, fieldDefinition)
                .flatMap { fieldType: JsonSchemaType ->
                    val singleFieldSchema: Schema =
                        parseSingleType(
                            fieldName,
                            fieldNamespace,
                            fieldType,
                            fieldDefinition,
                            appendExtraProps,
                            addStringToLogicalTypes,
                        )
                    if (singleFieldSchema.isUnion) {
                        return@flatMap singleFieldSchema.types
                    } else {
                        return@flatMap listOf(
                            singleFieldSchema,
                        )
                    }
                }
                .distinct()
                .toMutableList()

        if (nonNullFieldTypes.isEmpty()) {
            return Schema.create(Schema.Type.NULL)
        } else {
            // Mark every field as nullable to prevent missing value exceptions from Avro / Parquet.
            if (!nonNullFieldTypes.contains(NULL_SCHEMA)) {
                nonNullFieldTypes.add(0, NULL_SCHEMA)
            }
            // Logical types are converted to a union of logical type itself and string. The purpose
            // is to
            // default the logical type field to a string, if the value of the logical type field is
            // invalid and
            // cannot be properly processed.
            if (
                ((nonNullFieldTypes.any { schema: Schema -> schema.logicalType != null }) &&
                    (!nonNullFieldTypes.contains(STRING_SCHEMA)) &&
                    addStringToLogicalTypes)
            ) {
                nonNullFieldTypes.add(STRING_SCHEMA)
            }
            return Schema.createUnion(nonNullFieldTypes)
        }
    }

    /**
     * Method checks unionTypes list for content. If we have both "long" and "long-timestamp" types
     * then it keeps the "long" only. Need to do it for Schema creation otherwise it would fail with
     * a duplicated types exception.
     *
     * @param unionTypes
     * - list of union types
     * @return new Schema
     */
    private fun createUnionAndCheckLongTypesDuplications(unionTypes: List<Schema>): Schema {
        val isALong: Predicate<Schema> = Predicate { type: Schema -> type.type == Schema.Type.LONG }
        val isPlainLong: Predicate<Schema> =
            isALong.and { type: Schema ->
                Objects.isNull(
                    type.logicalType,
                )
            }
        val isTimestampMicrosLong: Predicate<Schema> =
            isALong.and { type: Schema ->
                Objects.nonNull(
                    type.logicalType,
                ) && ("timestamp-micros" == type.logicalType.name)
            }

        val hasPlainLong: Boolean = unionTypes.any { isPlainLong.test(it) }
        val hasTimestampMicrosLong: Boolean = unionTypes.any { isTimestampMicrosLong.test(it) }
        val removeTimestampType: Predicate<Schema> = Predicate { type: Schema ->
            !(hasPlainLong &&
                hasTimestampMicrosLong &&
                isTimestampMicrosLong.test(
                    type,
                ))
        }
        return Schema.createUnion(unionTypes.filter { removeTimestampType.test(it) }.toList())
    }

    companion object {
        private const val REFERENCE_TYPE: String = "\$ref"
        private const val TYPE: String = "type"
        private const val AIRBYTE_TYPE: String = "airbyte_type"
        private val UUID_SCHEMA: Schema =
            LogicalTypes.uuid().addToSchema(Schema.create(Schema.Type.STRING))
        private val NULL_SCHEMA: Schema = Schema.create(Schema.Type.NULL)
        private val STRING_SCHEMA: Schema = Schema.create(Schema.Type.STRING)

        private val TIMESTAMP_MILLIS_SCHEMA: Schema =
            LogicalTypes.timestampMillis().addToSchema(Schema.create(Schema.Type.LONG))

        @Suppress("DEPRECATION")
        fun getNonNullTypes(fieldName: String?, fieldDefinition: JsonNode): List<JsonSchemaType> {
            return getTypes(fieldName, fieldDefinition)
                .filter { type: JsonSchemaType -> type != JsonSchemaType.NULL }
                .toList()
        }

        /** When no type or $ref are specified, it will default to string. */
        fun getTypes(fieldName: String?, fieldDefinition: JsonNode): List<JsonSchemaType> {
            val combinedRestriction: Optional<JsonNode> = getCombinedRestriction(fieldDefinition)
            if (combinedRestriction.isPresent) {
                return listOf(JsonSchemaType.COMBINED)
            }

            val typeProperty: JsonNode? = fieldDefinition.get(TYPE)
            val referenceType: JsonNode? = fieldDefinition.get(REFERENCE_TYPE)
            val airbyteType: String? = fieldDefinition.get(AIRBYTE_TYPE)?.asText()

            if (typeProperty != null && typeProperty.isArray) {
                return MoreIterators.toList(typeProperty.elements())
                    .map { s: JsonNode ->
                        JsonSchemaType.fromJsonSchemaType(
                            s.asText(),
                        )
                    }
                    .toList()
            }

            if (hasTextValue(typeProperty)) {
                return listOf(
                    JsonSchemaType.fromJsonSchemaType(
                        typeProperty!!.asText(),
                        airbyteType,
                    ),
                )
            }

            if (hasTextValue(referenceType)) {
                return listOf(
                    JsonSchemaType.fromJsonSchemaType(
                        referenceType!!.asText(),
                        airbyteType,
                    ),
                )
            }

            logger.warn {
                "Field \"$fieldName\" has unexpected type $referenceType. It will default to string."
            }
            return listOf(JsonSchemaType.STRING_V1)
        }

        private fun hasTextValue(value: JsonNode?): Boolean {
            return (value != null) && !value.isNull && value.isTextual
        }

        fun getCombinedRestriction(fieldDefinition: JsonNode): Optional<JsonNode> {
            if (fieldDefinition.has("anyOf")) {
                return Optional.of(fieldDefinition.get("anyOf"))
            }
            if (fieldDefinition.has("allOf")) {
                return Optional.of(fieldDefinition.get("allOf"))
            }
            if (fieldDefinition.has("oneOf")) {
                return Optional.of(fieldDefinition.get("oneOf"))
            }
            return Optional.empty()
        }
    }
}
