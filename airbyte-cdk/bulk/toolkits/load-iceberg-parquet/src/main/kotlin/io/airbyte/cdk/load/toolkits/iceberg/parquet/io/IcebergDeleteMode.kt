/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.toolkits.iceberg.parquet.io

import io.airbyte.cdk.ConfigErrorException
import org.apache.iceberg.HasTableOperations
import org.apache.iceberg.Table
import org.apache.iceberg.TableProperties

/** The delete-file encoding a Dedupe stream writes into an Iceberg table. */
enum class IcebergDeleteMode {
    EQUALITY,
    POSITIONAL,
    DELETION_VECTOR,
}

private const val DEFAULT_FORMAT_VERSION = 2

/**
 * The table's Iceberg format version, preferring live table metadata so that uncommitted-looking
 * properties cannot lie. Falls back to the persisted `format-version` property for table
 * implementations that do not expose [HasTableOperations].
 */
fun tableFormatVersion(table: Table): Int =
    (table as? HasTableOperations)
        ?.operations()
        ?.current()
        ?.formatVersion()
        ?: table.properties()[TableProperties.FORMAT_VERSION]?.toIntOrNull()
            ?: DEFAULT_FORMAT_VERSION

/**
 * Validates that [mode] can be written to [table], which must be a Dedupe target. Throws
 * [ConfigErrorException] naming the table and its format version when it cannot.
 */
fun validateDeleteMode(table: Table, mode: IcebergDeleteMode) {
    val version = tableFormatVersion(table)
    val supported =
        when (mode) {
            IcebergDeleteMode.EQUALITY -> version <= 2
            IcebergDeleteMode.POSITIONAL -> version == 2
            IcebergDeleteMode.DELETION_VECTOR -> version >= 3
        }
    if (!supported) {
        throw ConfigErrorException(
            "Table ${table.name()} has Iceberg format version v$version, which does not support " +
                "delete mode $mode.",
        )
    }
}
