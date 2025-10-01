/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.snowflake.write.load

import com.google.common.annotations.VisibleForTesting
import io.airbyte.cdk.load.data.AirbyteValue
import io.airbyte.cdk.load.orchestration.db.TableName
import io.airbyte.integrations.destination.snowflake.client.SnowflakeAirbyteClient
import io.airbyte.integrations.destination.snowflake.spec.SnowflakeConfiguration
import io.airbyte.integrations.destination.snowflake.sql.QUOTE
import io.github.oshai.kotlinlogging.KotlinLogging
import java.io.File
import java.nio.file.Path
import kotlin.io.path.deleteIfExists
import kotlin.io.path.pathString
import org.apache.commons.csv.CSVFormat
import org.apache.commons.csv.CSVPrinter

private val logger = KotlinLogging.logger {}

internal val CSV_FORMAT = CSVFormat.DEFAULT
internal const val DEFAULT_FLUSH_LIMIT = 1000

class SnowflakeInsertBuffer(
    private val tableName: TableName,
    val columns: List<String>,
    private val snowflakeClient: SnowflakeAirbyteClient,
    val snowflakeConfiguration: SnowflakeConfiguration,
    private val flushLimit: Int = DEFAULT_FLUSH_LIMIT,
) {

    @VisibleForTesting internal var csvFilePath: Path? = null

    @VisibleForTesting internal var recordCount = 0

    private var csvPrinter: CSVPrinter? = null

    private val snowflakeRecordFormatter: SnowflakeRecordFormatter =
        when (snowflakeConfiguration.legacyRawTablesOnly) {
            true -> SnowflakeRawRecordFormatter(columns)
            else -> SnowflakeSchemaRecordFormatter(columns)
        }

    fun accumulate(recordFields: Map<String, AirbyteValue>) {
        if (csvFilePath == null) {
            val csvFile = createCsvFile()
            csvFilePath = csvFile.toPath()
            csvPrinter = CSVPrinter(csvFile.bufferedWriter(Charsets.UTF_8), CSV_FORMAT)
        }

        writeToCsvFile(recordFields)
    }

    suspend fun flush() {
        csvFilePath?.let { filePath ->
            try {
                csvPrinter?.flush()
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
                csvPrinter?.close()
                csvPrinter = null
                csvFilePath = null
                recordCount = 0
            }
        }
            ?: logger.warn { "CSV file path is not set: nothing to upload to staging." }
    }

    private fun createCsvFile(): File {
        val csvFile = File.createTempFile("snowflake", ".csv")
        csvFile.deleteOnExit()
        return csvFile
    }

    private fun writeToCsvFile(record: Map<String, AirbyteValue>) {
        csvPrinter?.let {
            it.printRecord(snowflakeRecordFormatter.format(record))
            recordCount++
            if ((recordCount % flushLimit) == 0) {
                it.flush()
            }
        }
    }
}
