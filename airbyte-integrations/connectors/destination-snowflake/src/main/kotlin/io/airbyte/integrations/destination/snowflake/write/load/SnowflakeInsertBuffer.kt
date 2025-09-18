/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.snowflake.write.load

import com.google.common.annotations.VisibleForTesting
import io.airbyte.cdk.load.data.AirbyteValue
import io.airbyte.cdk.load.data.csv.toCsvValue
import io.airbyte.cdk.load.orchestration.db.TableName
import io.airbyte.integrations.destination.snowflake.client.SnowflakeAirbyteClient
import io.airbyte.integrations.destination.snowflake.sql.QUOTE
import io.github.oshai.kotlinlogging.KotlinLogging
import java.io.File
import java.io.FileOutputStream
import java.nio.file.Path
import kotlin.io.path.bufferedWriter
import kotlin.io.path.deleteIfExists
import kotlin.io.path.pathString
import org.apache.commons.csv.CSVFormat
import org.apache.commons.csv.CSVPrinter

private val logger = KotlinLogging.logger {}

internal val CSV_FORMAT = CSVFormat.DEFAULT

class SnowflakeInsertBuffer(
    private val tableName: TableName,
    private val columns: List<String>,
    private val snowflakeClient: SnowflakeAirbyteClient
) {

    @VisibleForTesting internal var csvFilePath: Path? = null

    @VisibleForTesting internal var recordCount = 0

    fun accumulate(recordFields: Map<String, AirbyteValue>) {
        if (csvFilePath == null) {
            csvFilePath = createCsvFile()
        }

        writeToCsvFile(csvFilePath, recordFields)

        recordCount++
    }

    suspend fun flush() {
        csvFilePath?.let { filePath ->
            try {
                logger.info { "Beginning insert into ${tableName.toPrettyString(quote = QUOTE)}" }
                // Next, put the CSV file into the staging table
                snowflakeClient.putInStage(tableName, filePath.pathString)
                // Finally, copy the data from the staging table to the final table
                snowflakeClient.copyFromStage(tableName)
                logger.info {
                    "Finished insert of $recordCount row(s) into ${tableName.toPrettyString(quote = QUOTE)}"
                }
            } catch (e: Exception) {
                logger.error(e) { "Unable to flush accumulated data." }
            } finally {
                filePath.deleteIfExists()
                csvFilePath = null
                recordCount = 0
            }
        }
            ?: logger.warn { "CSV file path is not set: nothing to upload to staging." }
    }

    private fun createCsvFile(): Path {
        val csvFile = File.createTempFile("snowflake", ".csv")
        csvFile.deleteOnExit()
        return csvFile.toPath()
    }

    private fun writeToCsvFile(csvFilePath: Path?, record: Map<String, AirbyteValue>) {
        csvFilePath?.let { filePath ->
            FileOutputStream(filePath.pathString, true).bufferedWriter(Charsets.UTF_8).use { writer
                ->
                val printer = CSVPrinter(writer, CSV_FORMAT)
                printer.use {
                    val csvRecord =
                        columns.map { columnName ->
                            if (record.containsKey(columnName)) record[columnName].toCsvValue()
                            else ""
                        }
                    printer.printRecord(csvRecord)
                }
            }
        }
    }
}
