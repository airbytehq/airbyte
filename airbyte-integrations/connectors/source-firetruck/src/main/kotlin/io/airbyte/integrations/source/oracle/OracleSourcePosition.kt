/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.oracle

/** Represents a position in the Oracle database's write-ahead log. */
data class OracleSourcePosition(val scn: Long) : Comparable<OracleSourcePosition> {

    override fun compareTo(other: OracleSourcePosition): Int {
        return scn.compareTo(other.scn)
    }
}
