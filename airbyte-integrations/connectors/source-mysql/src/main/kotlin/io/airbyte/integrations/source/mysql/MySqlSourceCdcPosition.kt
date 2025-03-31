/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.mysql

import kotlin.io.path.Path
import kotlin.io.path.extension

/** WAL position datum for MySQL. */
data class MySqlSourceCdcPosition(val fileName: String, val position: Long) :
    Comparable<MySqlSourceCdcPosition> {

    /**
     * Numerical value encoded in the extension of the binlog file name.
     *
     * These files are typically named `binlog.000002` or something like that. These file's sizes
     * are, according to the documentation, capped at 1 GB.
     */
    val fileExtension: Int
        get() = Path(fileName).extension.toInt()

    /**
     * Numerical value obtained by ORing [fileExtension] in the high bits of [position]. This
     * unsigned long integer can be used as a cursor value for the purposes of deduping records in
     * incremental syncs; its value is meaningless in and of itself, all that matters is that it is
     * monotonically increasing from one record to the next within the same sync.
     *
     * Specifically, deduplication will group all records by (_ab_cdc_updated_at, emitted_at) and
     * will pick the record with the latest cursor value and discard the rest.
     */
    val cursorValue: Long
        get() = (fileExtension.toLong() shl Int.SIZE_BITS) or position

    override fun compareTo(other: MySqlSourceCdcPosition): Int =
        cursorValue.compareTo(other.cursorValue)
}
