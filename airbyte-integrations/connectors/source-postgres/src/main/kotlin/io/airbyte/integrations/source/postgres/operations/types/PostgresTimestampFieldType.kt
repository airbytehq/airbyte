/* Copyright (c) 2026 Airbyte, Inc., all rights reserved. */
package io.airbyte.integrations.source.postgres.operations.types

import com.fasterxml.jackson.databind.JsonNode
import com.fasterxml.jackson.databind.node.TextNode
import io.airbyte.cdk.data.LeafAirbyteSchemaType
import io.airbyte.cdk.jdbc.JdbcAccessor
import io.airbyte.cdk.jdbc.SymmetricJdbcFieldType
import io.airbyte.cdk.output.sockets.ProtobufAwareCustomConnectorJsonCodec
import java.sql.PreparedStatement
import java.sql.ResultSet
import java.time.LocalDateTime

object PostgresTimestampFieldType :
    SymmetricJdbcFieldType<String>(
        LeafAirbyteSchemaType.TIMESTAMP_WITHOUT_TIMEZONE,
        PgTimestampAccessor,
        PgTimestampCodec,
    )

// TODO: Improve performance by not stringifying and parsing
object PgTimestampCodec : ProtobufAwareCustomConnectorJsonCodec<String> {
    override fun encode(decoded: String): JsonNode = TextNode(decoded)
    override fun decode(encoded: JsonNode): String {
        val decoded = encoded.asText()
        if (
            decoded.equals("infinity", ignoreCase = true) ||
                decoded.equals("-infinity", ignoreCase = true)
        ) {
            throw IllegalArgumentException("value $decoded is unsupported")
        }
        return decoded
    }
    override fun valueForProtobufEncoding(v: String): Any? {
        val isBce = v.endsWith(" BC")
        val str = if (isBce) v.removeSuffix(" BC") else v
        val parsed = LocalDateTime.parse(str)
        return if (isBce) parsed.withYear(1 - parsed.year) else parsed
    }
}

private object PgTimestampAccessor : JdbcAccessor<String> {
    override fun get(rs: ResultSet, colIdx: Int): String? {
        val timestampStr = rs.getString(colIdx)
        return when {
            rs.wasNull() -> null
            timestampStr == "infinity" || timestampStr == "-infinity" ->
                throw IllegalStateException("Timestamp '$timestampStr' is not supported")
            else -> DateTimeConverter.convertToTimestamp(rs.getTimestamp(colIdx))
        }
    }

    override fun set(stmt: PreparedStatement, paramIdx: Int, value: String) {
        val isBce = value.endsWith(" BC")
        val str = if (isBce) value.removeSuffix(" BC") else value
        val parsed = LocalDateTime.parse(str)
        stmt.setObject(paramIdx, if (isBce) parsed.withYear(1 - parsed.year) else parsed)
    }
}
