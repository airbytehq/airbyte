/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.snowflake.db

import io.airbyte.cdk.load.orchestration.db.ColumnNameGenerator
import jakarta.inject.Singleton
import java.util.Locale

@Singleton
class SnowflakeColumnNameGenerator : ColumnNameGenerator {
    override fun getColumnName(column: String): ColumnNameGenerator.ColumnName {
        return ColumnNameGenerator.ColumnName(
            displayName = column,
            canonicalName = column.lowercase(Locale.getDefault()),
        )
    }
}
