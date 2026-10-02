/* Copyright (c) 2026 Airbyte, Inc., all rights reserved. */
package io.airbyte.integrations.source.mongodbv3.discover

import com.fasterxml.jackson.databind.JsonNode
import com.fasterxml.jackson.databind.node.ObjectNode
import io.airbyte.cdk.data.AirbyteSchemaType
import io.airbyte.cdk.data.ArrayAirbyteSchemaType
import io.airbyte.cdk.data.JsonEncoder
import io.airbyte.cdk.data.LeafAirbyteSchemaType
import io.airbyte.cdk.discover.CdcIntegerMetaFieldType
import io.airbyte.cdk.discover.FieldType
import io.airbyte.cdk.discover.MetaField
import io.airbyte.cdk.util.Jsons
import io.airbyte.integrations.source.mongodbv3.read.MongoBooleanValueCodec
import io.airbyte.integrations.source.mongodbv3.read.MongoDbValueCodec
import io.airbyte.integrations.source.mongodbv3.read.MongoJsonbValueCodec
import io.airbyte.integrations.source.mongodbv3.read.MongoNullValueCodec
import io.airbyte.integrations.source.mongodbv3.read.MongoNumberValueCodec
import io.airbyte.integrations.source.mongodbv3.read.MongoStringValueCodec

/**
 * [FieldType]s of the top-level fields of a document. DISCOVER samples documents, records each
 * field's BSON type name (`$type`) and maps it with [fromBsonTypeName]. Documents in one collection
 * may hold different BSON types under the same field name, so the discovered type is only a hint:
 * record values are converted based on their actual BSON type.
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
         * Maps a `$type` BSON type name to a field type. Note `$type` reports booleans as `bool`,
         * not `boolean`, so they are discovered as [STRING] like every other unlisted type
         * (`objectId`, `date`, `timestamp`, `binData`, `regex`, ...).
         */
        fun fromBsonTypeName(bsonTypeName: String): MongoDbFieldType =
            when (bsonTypeName) {
                "boolean" -> BOOLEAN
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

        /**
         * Recovers the field type from a catalog property's JSON schema (`{"type": ...}`), the
         * inverse of [jsonSchema]. Used at READ time to serve [fields]
         * [MongoDbSourceMetadataQuerier] from the configured catalog rather than re-sampling
         * documents.
         */
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

/**
 * [MetaField]s specific to the MongoDB source, in addition to
 * [io.airbyte.cdk.discover.CommonMetaField].
 */
enum class MongoDbMetaField(
    override val type: FieldType,
) : MetaField {
    /** Monotonic per-sync counter used as the (source-defined) cursor of every stream. */
    CDC_CURSOR(CdcIntegerMetaFieldType),
    ;

    override val id: String
        get() = MetaField.META_PREFIX + name.lowercase()
}
