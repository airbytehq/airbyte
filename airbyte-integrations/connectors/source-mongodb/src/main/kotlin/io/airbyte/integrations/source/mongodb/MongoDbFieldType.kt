/* Copyright (c) 2026 Airbyte, Inc., all rights reserved. */
package io.airbyte.integrations.source.mongodb

import io.airbyte.cdk.data.AirbyteSchemaType
import io.airbyte.cdk.data.BooleanCodec
import io.airbyte.cdk.data.DoubleCodec
import io.airbyte.cdk.data.JsonEncoder
import io.airbyte.cdk.data.JsonStringCodec
import io.airbyte.cdk.data.LeafAirbyteSchemaType
import io.airbyte.cdk.data.NullCodec
import io.airbyte.cdk.data.TextCodec
import io.airbyte.cdk.discover.FieldType
import io.airbyte.protocol.models.JsonSchemaType

/**
 * MongoDB field types mapped to Airbyte schema types.
 *
 * MongoDB uses BSON types internally. This enum maps BSON type names
 * (as returned by MongoDB's $type operator) to Airbyte schema types.
 *
 * Type mapping matches source-mongodb-v2 behavior:
 * - boolean -> BOOLEAN
 * - int, long, double, decimal -> NUMBER
 * - array -> ARRAY
 * - object, javascriptWithScope -> OBJECT
 * - null -> NULL
 * - Everything else (including dates, strings, objectId) -> STRING
 *
 * Note: For ARRAY and OBJECT types, we store STRING as the airbyteSchemaType
 * (since AirbyteSchemaType is sealed), but provide the correct JsonSchemaType
 * via [jsonSchemaType] for schema generation in [MongoDbAirbyteStreamFactory].
 */
enum class MongoDbFieldType(
    override val airbyteSchemaType: AirbyteSchemaType,
    override val jsonEncoder: JsonEncoder<*>,
    /** The JsonSchemaType to use when building the catalog schema. */
    val jsonSchemaType: JsonSchemaType,
) : FieldType {
    // Boolean type
    BOOLEAN(LeafAirbyteSchemaType.BOOLEAN, BooleanCodec, JsonSchemaType.BOOLEAN),

    // Numeric types - all map to NUMBER to match v2
    NUMBER(LeafAirbyteSchemaType.NUMBER, DoubleCodec, JsonSchemaType.NUMBER),

    // Array type - uses STRING internally but renders as {"type": "array"} via jsonSchemaType
    ARRAY(LeafAirbyteSchemaType.STRING, JsonStringCodec, JsonSchemaType.ARRAY),

    // Object type - uses STRING internally but renders as {"type": "object"} via jsonSchemaType
    OBJECT(LeafAirbyteSchemaType.STRING, JsonStringCodec, JsonSchemaType.OBJECT),

    // Null type
    NULL(LeafAirbyteSchemaType.NULL, NullCodec, JsonSchemaType.NULL),

    // String type - default for everything else (dates, objectId, etc.)
    STRING(LeafAirbyteSchemaType.STRING, TextCodec, JsonSchemaType.STRING),
    ;

    companion object {
        /**
         * Maps a BSON type name (as returned by MongoDB's $type operator)
         * to the corresponding [MongoDbFieldType].
         *
         * Matches source-mongodb-v2 type mapping behavior.
         *
         * @param bsonTypeName The BSON type name from MongoDB
         * @return The corresponding MongoDbFieldType
         */
        fun fromBsonTypeName(bsonTypeName: String): MongoDbFieldType {
            return when (bsonTypeName.lowercase()) {
                "bool", "boolean" -> BOOLEAN
                "int", "long", "double", "decimal" -> NUMBER
                "array" -> ARRAY
                "object", "javascriptwithscope" -> OBJECT
                "null" -> NULL
                // Everything else maps to STRING (including date, timestamp, objectid, string, etc.)
                else -> STRING
            }
        }
    }
}
