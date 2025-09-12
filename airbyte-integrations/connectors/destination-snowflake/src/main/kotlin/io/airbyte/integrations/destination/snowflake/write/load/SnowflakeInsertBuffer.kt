/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.snowflake.write.load

import com.google.common.annotations.VisibleForTesting
import io.airbyte.cdk.load.data.AirbyteValue
import io.airbyte.cdk.load.data.csv.toCsvValue
import io.airbyte.cdk.load.orchestration.db.TableName
import io.airbyte.integrations.destination.snowflake.client.CSV_FIELD_DELIMITER
import io.airbyte.integrations.destination.snowflake.client.CSV_RECORD_DELIMITER
import io.airbyte.integrations.destination.snowflake.client.SnowflakeAirbyteClient
import io.airbyte.integrations.destination.snowflake.client.SnowflakeDirectLoadSqlGenerator.Companion.QUOTE
import io.github.oshai.kotlinlogging.KotlinLogging
import java.io.File
import java.nio.file.Files
import java.nio.file.Path
import java.util.concurrent.BlockingQueue
import java.util.concurrent.LinkedBlockingQueue

private val logger = KotlinLogging.logger {}

class SnowflakeInsertBuffer(
    private val tableName: TableName,
    private val columns: List<String>,
    private val snowflakeClient: SnowflakeAirbyteClient
) {

    @VisibleForTesting
    internal val recordQueue: BlockingQueue<Map<String, AirbyteValue>> = LinkedBlockingQueue()

    fun accumulate(recordFields: Map<String, AirbyteValue>) {
        logger.info { "Accumulating $recordFields" }
        recordQueue.offer(recordFields)
    }

    suspend fun flush() {
        var tempFilePath = ""
        try {
            logger.info { "Beginning insert into ${tableName.toPrettyString(quote=QUOTE)}" }
            // First, get all accumulated records
            val records = mutableListOf<Map<String, AirbyteValue>>()
            recordQueue.drainTo(records)
            // Next, generate a CSV file from the accumulated records
            tempFilePath = generateCsvFile(records)
            // Next, put the CSV file into the staging table
            snowflakeClient.putInStage(tableName, tempFilePath)
            // Finally, copy the data from the staging table to the final table
            snowflakeClient.copyFromStage(tableName)
            logger.info {
                "Finished insert of ${records.size} row(s) into ${tableName.toPrettyString(quote=QUOTE)}"
            }
        } finally {
            if (tempFilePath.isNotBlank()) {
                // Eagerly delete temp file to avoid build up during long syncs.
                Files.deleteIfExists(Path.of(tempFilePath))
            }
        }
    }

    private fun generateCsvFile(records: List<Map<String, AirbyteValue>>): String {
        val csvFile = File.createTempFile("snowflake", ".csv")
        csvFile.deleteOnExit()
        csvFile.bufferedWriter(Charsets.UTF_8).use { writer ->
            records.forEach { record ->
                writer.write(
                    "${columns.map { columnName -> record[columnName].toCsvValue()}.joinToString(CSV_FIELD_DELIMITER)}$CSV_RECORD_DELIMITER"
                )
            }
        }
        return csvFile.absolutePath
    }
}
