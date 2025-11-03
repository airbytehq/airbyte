package io.airbyte.integrations.destination.gcs_data_lake.catalog

import io.airbyte.cdk.load.orchestration.db.ColumnNameGenerator
import jakarta.inject.Singleton

@Singleton
class GcsDataLakeColumnNameGenerator :
    ColumnNameGenerator {
    override fun getColumnName(column: String): ColumnNameGenerator.ColumnName {
        return ColumnNameGenerator.ColumnName(
            column,
            column,
        )
    }
}
