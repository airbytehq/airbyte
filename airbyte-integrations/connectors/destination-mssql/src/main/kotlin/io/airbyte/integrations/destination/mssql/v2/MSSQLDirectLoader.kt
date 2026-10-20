/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.mssql.v2

import edu.umd.cs.findbugs.annotations.SuppressFBWarnings
import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.message.DestinationRecordRaw
import io.airbyte.cdk.load.write.DirectLoader
import io.airbyte.cdk.load.write.DirectLoaderFactory
import io.airbyte.cdk.load.write.StreamStateStore
import io.airbyte.integrations.destination.mssql.v2.config.MSSQLConfiguration
import io.airbyte.integrations.destination.mssql.v2.config.MSSQLIsNotConfiguredForBulkLoad
import io.github.oshai.kotlinlogging.KotlinLogging
import io.micronaut.context.annotation.Requires
import jakarta.inject.Singleton
import java.sql.Connection
import java.sql.PreparedStatement
import java.sql.SQLException

@SuppressFBWarnings("NP_NONNULL_PARAM_VIOLATION", "kotlin coroutines")
class MSSQLDirectLoader(
    config: MSSQLConfiguration,
    private val stateStore: StreamStateStore<MSSQLStreamState>,
    private val streamDescriptor: DestinationStream.Descriptor,
    private val batch: Int,
    private val parent: MSSQLDirectLoaderFactory,
) : DirectLoader {
    private val log = KotlinLogging.logger {}
    private val recordCommitBatchSize = config.batchEveryNRecords
    private val maxBatchDataSize = config.maxBatchSizeBytes

    private var rows: Long = 0
    private var dataSize: Long = 0

    private class Batch(
        val sqlBuilder: MSSQLQueryBuilder,
        val connection: Connection,
        val preparedStatement: PreparedStatement,
    )

    private var openBatch: Batch? = null

    private suspend fun awaitBatch(): Batch =
        openBatch
            ?: run {
                val state = stateStore.awaitStreamState(streamDescriptor)
                check(state is MSSQLDirectLoaderStreamState) {
                    "Unexpected state ${state::class.simpleName} for stream $streamDescriptor."
                }
                val connection = state.dataSource.connection.also { it.autoCommit = false }
                Batch(
                    state.sqlBuilder,
                    connection,
                    connection.prepareStatement(
                        state.sqlBuilder.getFinalTableInsertColumnHeader().trimIndent(),
                    ),
                )
            }
                .also { openBatch = it }

    override suspend fun accept(
        record: DestinationRecordRaw,
    ): DirectLoader.DirectLoadResult {
        val batch = awaitBatch()
        batch.sqlBuilder.populateStatement(
            batch.preparedStatement,
            record,
            batch.sqlBuilder.finalTableSchema,
        )
        batch.preparedStatement.addBatch()

        // Periodically execute the batch to avoid too-large batches
        if (++rows % recordCommitBatchSize == 0L) {
            executeBatchSafely(batch)
        }

        // Periodically complete the batch and ack underlying records.
        dataSize += record.serializedSizeBytes

        if (dataSize >= maxBatchDataSize) {
            finish()
            return DirectLoader.Complete
        }

        return DirectLoader.Incomplete
    }

    private fun executeBatchSafely(batch: Batch) {
        val preparedStatement = batch.preparedStatement
        // This is to prevent deadlock errors that will nuke the transaction.
        // TODO: Promote direct loader to use suspend functions so this can use a suspending mutex
        synchronized(parent) {
            try {
                preparedStatement.executeBatch()
            } catch (e: SQLException) {
                MSSQLErrorClassifier.rethrowClassified(e)
            }
            preparedStatement.clearBatch()
            preparedStatement.clearParameters()
            batch.connection.commit()
        }
    }

    override suspend fun finish() {
        log.info { "Finishing batch $batch for stream $streamDescriptor" }

        val batch = awaitBatch()

        // Execute remaining records if any
        executeBatchSafely(batch)
        batch.preparedStatement.close()

        // If CDC is enabled, remove stale records
        if (batch.sqlBuilder.hasCdc) {
            batch.sqlBuilder.deleteCdc(batch.connection)
        }

        batch.connection.commit()
    }

    override fun close() {
        log.info { "Closing connection for batch $batch" }
        openBatch?.connection?.close()
    }
}

@Singleton
@Requires(condition = MSSQLIsNotConfiguredForBulkLoad::class)
class MSSQLDirectLoaderFactory(
    val config: MSSQLConfiguration,
    val stateStore: StreamStateStore<MSSQLStreamState>,
) : DirectLoaderFactory<MSSQLDirectLoader> {
    private val log = KotlinLogging.logger {}

    override val inputPartitions: Int =
        config.numInputPartitions // Distribute work by stream, if interleaved
    override val maxNumOpenLoaders: Int = config.maxNumOpenLoaders

    private var batch: Int = 0

    override fun create(
        streamDescriptor: DestinationStream.Descriptor,
        part: Int,
    ): MSSQLDirectLoader {
        log.info { "Creating query builder for batch $batch of stream $streamDescriptor" }

        return MSSQLDirectLoader(config, stateStore, streamDescriptor, batch++, this)
    }
}
