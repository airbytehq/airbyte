/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.cdk.db

import com.google.common.base.Preconditions
import io.airbyte.cdk.db.jdbc.JdbcDatabase
import io.airbyte.cdk.db.jdbc.JdbcUtils
import java.sql.Connection
import java.sql.ResultSet
import java.sql.SQLException

object PostgresUtils {
    @JvmStatic
    @Throws(SQLException::class)
    fun getLsn(database: JdbcDatabase): PgLsn {
        // pg version >= 10. For versions < 10 use query select * from pg_current_xlog_location()
        val jsonNodes =
            database.bufferedResultSetQuery(
                { conn: Connection ->
                    conn.createStatement().executeQuery("select * from pg_current_wal_lsn()")
                },
                { resultSet: ResultSet -> JdbcUtils.defaultSourceOperations.rowToJson(resultSet) }
            )

        Preconditions.checkState(jsonNodes.size == 1)
        return PgLsn.Companion.fromPgString(jsonNodes[0]["pg_current_wal_lsn"].asText())
    }
}
