/* Copyright (c) 2026 Airbyte, Inc., all rights reserved. */
package io.airbyte.integrations.source.postgres.operations.types

import io.airbyte.cdk.data.LeafAirbyteSchemaType
import io.airbyte.cdk.data.TextCodec
import io.airbyte.cdk.jdbc.JdbcAccessor
import io.airbyte.cdk.jdbc.SymmetricJdbcFieldType
import io.airbyte.integrations.source.postgres.cdc.DateTimeConverter
import java.sql.PreparedStatement
import java.sql.ResultSet
import java.time.OffsetTime

object PostgresTimeTzFieldType :
    SymmetricJdbcFieldType<String>(
        LeafAirbyteSchemaType.TIME_WITH_TIMEZONE,
        PgTimeTzAccessor,
        TextCodec,
    )

private object PgTimeTzAccessor : JdbcAccessor<String> {
    override fun get(rs: ResultSet, colIdx: Int): String? {
        val offsetTime =
            rs.getObject(colIdx, OffsetTime::class.java)?.takeUnless { rs.wasNull() } ?: return null
        return DateTimeConverter.convertToTimeWithTimezone(offsetTime)
    }

    override fun set(stmt: PreparedStatement, paramIdx: Int, value: String) {
        stmt.setString(paramIdx, value)
    }
}
