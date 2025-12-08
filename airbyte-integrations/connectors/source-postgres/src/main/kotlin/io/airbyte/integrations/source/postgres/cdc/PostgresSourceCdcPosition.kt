/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.postgres.cdc

import io.debezium.connector.postgresql.connection.Lsn

data class PostgresSourceCdcPosition(
    val lsn: Lsn?, // For decorating records with _ab_cdc_lsn.
    val lsnCommit: Lsn?, // For determining when target LSN is reached.
) : Comparable<PostgresSourceCdcPosition> {
    // See https://github.com/airbytehq/airbyte/pull/35939.
    override fun compareTo(other: PostgresSourceCdcPosition): Int =
        if (lsnCommit == null || other.lsnCommit == null) 1
        else lsnCommit.compareTo(other.lsnCommit)
}
