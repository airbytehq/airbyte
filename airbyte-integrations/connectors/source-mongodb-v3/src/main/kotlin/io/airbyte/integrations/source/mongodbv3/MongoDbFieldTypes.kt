/* Copyright (c) 2026 Airbyte, Inc., all rights reserved. */
package io.airbyte.integrations.source.mongodbv3

import com.fasterxml.jackson.databind.node.ObjectNode
import io.airbyte.cdk.data.AirbyteSchemaType
import io.airbyte.cdk.data.AnyEncoder
import io.airbyte.cdk.data.ArrayAirbyteSchemaType
import io.airbyte.cdk.data.JsonEncoder
import io.airbyte.cdk.data.LeafAirbyteSchemaType
import io.airbyte.cdk.discover.CdcIntegerMetaFieldType
import io.airbyte.cdk.discover.FieldType
import io.airbyte.cdk.discover.MetaField
import io.airbyte.cdk.util.Jsons

/**
 * [FieldType]s of the top-level fields of a MongoDB document.
 *
 * MongoDB is schemaless: DISCOVER samples documents and records the BSON type name of each field
 * (the `$type` aggregation operator), then maps it to one of these types. Both the mapping (
 * [fromBsonTypeName]) and the JSON schema of each type ([jsonSchema]) mirror the legacy
 * `source-mongodb-v2` connector so that the `discover` output of the two connectors is identical.
 *
 * Because documents in one collection may hold different BSON types under the same field name, the
 * discovered type is only a hint: record values are converted based on their actual BSON type.
 */
enum class MongoDbFieldType(
    override val airbyteSchemaType: AirbyteSchemaType,
    private val jsonSchemaTemplate: ObjectNode,
) : FieldType {
    STRING(LeafAirbyteSchemaType.STRING, legacyJsonSchema("string")),
    NUMBER(LeafAirbyteSchemaType.NUMBER, legacyJsonSchema("number")),
    BOOLEAN(LeafAirbyteSchemaType.BOOLEAN, legacyJsonSchema("boolean")),
    /** The legacy connector emits arrays without an `items` schema. */
    ARRAY(ArrayAirbyteSchemaType(LeafAirbyteSchemaType.JSONB), legacyJsonSchema("array")),
    OBJECT(LeafAirbyteSchemaType.JSONB, legacyJsonSchema("object")),
    NULL(LeafAirbyteSchemaType.NULL, legacyJsonSchema("null")),
    ;

    /** Values are encoded according to their BSON type rather than the discovered type. */
    override val jsonEncoder: JsonEncoder<*> = AnyEncoder

    /** JSON schema of a field of this type, as emitted in the catalog. Returns a fresh copy. */
    fun jsonSchema(): ObjectNode = jsonSchemaTemplate.deepCopy()

    companion object {
        /**
         * Maps a BSON type name, as returned by the `$type` aggregation operator, to a field type.
         *
         * This is the legacy connector's mapping, quirks included: `$type` reports booleans as
         * `bool`, not `boolean`, so boolean fields are discovered as [STRING] like every other
         * unlisted type (`objectId`, `date`, `timestamp`, `binData`, `regex`, `javascript`, ...).
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
    }
}

private fun legacyJsonSchema(type: String): ObjectNode = Jsons.objectNode().put("type", type)

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
