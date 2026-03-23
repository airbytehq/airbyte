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
import java.time.OffsetDateTime

object PostgresTimestampTzFieldType :
    SymmetricJdbcFieldType<String>(
        LeafAirbyteSchemaType.TIMESTAMP_WITH_TIMEZONE,
        PgTimestampTzAccessor,
        PgTimestampTzCodec,
    )

// TODO: Improve performance by not stringifying and parsing
object PgTimestampTzCodec : ProtobufAwareCustomConnectorJsonCodec<String> {
    override fun encode(decoded: String): JsonNode = TextNode(decoded)
    override fun decode(encoded: JsonNode): String = encoded.asText()
    override fun valueForProtobufEncoding(v: String): Any? {
        if (v == "Infinity" || v == "-Infinity" || v == "infinity" || v == "-infinity") {
            throw IllegalStateException("Timestamp '$v' is not supported")
        }
        val isBce = v.endsWith(" BC")
        val str = if (isBce) v.removeSuffix(" BC") else v
        val parsed = OffsetDateTime.parse(str)
        return if (isBce) parsed.withYear(1 - parsed.year) else parsed
    }
}

private object PgTimestampTzAccessor : JdbcAccessor<String> {
    override fun get(rs: ResultSet, colIdx: Int): String? {
        val timestampStr = rs.getString(colIdx)
        return when {
            rs.wasNull() -> null
            timestampStr == "infinity" || timestampStr == "-infinity" ->
                throw IllegalStateException("Timestamp '$timestampStr' is not supported")
            else ->
                DateTimeConverter.convertToTimestampWithTimezone(
                    rs.getObject(colIdx, OffsetDateTime::class.java)
                )
        }
    }

    override fun set(stmt: PreparedStatement, paramIdx: Int, value: String) {
        stmt.setString(paramIdx, value)
    }
}
