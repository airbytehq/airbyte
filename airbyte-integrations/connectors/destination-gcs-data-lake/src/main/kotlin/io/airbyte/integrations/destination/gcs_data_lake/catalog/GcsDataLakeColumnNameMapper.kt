/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.gcs_data_lake.catalog

import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.dataflow.transform.ColumnNameMapper
import io.airbyte.cdk.load.orchestration.db.legacy_typing_deduping.TableCatalog
import jakarta.inject.Singleton

/**
 * Maps column names from the source schema to BigLake-compatible names.
 *
 * This mapper delegates to the [TableCatalog] which was pre-computed during initialization using
 * [GcsDataLakeColumnNameGenerator]. The catalog handles:
 * - Column name sanitization
 * - Collision detection and resolution (adding _1, _2 suffixes)
 * - Consistent mapping across the entire sync
 */
@Singleton
class GcsDataLakeColumnNameMapper(private val catalogInfo: TableCatalog) : ColumnNameMapper {
    override fun getMappedColumnName(stream: DestinationStream, columnName: String): String {
        return catalogInfo.getMappedColumnName(stream, columnName)
            ?: throw IllegalStateException(
                "Column name '$columnName' not found in catalog for stream ${stream.mappedDescriptor}"
            )
    }
}
