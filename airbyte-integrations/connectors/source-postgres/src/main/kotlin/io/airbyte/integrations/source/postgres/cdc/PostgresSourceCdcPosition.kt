/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.postgres.cdc

import io.airbyte.cdk.read.cdc.PartiallyOrdered
import io.debezium.connector.postgresql.connection.Lsn

data class PostgresSourceCdcPosition(
    // See this article for an explanation of the difference between lsn and lsn_commit:
    // https://www.morling.dev/blog/postgres-replication-slots-confirmed-flush-lsn-vs-restart-lsn/
    val lsn: Lsn?, // For decorating records with _ab_cdc_lsn.
    val lsnCommit: Lsn?, // For determining when target LSN is reached.
) : PartiallyOrdered<PostgresSourceCdcPosition> {
    // See https://github.com/airbytehq/airbyte/pull/35939.
    override fun compareTo(other: PostgresSourceCdcPosition): Int? {
        if (this == other) return 0
        if (lsnCommit == null || other.lsnCommit == null) return null
        return lsnCommit.compareTo(other.lsnCommit)
    }
}
