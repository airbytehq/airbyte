/* Copyright (c) 2026 Airbyte, Inc., all rights reserved. */
package io.airbyte.integrations.source.postgres.operations.types

import io.airbyte.cdk.data.LeafAirbyteSchemaType
import io.airbyte.cdk.data.TextCodec
import io.airbyte.cdk.jdbc.JdbcAccessor
import io.airbyte.cdk.jdbc.SymmetricJdbcFieldType
import io.airbyte.integrations.source.postgres.cdc.DateTimeConverter
import java.sql.PreparedStatement
import java.sql.ResultSet
import java.time.LocalTime

object PostgresTimeFieldType :
    SymmetricJdbcFieldType<String>(
        LeafAirbyteSchemaType.TIME_WITHOUT_TIMEZONE,
        PgTimeAccessor,
        TextCodec,
    )

private object PgTimeAccessor : JdbcAccessor<String> {
    override fun get(rs: ResultSet, colIdx: Int): String? {
        val localTime =
            rs.getObject(colIdx, LocalTime::class.java)?.takeUnless { rs.wasNull() } ?: return null
        return DateTimeConverter.convertToTime(localTime)
    }

    override fun set(stmt: PreparedStatement, paramIdx: Int, value: String) {
        stmt.setString(paramIdx, value)
    }
}
