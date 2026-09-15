/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.toolkits.iceberg.parquet.io

import java.util.concurrent.ConcurrentHashMap
import java.util.concurrent.atomic.AtomicBoolean
import java.util.concurrent.atomic.AtomicInteger
import java.util.concurrent.atomic.AtomicLong
import org.apache.iceberg.DataFile
import org.apache.iceberg.deletes.PositionDeleteIndex

/**
 * Stream-scoped state shared by positional writers created for successive flushes.
 *
 * [deleteIndexEnabled] turns on the deletion-vector index described by [DeleteIndexStatistics],
 * which lets a flush learn the already-deleted positions of a data file without reading its prior
 * delete files.
 */
class PositionalDeleteResolutionState(deleteIndexEnabled: Boolean = false) {
    val deleteIndex = DeleteIndexState(enabled = deleteIndexEnabled)

    internal val warningLogged = AtomicBoolean(false)
    internal val dataFilesOpened = AtomicInteger(0)
    internal val rowsScanned = AtomicLong(0)
    internal val fullySupersededDataFiles: MutableSet<DataFile> = ConcurrentHashMap.newKeySet()
    internal val positionDeleteIndexes =
        ConcurrentHashMap<String, Map<String, PositionDeleteIndex>>()
    internal val unreadablePositionDeleteFiles = ConcurrentHashMap.newKeySet<String>()
    internal val positionDeleteFilesRead = AtomicInteger(0)
}
