/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.mssql.v2

import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.message.Batch
import io.airbyte.cdk.load.message.DestinationRecordAirbyteValue
import io.airbyte.cdk.load.message.SimpleBatch
import io.airbyte.cdk.load.state.StreamProcessingFailed
import io.airbyte.cdk.load.write.StreamLoader
import io.github.oshai.kotlinlogging.KotlinLogging
import javax.sql.DataSource

private val log = KotlinLogging.logger {}

class MSSQLStreamLoader(
    private val dataSource: DataSource,
    override val stream: DestinationStream,
    private val sqlBuilder: MSSQLQueryBuilder,
) : StreamLoader {

    override suspend fun start() {
        ensureTableExists(dataSource)
    }

    override suspend fun close(streamFailure: StreamProcessingFailed?) {
        if (streamFailure == null) {
            truncatePreviousGenerations(dataSource)
        }
        super.close(streamFailure)
    }

    override suspend fun processRecords(
        records: Iterator<DestinationRecordAirbyteValue>,
        totalSizeBytes: Long,
        endOfStream: Boolean
    ): Batch {
        dataSource.connection.use { connection ->
            val statement =
                connection.prepareStatement(sqlBuilder.getFinalTableInsertColumnHeader())
            records.forEach { record ->
                sqlBuilder.populateStatement(statement, record, sqlBuilder.finalTableSchema)
                statement.addBatch()
            }
            statement.executeLargeBatch()
            connection.commit()
        }
        return SimpleBatch(Batch.State.COMPLETE)
    }

    private fun ensureTableExists(dataSource: DataSource) {
        try {
            // TODO leverage preparedStatement instead of createStatement
            dataSource.connection.use { connection ->
                connection.createStatement().use { statement ->
                    statement.executeUpdate(sqlBuilder.createFinalSchemaIfNotExists())
                }
                connection.createStatement().use { statement ->
                    statement.executeUpdate(sqlBuilder.createFinalTableIfNotExists())
                }
                val alterStatement =
                    connection.prepareStatement(GET_EXISTING_SCHEMA_QUERY.trimIndent()).use {
                        statement ->
                        val existingSchema = sqlBuilder.getExistingSchema(statement)
                        val expectedSchema = sqlBuilder.getSchema()
                        sqlBuilder.alterTableIfNeeded(
                            existingSchema = existingSchema,
                            expectedSchema = expectedSchema,
                        )
                    }
                alterStatement?.let {
                    connection.createStatement().use { statement ->
                        statement.executeUpdate(alterStatement)
                    }
                }
            }
        } catch (ex: Exception) {
            log.error(ex) { ex.message }
            throw ex
        }
    }

    private fun truncatePreviousGenerations(dataSource: DataSource) {
        // TODO this can be improved to avoid attempting to truncate the data for each sync
        dataSource.connection.use { connection ->
            connection.createStatement().use { statement ->
                statement.executeUpdate(
                    sqlBuilder.deletePreviousGenerations(stream.minimumGenerationId)
                )
            }
        }
    }
}
