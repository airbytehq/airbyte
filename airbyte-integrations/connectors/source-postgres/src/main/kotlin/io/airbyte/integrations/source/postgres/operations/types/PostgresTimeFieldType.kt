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
import java.time.LocalTime

object PostgresTimeFieldType :
    SymmetricJdbcFieldType<String>(
        LeafAirbyteSchemaType.TIME_WITHOUT_TIMEZONE,
        PgTimeAccessor,
        PgTimeCodec,
    )

// TODO: Improve performance by not stringifying and parsing
object PgTimeCodec : ProtobufAwareCustomConnectorJsonCodec<String> {
    override fun encode(decoded: String): JsonNode = TextNode(decoded)
    override fun decode(encoded: JsonNode): String = encoded.asText()
    override fun valueForProtobufEncoding(v: String): Any? = LocalTime.parse(v)
}

private object PgTimeAccessor : JdbcAccessor<String> {
    override fun get(rs: ResultSet, colIdx: Int): String? {
        val localTime =
            rs.getObject(colIdx, LocalTime::class.java)?.takeUnless { rs.wasNull() } ?: return null
        return DateTimeConverter.convertToTime(localTime)
    }

    override fun set(stmt: PreparedStatement, paramIdx: Int, value: String) {
        stmt.setObject(paramIdx, LocalTime.parse(value))
    }
}
