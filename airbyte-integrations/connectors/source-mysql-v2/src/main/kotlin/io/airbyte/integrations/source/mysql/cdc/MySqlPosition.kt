/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.mysql.cdc

/** WAL position datum for MySQL. */
data class MySqlPosition(val fileName: String, val position: Long) : Comparable<MySqlPosition> {

    override fun compareTo(other: MySqlPosition): Int {
        val fileNameDelta: Int = fileName.compareTo(other.fileName)
        if (fileNameDelta != 0) {
            return fileNameDelta
        }
        return position.compareTo(other.position)
    }
}
