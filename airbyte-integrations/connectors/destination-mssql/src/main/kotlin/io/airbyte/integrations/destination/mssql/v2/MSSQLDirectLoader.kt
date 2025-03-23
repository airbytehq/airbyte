/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.mssql.v2

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

class MSSQLDirectLoader(
    private val connection: Connection,
    private val sqlBuilder: MSSQLQueryBuilder,
    private val preparedStatement: PreparedStatement,
    private val streamDescriptor: DestinationStream.Descriptor,
    private val batch: Int,
) : DirectLoader {
    private val log = KotlinLogging.logger {}
    private val recordCommitBatchSize = 5_000
    private val maxBatchDataSize = 200 * 1024 * 1024L

    var rows: Long = 0
    var dataSize: Long = 0

    override fun accept(
        record: DestinationRecordRaw,
    ): DirectLoader.DirectLoadResult {
        sqlBuilder.populateStatement(preparedStatement, record, sqlBuilder.finalTableSchema)
        preparedStatement.addBatch()

        // Periodically execute the batch to avoid too-large batches
        if (++rows % recordCommitBatchSize == 0L) {
            preparedStatement.executeBatch()
            connection.commit()
        }

        // Periodically complete the batch and ack underlying records.
        dataSize += record.serializedSizeBytes
        if (dataSize >= maxBatchDataSize) {
            finish()
            return DirectLoader.Complete
        }

        return DirectLoader.Incomplete
    }

    override fun finish() {
        log.info { "Executing batch $batch for stream $streamDescriptor" }

        // Execute remaining records if any
        preparedStatement.executeBatch()
        preparedStatement.close()

        // If CDC is enabled, remove stale records
        if (sqlBuilder.hasCdc) {
            sqlBuilder.deleteCdc(connection)
        }

        connection.commit()
    }

    override fun close() {
        connection.close()
    }
}

@Singleton
@Requires(condition = MSSQLIsNotConfiguredForBulkLoad::class)
class MSSQLDirectLoaderFactory(
    val config: MSSQLConfiguration,
    val stateStore: StreamStateStore<MSSQLStreamState>,
) : DirectLoaderFactory<MSSQLDirectLoader> {
    private val log = KotlinLogging.logger {}

    override val inputPartitions: Int = 2 // Distribute work by stream, if interleaved
    override val maxNumOpenLoaders: Int = 8

    private var batch: Int = 0
    override fun create(
        streamDescriptor: DestinationStream.Descriptor,
        part: Int
    ): MSSQLDirectLoader {
        log.info { "Creating query builder for batch $batch of stream $streamDescriptor" }

        val state = stateStore.get(streamDescriptor)!! as MSSQLDirectLoaderStreamState
        val connection = state.dataSource.connection
        connection.autoCommit = false
        val statement =
            connection.prepareStatement(
                state.sqlBuilder.getFinalTableInsertColumnHeader().trimIndent()
            )

        return MSSQLDirectLoader(connection, state.sqlBuilder, statement, streamDescriptor, batch++)
    }
}
