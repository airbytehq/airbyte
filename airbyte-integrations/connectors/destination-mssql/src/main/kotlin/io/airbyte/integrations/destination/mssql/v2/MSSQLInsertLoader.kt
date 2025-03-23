/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.mssql.v2

import io.airbyte.cdk.load.command.DestinationCatalog
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

    private val maxRequestSizeBytes = 10 * 1024 * 1024

    private var totalSize: Long = 0

    override fun accept(
        record: DestinationRecordRaw,
    ): DirectLoader.DirectLoadResult {
        sqlBuilder.populateStatement(preparedStatement, record, sqlBuilder.finalTableSchema)
        preparedStatement.addBatch()
        totalSize += record.serializedSizeBytes.toLong()
        if (totalSize >= maxRequestSizeBytes) {
            finish()
            return DirectLoader.Complete
        } else {
            return DirectLoader.Incomplete
        }
    }

    override fun finish() {
        log.info { "Executing batch $batch for stream $streamDescriptor" }

        preparedStatement.executeBatch()
        connection.commit()

        if (sqlBuilder.hasCdc) {
            sqlBuilder.deleteCdc(connection)
        }
    }

    override fun close() {
        println("Closing connection")
        connection.close()
    }
}

@Singleton
@Requires(condition = MSSQLIsNotConfiguredForBulkLoad::class)
class MSSQLDirectLoaderFactory(
    val config: MSSQLConfiguration,
    val catalog: DestinationCatalog,
    val stateStore: StreamStateStore<MSSQLStreamState>,
) : DirectLoaderFactory<MSSQLDirectLoader> {
    private val log = KotlinLogging.logger {}

    override val inputPartitions: Int = 2
    override val maxNumOpenLoaders: Int = 8

    private var batch: Int = 0
    override fun create(
        streamDescriptor: DestinationStream.Descriptor,
        part: Int
    ): MSSQLDirectLoader {
        log.info { "Creating query builder for batch $batch of stream $streamDescriptor" }

        val stream = catalog.getStream(streamDescriptor)
        val dataSource = stateStore.get(streamDescriptor)!!.dataSource
        val connection = dataSource.connection
        connection.autoCommit = false
        val sqlBuilder = MSSQLQueryBuilder(config.schema, stream)
        val statement =
            connection.prepareStatement(sqlBuilder.getFinalTableInsertColumnHeader().trimIndent())

        return MSSQLDirectLoader(connection, sqlBuilder, statement, streamDescriptor, batch++)
    }
}
