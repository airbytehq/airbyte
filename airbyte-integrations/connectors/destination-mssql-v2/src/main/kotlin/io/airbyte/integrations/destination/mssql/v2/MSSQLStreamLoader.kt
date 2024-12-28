package io.airbyte.integrations.destination.mssql.v2

import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.message.Batch
import io.airbyte.cdk.load.message.DestinationFile
import io.airbyte.cdk.load.message.DestinationRecord
import io.airbyte.cdk.load.message.SimpleBatch
import io.airbyte.cdk.load.write.StreamLoader
import javax.sql.DataSource

class MSSQLStreamLoader(
    private val dataSource: DataSource,
    override val stream: DestinationStream,
    private val sqlBuilder: MSSQLQueryBuilder,
) : StreamLoader {

    override suspend fun processRecords(
        records: Iterator<DestinationRecord>,
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

    override suspend fun processFile(file: DestinationFile): Batch {
        TODO("Not yet implemented")
    }
}
