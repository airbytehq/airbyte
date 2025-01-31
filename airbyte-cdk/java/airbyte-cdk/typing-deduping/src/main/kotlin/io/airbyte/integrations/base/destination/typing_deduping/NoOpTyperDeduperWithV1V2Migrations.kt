/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.integrations.base.destination.typing_deduping

import io.airbyte.cdk.integrations.base.IntegrationRunner
import io.airbyte.cdk.integrations.destination.StreamSyncSummary
import io.airbyte.integrations.base.destination.typing_deduping.TyperDeduperUtil.executeRawTableMigrations
import io.airbyte.integrations.base.destination.typing_deduping.TyperDeduperUtil.executeWeirdMigrations
import io.airbyte.integrations.base.destination.typing_deduping.TyperDeduperUtil.prepareSchemas
import io.airbyte.integrations.base.destination.typing_deduping.migrators.Migration
import io.airbyte.integrations.base.destination.typing_deduping.migrators.MinimumDestinationState
import io.airbyte.protocol.models.v0.StreamDescriptor
import io.github.oshai.kotlinlogging.KotlinLogging
import java.util.concurrent.ExecutorService
import java.util.concurrent.Executors
import org.apache.commons.lang3.concurrent.BasicThreadFactory

/**
 * This is a NoOp implementation which skips and Typing and Deduping operations and does not emit
 * the final tables. However, this implementation still performs V1->V2 migrations and V2
 * json->string migrations in the raw tables.
 */
private val log = KotlinLogging.logger {}

class NoOpTyperDeduperWithV1V2Migrations<DestinationState : MinimumDestinationState>(
    private val sqlGenerator: SqlGenerator,
    private val destinationHandler: DestinationHandler<DestinationState>,
    private val parsedCatalog: ParsedCatalog,
    private val v1V2Migrator: DestinationV1V2Migrator,
    private val v2TableMigrator: V2TableMigrator,
    private val migrations: List<Migration<DestinationState>>
) : TyperDeduper {
    private val executorService: ExecutorService =
        Executors.newFixedThreadPool(
            FutureUtils.countOfTypeAndDedupeThreads,
            BasicThreadFactory.Builder()
                .namingPattern(IntegrationRunner.TYPE_AND_DEDUPE_THREAD_NAME)
                .build()
        )

    @Throws(Exception::class)
    override fun prepareSchemasAndRunMigrations() {
        prepareSchemas(sqlGenerator, destinationHandler, parsedCatalog)

        executeWeirdMigrations(
            executorService,
            sqlGenerator,
            destinationHandler,
            v1V2Migrator,
            v2TableMigrator,
            parsedCatalog
        )

        val destinationInitialStatuses =
            executeRawTableMigrations(
                executorService,
                destinationHandler,
                migrations,
                destinationHandler.gatherInitialState(parsedCatalog.streams)
            )

        // Commit the updated destination states.
        // We don't need to trigger any soft resets, because we don't have any final tables.
        destinationHandler.commitDestinationStates(
            destinationInitialStatuses.associate { it.streamConfig.id to it.destinationState }
        )
    }

    override fun prepareFinalTables() {
        log.info { "Skipping prepareFinalTables" }
    }

    override fun typeAndDedupe(originalNamespace: String, originalName: String) {
        log.info { "Skipping TypeAndDedupe" }
    }

    override fun typeAndDedupe(streamSyncSummaries: Map<StreamDescriptor, StreamSyncSummary>) {
        log.info { "Skipping TypeAndDedupe final" }
    }

    override fun commitFinalTables(streamSyncSummaries: Map<StreamDescriptor, StreamSyncSummary>) {
        log.info { "Skipping commitFinalTables final" }
    }

    override fun cleanup() {
        log.info { "Cleaning Up type-and-dedupe thread pool" }
        executorService.shutdown()
    }
}
