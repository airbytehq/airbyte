/* Copyright (c) 2026 Airbyte, Inc., all rights reserved. */
package io.airbyte.integrations.source.postgres.operations.types

import io.airbyte.cdk.data.DoubleCodec
import io.airbyte.cdk.data.LeafAirbyteSchemaType
import io.airbyte.cdk.data.TextCodec
import io.airbyte.cdk.jdbc.JdbcAccessor
import io.airbyte.cdk.jdbc.SymmetricJdbcFieldType
import java.sql.PreparedStatement
import java.sql.ResultSet

// Scalar money: encodes as a JSON string. Formats via Double.toString() to match legacy behavior
// (e.g. "-1000.00" -> "-1000.0", "999.99" -> "999.99").
object PostgresMoneyFieldType :
    SymmetricJdbcFieldType<String>(LeafAirbyteSchemaType.NUMBER, PgMoneyAccessor, TextCodec)

private object PgMoneyAccessor : JdbcAccessor<String> {
    override fun get(rs: ResultSet, colIdx: Int): String? {
        val moneyStr = rs.getString(colIdx)?.takeUnless { rs.wasNull() } ?: return null
        val cleaned = moneyStr.replace("[^\\d.-]".toRegex(), "")
        return cleaned.toBigDecimal().toDouble().toString()
    }

    override fun set(stmt: PreparedStatement, paramIdx: Int, value: String) {
        stmt.setString(paramIdx, value)
    }
}

// Array elements for money[]: pgjdbc maps money to Types.DOUBLE but Double.parseDouble() fails
// on money strings with thousands separators (e.g. "$1,001.01"). Use getString() instead and
// strip non-numeric characters manually.
object PostgresMoneyArrayElementFieldType :
    SymmetricJdbcFieldType<Double>(
        LeafAirbyteSchemaType.NUMBER,
        PgMoneyDoubleAccessor,
        DoubleCodec
    )

private object PgMoneyDoubleAccessor : JdbcAccessor<Double> {
    override fun get(rs: ResultSet, colIdx: Int): Double? {
        val moneyStr = rs.getString(colIdx)?.takeUnless { rs.wasNull() } ?: return null
        return moneyStr.replace("[^\\d.-]".toRegex(), "").toDouble()
    }

    override fun set(stmt: PreparedStatement, paramIdx: Int, value: Double) {
        stmt.setDouble(paramIdx, value)
    }
}
