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
class StartupState(private val connectionFactory: PostgresSourceJdbcConnectionFactory) {

    /**
     * Lazily queries the current WAL position and transaction state. The query is deferred until
     * first access so that non-CDC connections never execute WAL-level SQL that requires
     * wal_level = logical.
     */
    private val data: Triple<Long, Long, Instant> by lazy {
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
            """
                .trimIndent(),
            withResultSet = { rs ->
                Triple(
                    rs.getLong("txid"),
                    Lsn.valueOf(rs.getString("lsn")).asLong(),
                    rs.getTimestamp("time").toInstant(),
                )
            }
        )
    }

    val txId: Long
        get() = data.first

    val lsn: Long
        get() = data.second

    val time: Instant
        get() = data.third
}
