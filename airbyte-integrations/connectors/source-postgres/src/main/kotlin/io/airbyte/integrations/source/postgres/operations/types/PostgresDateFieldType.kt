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
import java.time.LocalDate

object PostgresDateFieldType :
    SymmetricJdbcFieldType<String>(LeafAirbyteSchemaType.DATE, PgDateAccessor, PgDateCodec)

// TODO: Improve performance by not stringifying and parsing
object PgDateCodec : ProtobufAwareCustomConnectorJsonCodec<String> {
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
        val parsed = LocalDate.parse(str, DateTimeConverter.DATE_FORMATTER)
        return if (isBce) parsed.withYear(1 - parsed.year) else parsed
    }
}

private object PgDateAccessor : JdbcAccessor<String> {
    override fun get(rs: ResultSet, colIdx: Int): String? {
        val dateStr = rs.getString(colIdx)
        return when {
            rs.wasNull() -> null
            dateStr == "infinity" || dateStr == "-infinity" ->
                throw IllegalStateException("Date '$dateStr' is not supported")
            else -> DateTimeConverter.convertToDate(rs.getDate(colIdx))
        }
    }

    override fun set(stmt: PreparedStatement, paramIdx: Int, value: String) {
        val isBce = value.endsWith(" BC")
        val str = if (isBce) value.removeSuffix(" BC") else value
        val parsed = LocalDate.parse(str, DateTimeConverter.DATE_FORMATTER)
        stmt.setObject(paramIdx, if (isBce) parsed.withYear(1 - parsed.year) else parsed)
    }
}
