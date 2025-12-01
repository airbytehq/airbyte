/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.postgres.cdc

import io.debezium.connector.postgresql.connection.Lsn

data class PostgresSourceCdcPosition(
    val lsn: Lsn,
    val lsnProc: Lsn,
) : Comparable<PostgresSourceCdcPosition> {
    override fun compareTo(other: PostgresSourceCdcPosition): Int =
        compareValuesBy(this, other, { it.lsn }, { it.lsnProc })
}
