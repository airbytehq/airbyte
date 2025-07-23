/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.skeleton_directload

import io.airbyte.cdk.load.check.DestinationCheckerSync
import io.airbyte.cdk.load.command.DestinationCatalog
import io.airbyte.cdk.load.command.DestinationConfiguration
import io.airbyte.cdk.load.orchestration.db.DefaultTempTableNameGenerator
import io.airbyte.cdk.load.orchestration.db.direct_load_table.DefaultDirectLoadTableSqlOperations
import io.airbyte.cdk.load.orchestration.db.direct_load_table.DirectLoadTableExecutionConfig
import io.airbyte.cdk.load.orchestration.db.direct_load_table.DirectLoadTableWriter
import io.airbyte.cdk.load.orchestration.db.legacy_typing_deduping.TableCatalog
import io.airbyte.cdk.load.state.SyncManager
import io.airbyte.cdk.load.task.DestinationTaskLauncher
import io.airbyte.cdk.load.write.DestinationWriter
import io.airbyte.cdk.load.write.StreamStateStore
import io.airbyte.cdk.load.write.WriteOperation
import io.airbyte.cdk.load.write.db.DbConstants.DEFAULT_INTERNAL_NAMESPACE
import io.airbyte.integrations.destination.skeleton_directload.check.SkeletonDirectLoadCheckCleaner
import io.airbyte.integrations.destination.skeleton_directload.spec.SkeletonDirectLoadConfiguration
import io.airbyte.integrations.destination.skeleton_directload.write.typing_deduping.SkeletonDirectLoadDatabaseHandler
import io.airbyte.integrations.destination.skeleton_directload.write.typing_deduping.direct_load_tables.SkeletonDirectLoadDatabaseInitialStatusGatherer
import io.airbyte.integrations.destination.skeleton_directload.write.typing_deduping.direct_load_tables.SkeletonDirectLoadNativeTableOperations
import io.airbyte.integrations.destination.skeleton_directload.write.typing_deduping.direct_load_tables.SkeletonDirectLoadSqlGenerator
import io.github.oshai.kotlinlogging.KotlinLogging
import io.micronaut.context.annotation.Factory
import jakarta.inject.Named
import jakarta.inject.Singleton
import java.io.InputStream

private val logger = KotlinLogging.logger {}

@Factory
class SkeletonDirectLoadBeansFactory {
    @Singleton
    fun getConfig(config: DestinationConfiguration) = config as SkeletonDirectLoadConfiguration

    @Singleton
    fun getChecker(
        catalog: DestinationCatalog,
        @Named("inputStream") stdinPipe: InputStream,
        taskLauncher: DestinationTaskLauncher,
        syncManager: SyncManager,
    ) =
        DestinationCheckerSync(
            catalog,
            stdinPipe,
            WriteOperation(taskLauncher, syncManager),
            SkeletonDirectLoadCheckCleaner(),
        )

    @Singleton
    fun getWriter(
        skeletonClient: SkeletonDirectLoadClient,
        config: SkeletonDirectLoadConfiguration,
        names: TableCatalog,
        // micronaut will only instantiate a single instance of StreamStateStore,
        // so accept it as a * generic and cast as needed.
        // we use a different type depending on whether we're in legacy raw tables vs
        // direct-load tables mode.
        streamStateStore: StreamStateStore<*>,
    ): DestinationWriter {
        val destinationHandler = SkeletonDirectLoadDatabaseHandler(skeletonClient)

        val sqlTableOperations =
            DefaultDirectLoadTableSqlOperations(
                SkeletonDirectLoadSqlGenerator(),
                destinationHandler,
            )
        // force smart cast
        @Suppress("UNCHECKED_CAST")
        streamStateStore as StreamStateStore<DirectLoadTableExecutionConfig>
        val tempTableNameGenerator =
            DefaultTempTableNameGenerator(internalNamespace = DEFAULT_INTERNAL_NAMESPACE)

        return DirectLoadTableWriter(
            internalNamespace = DEFAULT_INTERNAL_NAMESPACE,
            names = names,
            stateGatherer =
                SkeletonDirectLoadDatabaseInitialStatusGatherer(
                    skeletonClient,
                    tempTableNameGenerator
                ),
            destinationHandler = destinationHandler,
            nativeTableOperations =
                SkeletonDirectLoadNativeTableOperations(
                    skeletonClient,
                    sqlTableOperations,
                    destinationHandler,
                    tempTableNameGenerator,
                ),
            sqlTableOperations = sqlTableOperations,
            streamStateStore = streamStateStore,
            tempTableNameGenerator,
        )
    }

    @Singleton
    fun getSkeletonDirectLoadClient(
        @Suppress("UNUSED_PARAMETER")
        config: SkeletonDirectLoadConfiguration
    ): SkeletonDirectLoadClient {
        // This method should return a usable client. This could be a wrapper around an existing
        // library, something entirely custom
        return SkeletonDirectLoadClient()
    }
}
