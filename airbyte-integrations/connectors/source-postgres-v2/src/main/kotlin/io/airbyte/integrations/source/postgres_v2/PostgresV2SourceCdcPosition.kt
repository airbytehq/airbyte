/* Copyright (c) 2024 Airbyte, Inc., all rights reserved. */
package io.airbyte.integrations.source.postgres_v2

/**
 * WAL position datum for PostgreSQL using LSN (Log Sequence Number).
 *
 * PostgreSQL's LSN is a 64-bit unsigned integer representing a position in the
 * Write-Ahead Log. It's typically displayed as two 32-bit hexadecimal values
 * separated by a slash (e.g., "0/16B3748").
 */
data class PostgresV2SourceCdcPosition(
    val lsn: Long,
) : Comparable<PostgresV2SourceCdcPosition> {

    /**
     * Returns the LSN as a formatted string in PostgreSQL's standard LSN format.
     * For example: "0/16B3748"
     */
    val lsnString: String
        get() {
            val highBits = (lsn shr 32).toInt()
            val lowBits = lsn.toInt()
            return "$highBits/${Integer.toHexString(lowBits).uppercase()}"
        }

    /**
     * The LSN value can be used directly as a cursor value for the purposes of
     * deduping records in incremental syncs.
     */
    val cursorValue: Long
        get() = lsn

    override fun compareTo(other: PostgresV2SourceCdcPosition): Int =
        lsn.compareTo(other.lsn)

    companion object {
        /**
         * Parses an LSN string in PostgreSQL format (e.g., "0/16B3748") into a
         * PostgresV2SourceCdcPosition.
         */
        fun fromLsnString(lsnString: String): PostgresV2SourceCdcPosition {
            val parts = lsnString.split("/")
            require(parts.size == 2) { "Invalid LSN format: $lsnString" }
            val highBits = parts[0].toLong()
            val lowBits = java.lang.Long.parseLong(parts[1], 16)
            val lsn = (highBits shl 32) or lowBits
            return PostgresV2SourceCdcPosition(lsn)
        }

        /**
         * Creates a position from the numeric LSN value.
         */
        fun fromLsn(lsn: Long): PostgresV2SourceCdcPosition =
            PostgresV2SourceCdcPosition(lsn)
    }
}
