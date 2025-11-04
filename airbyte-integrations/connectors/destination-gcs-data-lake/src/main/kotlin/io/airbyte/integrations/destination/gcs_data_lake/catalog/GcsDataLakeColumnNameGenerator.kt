/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.gcs_data_lake.catalog

import io.airbyte.cdk.load.data.Transformations
import io.airbyte.cdk.load.orchestration.db.ColumnNameGenerator
import jakarta.inject.Singleton

/**
 * Generates BigLake-compatible column names for GCS Data Lake tables.
 *
 * BigLake external tables have strict naming requirements:
 * - Only alphanumeric characters (a-z, A-Z, 0-9) and underscores (_)
 * - Must start with a letter or underscore
 *
 * This implementation uses [Transformations.toAlphanumericAndUnderscore] to ensure all column names
 * meet these requirements.
 */
@Singleton
class GcsDataLakeColumnNameGenerator : ColumnNameGenerator {
    override fun getColumnName(column: String): ColumnNameGenerator.ColumnName {
        val sanitized = Transformations.toAlphanumericAndUnderscore(column)
        return ColumnNameGenerator.ColumnName(
            displayName = sanitized,
            canonicalName = sanitized,
        )
    }
}
