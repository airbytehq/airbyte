/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.postgres.cdc

import io.airbyte.cdk.read.cdc.PartiallyOrdered
import io.debezium.connector.postgresql.connection.Lsn

data class PostgresSourceCdcPosition(
    // See this article for an explanation of the difference between lsn_commit and lsn:
    // https://www.morling.dev/blog/postgres-replication-slots-confirmed-flush-lsn-vs-restart-lsn/
    val lsnCommit: Lsn?,
    val lsn: Lsn?, // For decorating records with _ab_cdc_lsn. Maybe lsnCommit would be more useful?
) : PartiallyOrdered<PostgresSourceCdcPosition> {
    // See https://github.com/airbytehq/airbyte/pull/35939.
    // Partial ordering by (lsnCommit, lsn). Null if indeterminate.
    override fun compareTo(other: PostgresSourceCdcPosition): Int? {
        if (this == other) return 0
        if (lsnCommit == null || other.lsnCommit == null) return null
        val commitDiff = lsnCommit.compareTo(other.lsnCommit)
        if (commitDiff != 0) return commitDiff
        return if (lsn == null || other.lsn == null) {
            null
        } else {
            lsn.compareTo(other.lsn)
        }
    }
}
