/* Copyright (c) 2026 Airbyte, Inc., all rights reserved. */
package io.airbyte.integrations.source.postgres.operations.types

import io.airbyte.cdk.data.LeafAirbyteSchemaType
import io.airbyte.cdk.data.TextCodec
import io.airbyte.cdk.jdbc.JdbcAccessor
import io.airbyte.cdk.jdbc.SymmetricJdbcFieldType
import io.airbyte.integrations.source.postgres.cdc.DateTimeConverter
import java.sql.PreparedStatement
import java.sql.ResultSet

object PostgresDateFieldType :
    SymmetricJdbcFieldType<String>(LeafAirbyteSchemaType.DATE, PgDateAccessor, TextCodec)

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
        stmt.setString(paramIdx, value)
    }
}
