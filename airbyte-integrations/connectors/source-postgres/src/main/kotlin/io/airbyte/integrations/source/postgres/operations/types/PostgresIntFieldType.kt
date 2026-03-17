/* Copyright (c) 2026 Airbyte, Inc., all rights reserved. */
package io.airbyte.integrations.source.postgres.operations.types

import com.fasterxml.jackson.databind.JsonNode
import io.airbyte.cdk.data.JsonCodec
import io.airbyte.cdk.data.LeafAirbyteSchemaType
import io.airbyte.cdk.jdbc.IntAccessor
import io.airbyte.cdk.jdbc.SymmetricJdbcFieldType
import io.airbyte.cdk.util.Jsons

/**
 * Like [io.airbyte.cdk.jdbc.IntFieldType] but with a codec that tolerates string values.
 *
 * The Debezium custom converter [PostgresCustomConverter] serializes NUMERIC/DECIMAL column values
 * as strings (via [SchemaBuilder.string]) to preserve precision. The standard [IntCodec] strictly
 * requires a numeric JSON node and rejects these string values. This codec accepts both numeric and
 * textual JSON nodes.
 *
 * Used for NUMERIC(p, 0) columns where precision is known and scale is zero (integer semantics).
 */
object PostgresIntFieldType :
    SymmetricJdbcFieldType<Int>(
        LeafAirbyteSchemaType.INTEGER,
        IntAccessor,
        PgIntCodec,
    )

object PgIntCodec : JsonCodec<Int> {
    override fun encode(decoded: Int): JsonNode = Jsons.numberNode(decoded)

    override fun decode(encoded: JsonNode): Int {
        if (encoded.isNumber) {
            if (!encoded.canConvertToExactIntegral()) {
                throw IllegalArgumentException("invalid integral value $encoded")
            }
            if (!encoded.canConvertToInt()) {
                throw IllegalArgumentException("invalid 32-bit integer value $encoded")
            }
            return encoded.intValue()
        }
        if (encoded.isTextual) {
            try {
                return encoded.textValue().toInt()
            } catch (e: NumberFormatException) {
                throw IllegalArgumentException("invalid integer value $encoded", e)
            }
        }
        throw IllegalArgumentException("invalid integer value $encoded")
    }
}
