/* Copyright (c) 2026 Airbyte, Inc., all rights reserved. */
package io.airbyte.integrations.source.mongodb.discover

import com.fasterxml.jackson.databind.JsonNode
import com.fasterxml.jackson.databind.node.ObjectNode
import io.airbyte.cdk.data.AirbyteSchemaType
import io.airbyte.cdk.data.ArrayAirbyteSchemaType
import io.airbyte.cdk.data.JsonEncoder
import io.airbyte.cdk.data.LeafAirbyteSchemaType
import io.airbyte.cdk.discover.CdcIntegerMetaFieldType
import io.airbyte.cdk.discover.FieldType
import io.airbyte.cdk.discover.MetaField
import io.airbyte.cdk.read.Stream
import io.airbyte.cdk.util.Jsons
import io.airbyte.integrations.source.mongodb.read.record.MongoBooleanValueCodec
import io.airbyte.integrations.source.mongodb.read.record.MongoDbValueCodec
import io.airbyte.integrations.source.mongodb.read.record.MongoJsonbValueCodec
import io.airbyte.integrations.source.mongodb.read.record.MongoNullValueCodec
import io.airbyte.integrations.source.mongodb.read.record.MongoNumberValueCodec
import io.airbyte.integrations.source.mongodb.read.record.MongoStringValueCodec

/**
 * [FieldType]s of a document's top-level fields, discovered by sampling (`$type`). A field may hold
 * different BSON types across documents, so the type is a hint: values convert by their actual
 * type.
 */
enum class MongoDbFieldType(
    override val airbyteSchemaType: AirbyteSchemaType,
    private val jsonSchemaTemplate: ObjectNode,
    /** Codec matching this type's `airbyteSchemaType` for JSONL and protobuf output. */
    val valueCodec: MongoDbValueCodec,
) : FieldType {
    STRING(LeafAirbyteSchemaType.STRING, jsonSchemaOf("string"), MongoStringValueCodec),
    NUMBER(LeafAirbyteSchemaType.NUMBER, jsonSchemaOf("number"), MongoNumberValueCodec),
    BOOLEAN(LeafAirbyteSchemaType.BOOLEAN, jsonSchemaOf("boolean"), MongoBooleanValueCodec),
    /** Arrays are emitted without an `items` schema. */
    ARRAY(
        ArrayAirbyteSchemaType(LeafAirbyteSchemaType.JSONB),
        jsonSchemaOf("array"),
        MongoJsonbValueCodec,
    ),
    OBJECT(LeafAirbyteSchemaType.JSONB, jsonSchemaOf("object"), MongoJsonbValueCodec),
    NULL(LeafAirbyteSchemaType.NULL, jsonSchemaOf("null"), MongoNullValueCodec),
    ;

    /** Values are converted by their BSON type; the codec adapts them to each output channel. */
    override val jsonEncoder: JsonEncoder<*> = valueCodec

    /** JSON schema of a field of this type, as emitted in the catalog. Returns a fresh copy. */
    fun jsonSchema(): ObjectNode = jsonSchemaTemplate.deepCopy()

    companion object {
        /**
         * Maps a `$type` name to a field type. Unlisted types (`objectId`, `date`, `timestamp`,
         * `binData`, `regex`, ...) are discovered as [STRING], which is how their values are
         * emitted.
         */
        fun fromBsonTypeName(bsonTypeName: String): MongoDbFieldType =
            when (bsonTypeName) {
                "bool" -> BOOLEAN
                "int",
                "long",
                "double",
                "decimal" -> NUMBER
                "array" -> ARRAY
                "object",
                "javascriptWithScope" -> OBJECT
                "null" -> NULL
                else -> STRING
            }

        /** The inverse of [jsonSchema]: the field type of a catalog property's `{"type": ...}`. */
        fun fromJsonSchema(property: JsonNode): MongoDbFieldType =
            when (property["type"]?.asText()) {
                "boolean" -> BOOLEAN
                "number" -> NUMBER
                "array" -> ARRAY
                "object" -> OBJECT
                "null" -> NULL
                else -> STRING
            }
    }
}

private fun jsonSchemaOf(type: String): ObjectNode = Jsons.objectNode().put("type", type)

/** The declared [MongoDbFieldType] of each non-meta field of a stream, by field id. */
fun schemaFieldTypesOf(stream: Stream): Map<String, MongoDbFieldType> =
    stream.schema
        .filterNot { it.id.startsWith(MetaField.META_PREFIX) }
        .mapNotNull { field -> (field.type as? MongoDbFieldType)?.let { field.id to it } }
        .toMap()

/** MongoDB-specific [MetaField]s, in addition to [io.airbyte.cdk.discover.CommonMetaField]. */
enum class MongoDbMetaField(
    override val type: FieldType,
) : MetaField {
    /** Monotonic per-sync counter used as the (source-defined) cursor of every stream. */
    CDC_CURSOR(CdcIntegerMetaFieldType),
    ;

    override val id: String
        get() = MetaField.META_PREFIX + name.lowercase()
}
