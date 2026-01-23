/* Copyright (c) 2026 Airbyte, Inc., all rights reserved. */
package io.airbyte.integrations.source.mongodb

import io.airbyte.cdk.data.AirbyteSchemaType
import io.airbyte.cdk.data.BooleanCodec
import io.airbyte.cdk.data.DoubleCodec
import io.airbyte.cdk.data.JsonEncoder
import io.airbyte.cdk.data.JsonStringCodec
import io.airbyte.cdk.data.LeafAirbyteSchemaType
import io.airbyte.cdk.data.LongCodec
import io.airbyte.cdk.data.NullCodec
import io.airbyte.cdk.data.OffsetDateTimeCodec
import io.airbyte.cdk.data.TextCodec
import io.airbyte.cdk.discover.FieldType

/**
 * MongoDB field types mapped to Airbyte schema types.
 *
 * MongoDB uses BSON types internally. This enum maps BSON type names
 * (as returned by MongoDB's $type operator) to Airbyte schema types.
 */
enum class MongoDbFieldType(
    override val airbyteSchemaType: AirbyteSchemaType,
    override val jsonEncoder: JsonEncoder<*>,
) : FieldType {
    // String types
    STRING(LeafAirbyteSchemaType.STRING, TextCodec),
    OBJECT_ID(LeafAirbyteSchemaType.STRING, TextCodec),

    // Numeric types
    INT(LeafAirbyteSchemaType.INTEGER, LongCodec),
    LONG(LeafAirbyteSchemaType.INTEGER, LongCodec),
    DOUBLE(LeafAirbyteSchemaType.NUMBER, DoubleCodec),
    DECIMAL(LeafAirbyteSchemaType.NUMBER, DoubleCodec),

    // Boolean type
    BOOLEAN(LeafAirbyteSchemaType.BOOLEAN, BooleanCodec),

    // Date/Time types - represented as strings in ISO format
    DATE(LeafAirbyteSchemaType.TIMESTAMP_WITH_TIMEZONE, OffsetDateTimeCodec),
    TIMESTAMP(LeafAirbyteSchemaType.TIMESTAMP_WITH_TIMEZONE, OffsetDateTimeCodec),

    // Binary type
    BINARY(LeafAirbyteSchemaType.BINARY, TextCodec),

    // Complex types - serialized as JSON
    OBJECT(LeafAirbyteSchemaType.JSONB, JsonStringCodec),
    ARRAY(LeafAirbyteSchemaType.JSONB, JsonStringCodec),

    // Special types
    NULL(LeafAirbyteSchemaType.NULL, NullCodec),
    JAVASCRIPT(LeafAirbyteSchemaType.STRING, TextCodec),
    JAVASCRIPT_WITH_SCOPE(LeafAirbyteSchemaType.JSONB, JsonStringCodec),
    REGEX(LeafAirbyteSchemaType.STRING, TextCodec),
    DB_POINTER(LeafAirbyteSchemaType.STRING, TextCodec),
    SYMBOL(LeafAirbyteSchemaType.STRING, TextCodec),
    MIN_KEY(LeafAirbyteSchemaType.STRING, TextCodec),
    MAX_KEY(LeafAirbyteSchemaType.STRING, TextCodec),
    UNDEFINED(LeafAirbyteSchemaType.NULL, NullCodec),
    ;

    companion object {
        /**
         * Maps a BSON type name (as returned by MongoDB's $type operator)
         * to the corresponding [MongoDbFieldType].
         *
         * @param bsonTypeName The BSON type name from MongoDB
         * @return The corresponding MongoDbFieldType, defaulting to STRING for unknown types
         */
        fun fromBsonTypeName(bsonTypeName: String): MongoDbFieldType {
            return when (bsonTypeName.lowercase()) {
                "string" -> STRING
                "objectid" -> OBJECT_ID
                "int" -> INT
                "long" -> LONG
                "double" -> DOUBLE
                "decimal" -> DECIMAL
                "bool", "boolean" -> BOOLEAN
                "date" -> DATE
                "timestamp" -> TIMESTAMP
                "bindata", "binary" -> BINARY
                "object" -> OBJECT
                "array" -> ARRAY
                "null" -> NULL
                "javascript" -> JAVASCRIPT
                "javascriptwithscope" -> JAVASCRIPT_WITH_SCOPE
                "regex" -> REGEX
                "dbpointer" -> DB_POINTER
                "symbol" -> SYMBOL
                "minkey" -> MIN_KEY
                "maxkey" -> MAX_KEY
                "undefined" -> UNDEFINED
                else -> STRING // Default to STRING for unknown types
            }
        }
    }
}
