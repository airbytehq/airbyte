/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.postgres.write.transform

import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.dataflow.transform.ColumnNameMapper
import io.airbyte.cdk.load.orchestration.db.legacy_typing_deduping.TableCatalog
import io.airbyte.integrations.destination.postgres.spec.PostgresConfiguration
import jakarta.inject.Singleton

@Singleton
class PostgresColumnNameMapper(
    private val catalogInfo: TableCatalog,
    private val postgresConfiguration: PostgresConfiguration,
) : ColumnNameMapper {
    override fun getMappedColumnName(stream: DestinationStream, columnName: String): String {
        if (postgresConfiguration.legacyRawTablesOnly == true) {
            return columnName
        } else {
            return catalogInfo.getMappedColumnName(stream, columnName)!!
        }
    }
}
