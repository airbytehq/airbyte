/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.base.destination.typing_deduping

import com.google.common.collect.Streams
import io.airbyte.cdk.integrations.util.ConnectorExceptionUtil.getResultsOrLogAndThrowFirst
import io.airbyte.commons.concurrency.CompletableFutures
import io.airbyte.integrations.base.destination.typing_deduping.migrators.Migration
import io.airbyte.integrations.base.destination.typing_deduping.migrators.MinimumDestinationState
import java.util.*
import java.util.concurrent.CompletableFuture
import java.util.concurrent.CompletionStage
import java.util.concurrent.ExecutorService
import java.util.stream.Collectors.toMap
import org.slf4j.Logger
import org.slf4j.LoggerFactory

class TyperDeduperUtil {
    companion object {
        private val LOGGER: Logger = LoggerFactory.getLogger(TyperDeduperUtil::class.java)

        @JvmStatic
        fun <DestinationState : MinimumDestinationState> executeRawTableMigrations(
            executorService: ExecutorService,
            destinationHandler: DestinationHandler<DestinationState>,
            migrations: List<Migration<DestinationState>>,
            initialStates: List<DestinationInitialStatus<DestinationState>>
        ): List<DestinationInitialStatus<DestinationState>> {
            // TODO: Either the migrations run the soft reset and create v2 tables or the actual
            // prepare tables.
            // unify the logic
            // with current state of raw tables & final tables. This is done first before gather
            // initial state
            // to avoid recreating
            // final tables later again.

            // Run migrations in lockstep. Some migrations may require us to refetch the initial
            // state.
            // We want to be able to batch those calls together across streams.
            // If a migration runs on one stream, it's likely to also run on other streams.
            // So we can bundle the gatherInitialState calls together.
            var currentStates = initialStates
            for (migration in migrations) {
                // Execute the migration on all streams in parallel
                val futures:
                    Map<StreamId, CompletionStage<Migration.MigrationResult<DestinationState>>> =
                    currentStates
                        .stream()
                        .collect(
                            toMap(
                                { it.streamConfig.id },
                                { initialState ->
                                    runMigrationsAsync(
                                        executorService,
                                        destinationHandler,
                                        migration,
                                        initialState
                                    )
                                }
                            )
                        )
                val migrationResultFutures =
                    CompletableFutures.allOf(futures.values.toList()).toCompletableFuture().join()
                getResultsOrLogAndThrowFirst(
                    "The following exceptions were thrown attempting to run migrations:\n",
                    migrationResultFutures
                )
                val migrationResults: Map<StreamId, Migration.MigrationResult<DestinationState>> =
                    futures.mapValues { it.value.toCompletableFuture().join() }

                // Check if we need to refetch DestinationInitialState
                val invalidatedStreams: Set<StreamId> =
                    migrationResults.filter { it.value.invalidateInitialState }.keys
                val updatedStates: List<DestinationInitialStatus<DestinationState>>
                if (invalidatedStreams.isNotEmpty()) {
                    LOGGER.info("Refetching initial state for streams: $invalidatedStreams")
                    updatedStates =
                        destinationHandler.gatherInitialState(
                            currentStates
                                .filter { invalidatedStreams.contains(it.streamConfig.id) }
                                .map { it.streamConfig }
                        )
                    LOGGER.info("Updated states: $updatedStates")
                } else {
                    updatedStates = emptyList()
                }

                // Update the DestinationInitialStates with the new DestinationStates,
                // and also update initialStates with the refetched states.
                currentStates =
                    currentStates.map { initialState ->
                        // migrationResults will always contain an entry for each stream, so we can
                        // safely use !!
                        val updatedDestinationState =
                            migrationResults[initialState.streamConfig.id]!!.updatedDestinationState
                        if (invalidatedStreams.contains(initialState.streamConfig.id)) {
                            // We invalidated this stream's DestinationInitialState.
                            // Find the updated DestinationInitialState, and update it with our new
                            // DestinationState
                            return@map updatedStates
                                .filter { updatedState ->
                                    updatedState.streamConfig.id.equals(
                                        initialState.streamConfig.id
                                    )
                                }
                                .first()
                                .copy(destinationState = updatedDestinationState)
                        } else {
                            // Just update the original DestinationInitialState with the new
                            // DestinationState.
                            return@map initialState.copy(destinationState = updatedDestinationState)
                        }
                    }
            }
            return currentStates
        }

        /**
         * The legacy-style migrations (V1V2Migrator, V2TableMigrator) need to run before we gather
         * initial state, because they're dumb and weird. (specifically: SnowflakeV2TableMigrator
         * inspects the final tables and triggers a soft reset directly within the migration). TODO:
         * Migrate these migrations to the new migration system. This will also reduce the number of
         * times we need to query DB metadata, since (a) we can rely on the gatherInitialState
         * values, and (b) we can add a DestinationState field for these migrations. It also enables
         * us to not trigger multiple soft resets in a single sync.
         */
        @JvmStatic
        fun <DestinationState> executeWeirdMigrations(
            executorService: ExecutorService,
            sqlGenerator: SqlGenerator,
            destinationHandler: DestinationHandler<DestinationState>,
            v1V2Migrator: DestinationV1V2Migrator,
            v2TableMigrator: V2TableMigrator,
            parsedCatalog: ParsedCatalog
        ) {
            val futures =
                parsedCatalog.streams.map {
                    CompletableFuture.supplyAsync(
                        {
                            v1V2Migrator.migrateIfNecessary(sqlGenerator, destinationHandler, it)
                            v2TableMigrator.migrateIfNecessary(it)
                        },
                        executorService
                    )
                }
            getResultsOrLogAndThrowFirst(
                "The following exceptions were thrown attempting to run migrations:\n",
                CompletableFutures.allOf(futures.toList()).toCompletableFuture().join()
            )
        }

        /**
         * Extracts all the "raw" and "final" schemas identified in the [parsedCatalog] and ensures
         * they exist in the Destination Database.
         */
        @JvmStatic
        fun <DestinationState> prepareSchemas(
            sqlGenerator: SqlGenerator,
            destinationHandler: DestinationHandler<DestinationState>,
            parsedCatalog: ParsedCatalog
        ) {
            val rawSchema = parsedCatalog.streams.stream().map { it.id.rawNamespace }
            val finalSchema = parsedCatalog.streams.stream().map { it.id.finalNamespace }
            val createAllSchemasSql =
                Streams.concat<String>(rawSchema, finalSchema)
                    .filter(Objects::nonNull)
                    .distinct()
                    .map(sqlGenerator::createSchema)
                    .toList()
            destinationHandler.execute(Sql.concat(createAllSchemasSql))
        }

        private fun <DestinationState : MinimumDestinationState> runMigrationsAsync(
            executorService: ExecutorService,
            destinationHandler: DestinationHandler<DestinationState>,
            migration: Migration<DestinationState>,
            initialStatus: DestinationInitialStatus<DestinationState>
        ): CompletionStage<Migration.MigrationResult<DestinationState>> {
            return CompletableFuture.supplyAsync(
                {
                    LOGGER.info(
                        "Maybe executing ${migration.javaClass.simpleName} migration for stream ${initialStatus.streamConfig.id.originalNamespace}.${initialStatus.streamConfig.id.originalName}."
                    )

                    // We technically don't need to track this, but might as well hedge against
                    // migrations
                    // accidentally setting softReset=false
                    val softReset = initialStatus.destinationState.needsSoftReset()
                    val migrationResult =
                        migration.migrateIfNecessary(
                            destinationHandler,
                            initialStatus.streamConfig,
                            initialStatus
                        )
                    val updatedNeedsSoftReset =
                        softReset || migrationResult.updatedDestinationState.needsSoftReset()
                    return@supplyAsync migrationResult.copy(
                        updatedDestinationState =
                            migrationResult.updatedDestinationState.withSoftReset(
                                updatedNeedsSoftReset
                            )
                    )
                },
                executorService
            )
        }
    }
}
