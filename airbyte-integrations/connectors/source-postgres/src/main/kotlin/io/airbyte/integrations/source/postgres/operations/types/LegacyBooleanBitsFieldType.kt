/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.postgres.operations.types

import io.airbyte.cdk.data.BooleanCodec
import io.airbyte.cdk.data.LeafAirbyteSchemaType
import io.airbyte.cdk.jdbc.JdbcAccessor
import io.airbyte.cdk.jdbc.SymmetricJdbcFieldType
import java.sql.PreparedStatement
import java.sql.ResultSet

// TODO: Legacy mapping only maps "1" to true, all else are false
object LegacyBooleanBitsFieldType :
    SymmetricJdbcFieldType<Boolean>(
        LeafAirbyteSchemaType.BOOLEAN,
        LegacyBooleanBitsAccessor,
        BooleanCodec,
    )

object LegacyBooleanBitsAccessor : JdbcAccessor<Boolean> {
    override fun get(rs: ResultSet, colIdx: Int): Boolean? {
        val str = rs.getString(colIdx) ?: return null
        // Legacy: only "1" maps to true, all other bit strings map to false
        return str == "1"
    }

    override fun set(stmt: PreparedStatement, paramIdx: Int, value: Boolean) {
        stmt.setString(paramIdx, if (value) "1" else "0")
    }
}
