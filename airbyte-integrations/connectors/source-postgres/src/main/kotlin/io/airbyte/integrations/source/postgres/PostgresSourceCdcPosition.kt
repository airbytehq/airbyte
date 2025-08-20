package io.airbyte.integrations.source.postgres

data class PostgresSourceCdcPosition(val fileName: String, val position: Long) : Comparable<PostgresSourceCdcPosition> {
    override fun compareTo(other: PostgresSourceCdcPosition): Int {
        // TODO implement comparison logic based on actual CDC position attributes
        return 0
    }
}
