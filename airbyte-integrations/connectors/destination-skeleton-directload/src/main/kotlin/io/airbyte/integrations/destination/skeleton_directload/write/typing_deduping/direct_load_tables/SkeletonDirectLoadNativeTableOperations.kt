/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.skeleton_directload.write.typing_deduping.direct_load_tables

import edu.umd.cs.findbugs.annotations.SuppressFBWarnings
import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.orchestration.db.ColumnNameMapping
import io.airbyte.cdk.load.orchestration.db.TableName
import io.airbyte.cdk.load.orchestration.db.TempTableNameGenerator
import io.airbyte.cdk.load.orchestration.db.direct_load_table.DefaultDirectLoadTableSqlOperations
import io.airbyte.cdk.load.orchestration.db.direct_load_table.DirectLoadTableNativeOperations
import io.airbyte.integrations.destination.skeleton_directload.SkeletonDirectLoadClient
import io.airbyte.integrations.destination.skeleton_directload.write.typing_deduping.SkeletonDirectLoadDatabaseHandler
import io.github.oshai.kotlinlogging.KotlinLogging

private val logger = KotlinLogging.logger {}

@SuppressFBWarnings("NP_NONNULL_PARAM_VIOLATION", "kotlin coroutines")
class SkeletonDirectLoadNativeTableOperations(
    @Suppress("UNUSED_PARAMETER") private val skeletonClient: SkeletonDirectLoadClient,
    @Suppress("UNUSED_PARAMETER") private val sqlOperations: DefaultDirectLoadTableSqlOperations,
    @Suppress("UNUSED_PARAMETER") private val databaseHandler: SkeletonDirectLoadDatabaseHandler,
    @Suppress("UNUSED_PARAMETER") private val tempTableNameGenerator: TempTableNameGenerator,
) : DirectLoadTableNativeOperations {
    override suspend fun ensureSchemaMatches(
        @Suppress("UNUSED_PARAMETER") stream: DestinationStream,
        @Suppress("UNUSED_PARAMETER") tableName: TableName,
        @Suppress("UNUSED_PARAMETER") columnNameMapping: ColumnNameMapping,
    ) {
        // The name is not ideal here but this method should actually perform actions on the DB.
    }

    override suspend fun getGenerationId(@Suppress("UNUSED_PARAMETER") tableName: TableName): Long {
        // This method should return the generation id for the current table
        return 0L
    }
}
