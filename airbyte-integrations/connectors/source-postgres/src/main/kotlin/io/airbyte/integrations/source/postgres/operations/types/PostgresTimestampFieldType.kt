/* Copyright (c) 2026 Airbyte, Inc., all rights reserved. */
package io.airbyte.integrations.source.postgres.operations.types

import io.airbyte.cdk.data.LeafAirbyteSchemaType
import io.airbyte.cdk.data.TextCodec
import io.airbyte.cdk.jdbc.JdbcAccessor
import io.airbyte.cdk.jdbc.SymmetricJdbcFieldType
import io.airbyte.integrations.source.postgres.cdc.DateTimeConverter
import java.sql.PreparedStatement
import java.sql.ResultSet

object PostgresTimestampFieldType :
    SymmetricJdbcFieldType<String>(
        LeafAirbyteSchemaType.TIMESTAMP_WITHOUT_TIMEZONE,
        PgTimestampAccessor,
        TextCodec,
    )

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
        stmt.setString(paramIdx, value)
    }
}
