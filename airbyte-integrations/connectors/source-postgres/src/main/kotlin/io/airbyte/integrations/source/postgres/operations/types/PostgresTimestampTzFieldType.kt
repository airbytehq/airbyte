/* Copyright (c) 2026 Airbyte, Inc., all rights reserved. */
package io.airbyte.integrations.source.postgres.operations.types

import io.airbyte.cdk.data.LeafAirbyteSchemaType
import io.airbyte.cdk.data.TextCodec
import io.airbyte.cdk.jdbc.JdbcAccessor
import io.airbyte.cdk.jdbc.SymmetricJdbcFieldType
import io.airbyte.integrations.source.postgres.cdc.DateTimeConverter
import java.sql.PreparedStatement
import java.sql.ResultSet
import java.time.OffsetDateTime

object PostgresTimestampTzFieldType :
    SymmetricJdbcFieldType<String>(
        LeafAirbyteSchemaType.TIMESTAMP_WITH_TIMEZONE,
        PgTimestampTzAccessor,
        TextCodec,
    )

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
