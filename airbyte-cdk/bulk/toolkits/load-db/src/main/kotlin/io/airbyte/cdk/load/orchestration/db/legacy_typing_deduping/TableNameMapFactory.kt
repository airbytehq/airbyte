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

@Factory
class TypingDedupingTableNameMapFactory(
  private val catalog: DestinationCatalog,
  private val rawTableNameGenerator: RawTableNameGenerator,
  private val finalTableNameGenerator: FinalTableNameGenerator,
  private val finalTableColumnNameGenerator: ColumnNameGenerator,
) {
    @Singleton
    fun get(): Map<DestinationStream, Pair<TableNames, ColumnNameMapping>> {
        // TODO handle collisions in table names
        return catalog.streams.associateWith { stream ->
            Pair(
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
    }
}

@Factory
class TypingDedupingTableNameMapByDescriptorFactory(
  private val map: Map<DestinationStream, Pair<TableNames, ColumnNameMapping>>,
) {
    @Singleton
    fun get(): Map<DestinationStream.Descriptor, Pair<TableNames, ColumnNameMapping>> {
        return map.mapKeys { (k, _) -> k.descriptor }
    }
}
