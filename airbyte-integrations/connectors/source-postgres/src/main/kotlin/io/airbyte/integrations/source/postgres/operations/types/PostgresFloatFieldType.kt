/* Copyright (c) 2026 Airbyte, Inc., all rights reserved. */
package io.airbyte.integrations.source.postgres.operations.types

import com.fasterxml.jackson.databind.JsonNode
import io.airbyte.cdk.data.JsonCodec
import io.airbyte.cdk.data.LeafAirbyteSchemaType
import io.airbyte.cdk.jdbc.JdbcAccessor
import io.airbyte.cdk.jdbc.SymmetricJdbcFieldType
import io.airbyte.cdk.util.Jsons
import java.sql.PreparedStatement
import java.sql.ResultSet

// Postgres real permits Infinity, -Infinity, and NaN. Downstream destinations expect only JSON
// numbers. On these values, the accessor throws during JDBC read (recording
// RETRIEVAL_FAILURE_TOTAL in record metadata), and the codec throws during CDC decode (recording
// DESERIALIZATION_FAILURE_TOTAL). The value is then nulled in the emitted record.
object PostgresFloatFieldType :
    SymmetricJdbcFieldType<Float>(
        LeafAirbyteSchemaType.NUMBER,
        FiniteFloatAccessor,
        FiniteFloatCodec,
    )

object FiniteFloatCodec : JsonCodec<Float> {
    override fun encode(decoded: Float): JsonNode = Jsons.numberNode(decoded)

    override fun decode(encoded: JsonNode): Float {
        if (!encoded.isNumber) {
            throw IllegalArgumentException("non-numeric value $encoded is unsupported")
        }
        val decoded: Float = encoded.floatValue()
        if (!decoded.isFinite()) {
            throw IllegalArgumentException("non-finite value $decoded is unsupported")
        }
        if (encode(decoded).doubleValue().compareTo(encoded.doubleValue()) != 0) {
            throw IllegalArgumentException(
                "invalid IEEE-754 32-bit floating point value $encoded (type ${encoded.javaClass.canonicalName})"
            )
        }
        return decoded
    }
}

private object FiniteFloatAccessor : JdbcAccessor<Float> {
    override fun get(rs: ResultSet, colIdx: Int): Float? {
        val value = rs.getFloat(colIdx)
        if (rs.wasNull()) return null
        if (!value.isFinite()) {
            throw IllegalStateException("non-finite value $value is unsupported")
        }
        return value
    }

    override fun set(stmt: PreparedStatement, paramIdx: Int, value: Float) {
        stmt.setFloat(paramIdx, value)
    }
}
