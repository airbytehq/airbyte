/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.mssql.v2

import io.airbyte.cdk.load.command.DestinationCatalog
import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.message.DestinationRecordRaw
import io.airbyte.cdk.load.write.BatchLoadStrategy
import io.airbyte.cdk.load.write.StreamStateStore
import io.airbyte.integrations.destination.mssql.v2.config.MSSQLConfiguration
import io.airbyte.integrations.destination.mssql.v2.config.MSSQLIsNotConfiguredForBulkLoad
import io.github.oshai.kotlinlogging.KotlinLogging
import io.micronaut.context.annotation.Requires
import jakarta.inject.Singleton
import java.sql.PreparedStatement
import java.util.concurrent.ConcurrentHashMap
import java.util.concurrent.atomic.AtomicLong
import kotlinx.coroutines.sync.Mutex
import kotlinx.coroutines.sync.withLock

@Singleton
@Requires(condition = MSSQLIsNotConfiguredForBulkLoad::class)
class MSSQLBatchLoader(
    config: MSSQLConfiguration,
    catalog: DestinationCatalog,
    val stateStore: StreamStateStore<MSSQLStreamState>,
): BatchLoadStrategy {
    private val log = KotlinLogging.logger {}

    override val targetBatchSizeBytes: Long = config.recordBatchSizeBytes
    override val maxMemoryRatioToReserveForBatches: Double = 1.0
    private val recordCommitBatchSize = config.batchEveryNRecords
    private val sharedTableLocks = ConcurrentHashMap(
        catalog.streams.associate { it.descriptor to Mutex() }
    )
    private val batchNo = AtomicLong(0L)

    override suspend fun loadBatch(
        stream: DestinationStream.Descriptor,
        partition: Int,
        batch: Iterator<DestinationRecordRaw>
    ) {
        log.info { "Loading batch ${batchNo.incrementAndGet()} for stream $stream" }
        var rows: Long = 0
        val state =
            (stateStore.get(stream) as MSSQLDirectLoaderStreamState?)
                ?: throw IllegalStateException("No state found for stream $stream.")
        val sqlBuilder = state.sqlBuilder
        state.dataSource.connection.use { connection ->
            connection.autoCommit = false

            sqlBuilder.getFinalTableInsertColumnHeader().executeUpdate(connection) { statement ->
                batch.forEach { record ->
                    sqlBuilder.populateStatement(
                        statement,
                        record,
                        sqlBuilder.finalTableSchema
                    )
                    statement.addBatch()

                    // Periodically execute the batch to avoid too-large batches
                    if (++rows % recordCommitBatchSize == 0L) {
                        statement.executeBatch()
                        connection.commit()
                    }
                }

                statement.executeBatch()
            }

            // If CDC is enabled, remove stale recordsM
            if (sqlBuilder.hasCdc) {
                log.info { "Deleting stale records from CDC table for stream $stream" }
                sqlBuilder.deleteCdc(connection)
            }
            connection.commit()

            log.info { "Completed batch ${batchNo.get()} for stream $stream" }
        }
    }
}
