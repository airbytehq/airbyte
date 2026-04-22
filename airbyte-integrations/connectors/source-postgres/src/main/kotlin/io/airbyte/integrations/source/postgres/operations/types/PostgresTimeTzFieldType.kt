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
import java.time.OffsetTime

object PostgresTimeTzFieldType :
    SymmetricJdbcFieldType<String>(
        LeafAirbyteSchemaType.TIME_WITH_TIMEZONE,
        PgTimeTzAccessor,
        PgTimeTzCodec,
    )

// TODO: Improve performance by not stringifying and parsing
object PgTimeTzCodec : ProtobufAwareCustomConnectorJsonCodec<String> {
    override fun encode(decoded: String): JsonNode = TextNode(decoded)
    override fun decode(encoded: JsonNode): String = encoded.asText()
    override fun valueForProtobufEncoding(v: String): Any? = OffsetTime.parse(v)
}

private object PgTimeTzAccessor : JdbcAccessor<String> {
    override fun get(rs: ResultSet, colIdx: Int): String? {
        val offsetTime =
            rs.getObject(colIdx, OffsetTime::class.java)?.takeUnless { rs.wasNull() } ?: return null
        return DateTimeConverter.convertToTimeWithTimezone(offsetTime)
    }

    override fun set(stmt: PreparedStatement, paramIdx: Int, value: String) {
        stmt.setObject(paramIdx, OffsetTime.parse(value))
    }
}
