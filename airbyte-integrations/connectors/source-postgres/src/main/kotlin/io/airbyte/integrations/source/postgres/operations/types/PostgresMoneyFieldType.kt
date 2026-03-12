/* Copyright (c) 2026 Airbyte, Inc., all rights reserved. */
package io.airbyte.integrations.source.postgres.operations.types

import io.airbyte.cdk.data.DoubleCodec
import io.airbyte.cdk.data.LeafAirbyteSchemaType
import io.airbyte.cdk.jdbc.JdbcAccessor
import io.airbyte.cdk.jdbc.SymmetricJdbcFieldType
import java.sql.PreparedStatement
import java.sql.ResultSet

object PostgresMoneyFieldType :
    SymmetricJdbcFieldType<Double>(LeafAirbyteSchemaType.NUMBER, PgMoneyAccessor, DoubleCodec)

private object PgMoneyAccessor : JdbcAccessor<Double> {
    override fun get(rs: ResultSet, colIdx: Int): Double? {
        val moneyStr = rs.getString(colIdx)?.takeUnless { rs.wasNull() } ?: return null
        return moneyStr.replace("[^\\d.-]".toRegex(), "").toDouble()
    }

    override fun set(stmt: PreparedStatement, paramIdx: Int, value: Double) {
        stmt.setDouble(paramIdx, value)
    }
}
