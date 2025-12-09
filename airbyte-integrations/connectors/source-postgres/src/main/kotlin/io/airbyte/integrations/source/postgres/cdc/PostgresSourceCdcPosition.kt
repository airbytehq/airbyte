/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.postgres.cdc

import io.debezium.connector.postgresql.connection.Lsn

data class PostgresSourceCdcPosition(
    val lsn: Lsn?, // For decorating records with _ab_cdc_lsn.
    val lsnCommit: Lsn?, // For determining when target LSN is reached.
) : Comparable<PostgresSourceCdcPosition> {
    override fun compareTo(other: PostgresSourceCdcPosition): Int {
        if (this == other) return 0
        // This breaks the contract of compareTo because it does not provide a consistent ordering:
        // For a and b such that a.lsnCommit == null, b.lsnCommit == null, and a.lsn != b.lsn,
        // a.compareTo(b) = 1 and b.compareTo(a) = 1.
        // The intent here is to duplicate the logic in the previous version of the connector, where
        // we do not terminate a sync based on a comparison of offsets without a lsn_commit.
        // See https://github.com/airbytehq/airbyte/pull/35939.
        if (lsnCommit == null || other.lsnCommit == null) return 1
        return lsnCommit.compareTo(other.lsnCommit)
    }
}
