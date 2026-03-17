/* Copyright (c) 2026 Airbyte, Inc., all rights reserved. */
package io.airbyte.integrations.source.postgres.operations.types

import com.fasterxml.jackson.databind.JsonNode
import io.airbyte.cdk.data.JsonCodec
import io.airbyte.cdk.data.LeafAirbyteSchemaType
import io.airbyte.cdk.jdbc.BigDecimalAccessor
import io.airbyte.cdk.jdbc.SymmetricJdbcFieldType
import io.airbyte.cdk.util.Jsons
import java.math.BigDecimal

/**
 * Like [io.airbyte.cdk.jdbc.BigDecimalFieldType] but with a codec that tolerates string values.
 *
 * The Debezium custom converter [PostgresCustomConverter] serializes NUMERIC/DECIMAL column values
 * as strings (via [SchemaBuilder.string]) to preserve precision. The standard [BigDecimalCodec]
 * strictly requires a numeric JSON node and rejects these string values. This codec accepts both
 * numeric and textual JSON nodes.
 */
object PostgresBigDecimalFieldType :
    SymmetricJdbcFieldType<BigDecimal>(
        LeafAirbyteSchemaType.NUMBER,
        BigDecimalAccessor,
        PgBigDecimalCodec,
    )

object PgBigDecimalCodec : JsonCodec<BigDecimal> {
    override fun encode(decoded: BigDecimal): JsonNode = Jsons.numberNode(decoded)

    override fun decode(encoded: JsonNode): BigDecimal {
        if (encoded.isNumber) return encoded.decimalValue()
        if (encoded.isTextual) {
            try {
                return BigDecimal(encoded.textValue())
            } catch (e: NumberFormatException) {
                throw IllegalArgumentException("invalid number value $encoded", e)
            }
        }
        throw IllegalArgumentException("invalid number value $encoded")
    }
}
