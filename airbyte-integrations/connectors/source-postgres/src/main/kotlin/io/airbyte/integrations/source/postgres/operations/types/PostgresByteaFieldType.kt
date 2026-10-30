/* Copyright (c) 2026 Airbyte, Inc., all rights reserved. */
package io.airbyte.integrations.source.postgres.operations.types

import io.airbyte.cdk.data.LeafAirbyteSchemaType
import io.airbyte.cdk.data.TextCodec
import io.airbyte.cdk.jdbc.JdbcAccessor
import io.airbyte.cdk.jdbc.SymmetricJdbcFieldType
import java.sql.PreparedStatement
import java.sql.ResultSet
import java.util.Base64

object PostgresByteaFieldType :
    SymmetricJdbcFieldType<String>(LeafAirbyteSchemaType.STRING, PgByteaAccessor, TextCodec)

private object PgByteaAccessor : JdbcAccessor<String> {
    override fun get(rs: ResultSet, colIdx: Int): String? {
        val bytes = rs.getBytes(colIdx)?.takeUnless { rs.wasNull() } ?: return null
        return Base64.getEncoder().encodeToString(bytes)
    }

    override fun set(stmt: PreparedStatement, paramIdx: Int, value: String) {
        stmt.setBytes(paramIdx, Base64.getDecoder().decode(value))
    }
}
