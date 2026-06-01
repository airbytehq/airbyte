/* Copyright (c) 2026 Airbyte, Inc., all rights reserved. */
package io.airbyte.integrations.source.postgres.operations.types

import io.airbyte.cdk.data.LeafAirbyteSchemaType
import io.airbyte.cdk.data.TextCodec
import io.airbyte.cdk.jdbc.JdbcAccessor
import io.airbyte.cdk.jdbc.SymmetricJdbcFieldType
import java.sql.PreparedStatement
import java.sql.ResultSet
import java.util.UUID

object PostgresUuidFieldType :
    SymmetricJdbcFieldType<String>(
        LeafAirbyteSchemaType.STRING,
        PgUuidAccessor,
        TextCodec,
    )

private object PgUuidAccessor : JdbcAccessor<String> {
    override fun get(rs: ResultSet, colIdx: Int): String? =
        rs.getString(colIdx)?.takeUnless { rs.wasNull() }

    override fun set(stmt: PreparedStatement, paramIdx: Int, value: String) {
        stmt.setObject(paramIdx, UUID.fromString(value))
    }
}
