/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.orchestration.db.legacy_typing_deduping

import io.airbyte.cdk.load.command.DestinationCatalog
import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.orchestration.db.ColumnNameGenerator
import io.airbyte.cdk.load.orchestration.db.ColumnNameMapping
import io.airbyte.cdk.load.orchestration.db.FinalTableNameGenerator
import io.airbyte.cdk.load.orchestration.db.RawTableNameGenerator
import io.airbyte.cdk.load.orchestration.db.TableNames
import io.micronaut.context.annotation.Factory
import javax.inject.Singleton

data class TableNameInfo(val tableNames: TableNames, val columnNameMapping: ColumnNameMapping)

data class TableCatalog(private val catalog: Map<DestinationStream, TableNameInfo>) :
    Map<DestinationStream, TableNameInfo> by catalog

data class TableCatalogByDescriptor(
    private val catalog: Map<DestinationStream.Descriptor, TableNameInfo>
) : Map<DestinationStream.Descriptor, TableNameInfo> by catalog

@Factory
class TableCatalogFactory(
    private val catalog: DestinationCatalog,
    private val rawTableNameGenerator: RawTableNameGenerator,
    private val finalTableNameGenerator: FinalTableNameGenerator,
    private val finalTableColumnNameGenerator: ColumnNameGenerator,
) {
    @Singleton
    fun get(): TableCatalog {
        // TODO handle collisions in table names
        return TableCatalog(
            catalog.streams.associateWith { stream ->
                TableNameInfo(
                    TableNames(
                        rawTableName = rawTableNameGenerator.getTableName(stream.descriptor),
                        finalTableName = finalTableNameGenerator.getTableName(stream.descriptor),
                    ),
                    ColumnNameMapping(
                        // TODO handle collisions in column names
                        stream.schema.asColumns().mapValues { (columnName, _) ->
                            finalTableColumnNameGenerator.getColumnName(columnName).displayName
                        }
                    )
                )
            }
        )
    }
}

@Factory
class TableCatalogByDescriptorFactory(
    private val map: TableCatalog,
) {
    @Singleton
    fun get(): TableCatalogByDescriptor {
        return TableCatalogByDescriptor(map.mapKeys { (k, _) -> k.descriptor })
    }
}
