/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.mssql.v2

import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.message.Batch
import io.airbyte.cdk.load.message.DestinationRecordAirbyteValue
import io.airbyte.cdk.load.message.SimpleBatch
import javax.sql.DataSource

class MSSQLStreamLoader(
    dataSource: DataSource,
    override val stream: DestinationStream,
    sqlBuilder: MSSQLQueryBuilder,
) : AbstractMSSQLStreamLoader(dataSource, stream, sqlBuilder) {

    private val recordCommitBatchSize = 5_000

    override suspend fun processRecords(
        records: Iterator<DestinationRecordAirbyteValue>,
        totalSizeBytes: Long,
        endOfStream: Boolean
    ): Batch {
        dataSource.connection.use { connection ->
            connection.autoCommit = false

            // Prepare the insert statement once
            sqlBuilder.getFinalTableInsertColumnHeader().executeUpdate(connection) { statement ->
                records.withIndex().forEach { (index, record) ->
                    // Populate placeholders for each record
                    sqlBuilder.populateStatement(statement, record, sqlBuilder.finalTableSchema)
                    statement.addBatch()

                    // Periodically execute the batch to avoid too-large batches
                    if (index > 0 && index % recordCommitBatchSize == 0) {
                        statement.executeBatch()
                        connection.commit()
                    }
                }

                // Execute remaining records if any
                statement.executeBatch()
            }

            // If CDC is enabled, remove stale records
            if (sqlBuilder.hasCdc) {
                sqlBuilder.deleteCdc(connection)
            }

            connection.commit()
        }

        // Indicate that the batch has been completely processed
        return SimpleBatch(Batch.State.COMPLETE)
    }
}
