/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.postgres.cdc

import io.airbyte.cdk.read.querySingleValue
import io.airbyte.integrations.source.postgres.PostgresSourceJdbcConnectionFactory
import io.debezium.connector.postgresql.connection.Lsn
import jakarta.inject.Singleton
import java.time.Instant

@Singleton
class StartupState(connectionFactory: PostgresSourceJdbcConnectionFactory) {
    val txId: Long
    val lsn: Long
    val time: Instant

    init {
        val (txId, lsn, time) =
            querySingleValue(
                connectionFactory,
                """
                SELECT
                    CASE WHEN pg_is_in_recovery()
                        THEN txid_snapshot_xmin(txid_current_snapshot())
                        ELSE txid_current()
                    END AS txid,
                    CASE WHEN pg_is_in_recovery()
                        THEN pg_last_wal_receive_lsn()
                        ELSE pg_current_wal_lsn()
                    END AS lsn,
                    CURRENT_TIMESTAMP AS time
            """.trimIndent(),
                withResultSet = { rs ->
                    Triple(
                        rs.getLong("txid"),
                        Lsn.valueOf(rs.getString("lsn")).asLong(),
                        rs.getTimestamp("time").toInstant(),
                    )
                }
            )
        this.txId = txId
        this.lsn = lsn
        this.time = time
    }
}
