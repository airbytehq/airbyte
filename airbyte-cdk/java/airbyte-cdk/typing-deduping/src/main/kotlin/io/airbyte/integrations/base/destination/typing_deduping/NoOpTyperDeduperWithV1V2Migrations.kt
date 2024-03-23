/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.integrations.base.destination.typing_deduping

import io.airbyte.cdk.integrations.base.IntegrationRunner
import io.airbyte.cdk.integrations.destination.StreamSyncSummary
import io.airbyte.integrations.base.destination.typing_deduping.TyperDeduperUtil.Companion.executeRawTableMigrations
import io.airbyte.integrations.base.destination.typing_deduping.TyperDeduperUtil.Companion.executeWeirdMigrations
import io.airbyte.integrations.base.destination.typing_deduping.TyperDeduperUtil.Companion.prepareSchemas
import io.airbyte.integrations.base.destination.typing_deduping.migrators.Migration
import io.airbyte.integrations.base.destination.typing_deduping.migrators.MinimumDestinationState
import io.airbyte.protocol.models.v0.StreamDescriptor
import lombok.extern.slf4j.Slf4j
import org.apache.commons.lang3.concurrent.BasicThreadFactory
import java.util.concurrent.ExecutorService
import java.util.concurrent.Executors
import java.util.concurrent.locks.Lock
import java.util.function.Function
import java.util.stream.Collectors

/**
 * This is a NoOp implementation which skips and Typing and Deduping operations and does not emit
 * the final tables. However, this implementation still performs V1->V2 migrations and V2
 * json->string migrations in the raw tables.
 */
@Slf4j
class NoOpTyperDeduperWithV1V2Migrations<DestinationState : MinimumDestinationState?>(private val sqlGenerator: SqlGenerator,
                                                                                      destinationHandler: DestinationHandler<DestinationState>,
                                                                                      parsedCatalog: ParsedCatalog,
                                                                                      v1V2Migrator: DestinationV1V2Migrator,
                                                                                      v2TableMigrator: V2TableMigrator,
                                                                                      migrations: List<Migration<DestinationState>>) : TyperDeduper {
    private val v1V2Migrator: DestinationV1V2Migrator
    private val v2TableMigrator: V2TableMigrator
    private val migrations: List<Migration<DestinationState?>>
    private val executorService: ExecutorService
    private val parsedCatalog: ParsedCatalog
    private val destinationHandler: DestinationHandler<DestinationState?>

    init {
        this.destinationHandler = destinationHandler
        this.parsedCatalog = parsedCatalog
        this.v1V2Migrator = v1V2Migrator
        this.v2TableMigrator = v2TableMigrator
        this.migrations = migrations
        this.executorService = Executors.newFixedThreadPool(FutureUtils.getCountOfTypeAndDedupeThreads(),
                BasicThreadFactory.Builder().namingPattern(IntegrationRunner.TYPE_AND_DEDUPE_THREAD_NAME).build())
    }

    @Throws(Exception::class)
    override fun prepareSchemasAndRunMigrations() {
        prepareSchemas(sqlGenerator, destinationHandler, parsedCatalog)

        executeWeirdMigrations(
                executorService,
                sqlGenerator,
                destinationHandler,
                v1V2Migrator,
                v2TableMigrator,
                parsedCatalog)

        val destinationInitialStatuses = executeRawTableMigrations(
                executorService,
                destinationHandler,
                migrations,
                destinationHandler.gatherInitialState(parsedCatalog.streams))

        // Commit the updated destination states.
        // We don't need to trigger any soft resets, because we don't have any final tables.
        destinationHandler.commitDestinationStates(destinationInitialStatuses.stream().collect(Collectors.toMap(
                Function { state: DestinationInitialStatus<DestinationState?> -> state.streamConfig.id },
                DestinationInitialStatus::destinationState)))
    }

    override fun prepareFinalTables() {
        NoOpTyperDeduperWithV1V2Migrations.log.info("Skipping prepareFinalTables")
    }

    override fun typeAndDedupe(originalNamespace: String, originalName: String, mustRun: Boolean) {
        NoOpTyperDeduperWithV1V2Migrations.log.info("Skipping TypeAndDedupe")
    }

    override fun getRawTableInsertLock(originalNamespace: String, originalName: String): Lock {
        return NoOpRawTableTDLock()
    }

    override fun typeAndDedupe(streamSyncSummaries: Map<StreamDescriptor?, StreamSyncSummary>) {
        NoOpTyperDeduperWithV1V2Migrations.log.info("Skipping TypeAndDedupe final")
    }

    override fun commitFinalTables() {
        NoOpTyperDeduperWithV1V2Migrations.log.info("Skipping commitFinalTables final")
    }

    override fun cleanup() {
        NoOpTyperDeduperWithV1V2Migrations.log.info("Cleaning Up type-and-dedupe thread pool")
        executorService.shutdown()
    }
}
