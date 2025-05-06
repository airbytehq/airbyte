/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.bigquery

import io.airbyte.cdk.load.check.DestinationCheckerSync
import io.airbyte.cdk.load.command.DestinationCatalog
import io.airbyte.cdk.load.state.SyncManager
import io.airbyte.cdk.load.task.DestinationTaskLauncher
import io.airbyte.cdk.load.write.WriteOperation
import io.airbyte.integrations.destination.bigquery.spec.BigqueryConfiguration
import io.airbyte.integrations.destination.bigquery.typing_deduping.BigqueryFinalTableNameGenerator
import io.airbyte.integrations.destination.bigquery.typing_deduping.BigqueryRawTableNameGenerator
import io.airbyte.integrations.destination.bigquery.typing_deduping.toTableId
import io.airbyte.integrations.destination.bigquery.util.BigqueryClientFactory
import io.micronaut.context.annotation.Factory
import jakarta.inject.Named
import jakarta.inject.Singleton
import java.io.PipedOutputStream

@Factory
class BigqueryCheckerFactory(
    private val catalog: DestinationCatalog,
    @Named("checkInputStreamPipe") private val pipe: PipedOutputStream,
    private val taskLauncher: DestinationTaskLauncher,
    private val syncManager: SyncManager,
) {
    @Singleton
    fun get() =
        DestinationCheckerSync<BigqueryConfiguration>(
            catalog,
            pipe,
            WriteOperation(taskLauncher, syncManager)
        ) { config, stream ->
            val bq = BigqueryClientFactory(config).make()
            bq.getTable(
                    BigqueryRawTableNameGenerator(config)
                        .getTableName(stream.descriptor)
                        .toTableId()
                )
                ?.delete()
            bq.getTable(
                    BigqueryFinalTableNameGenerator(config)
                        .getTableName(stream.descriptor)
                        .toTableId()
                )
                ?.delete()
        }
}
