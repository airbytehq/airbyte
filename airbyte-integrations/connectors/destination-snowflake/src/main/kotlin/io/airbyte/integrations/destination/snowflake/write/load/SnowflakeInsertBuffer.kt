/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.snowflake.write.load

import com.google.common.annotations.VisibleForTesting
import de.siegmar.fastcsv.writer.CsvWriter
import de.siegmar.fastcsv.writer.LineDelimiter
import de.siegmar.fastcsv.writer.QuoteStrategies
import io.airbyte.cdk.load.data.AirbyteValue
import io.airbyte.cdk.load.orchestration.db.TableName
import io.airbyte.integrations.destination.snowflake.client.SnowflakeAirbyteClient
import io.airbyte.integrations.destination.snowflake.spec.SnowflakeConfiguration
import io.airbyte.integrations.destination.snowflake.sql.QUOTE
import io.airbyte.integrations.destination.snowflake.sql.SnowflakeColumnUtils
import io.github.oshai.kotlinlogging.KotlinLogging
import java.io.File
import java.nio.file.Path
import java.util.zip.GZIPOutputStream
import kotlin.io.path.deleteIfExists
import kotlin.io.path.pathString

private val logger = KotlinLogging.logger {}

internal const val CSV_FIELD_SEPARATOR = ','
internal const val CSV_QUOTE_CHARACTER = '"'
internal val CSV_LINE_DELIMITER = LineDelimiter.LF
internal const val DEFAULT_FLUSH_LIMIT = 1000

class SnowflakeInsertBuffer(
    private val tableName: TableName,
    val columns: List<String>,
    private val snowflakeClient: SnowflakeAirbyteClient,
    val snowflakeConfiguration: SnowflakeConfiguration,
    private val snowflakeColumnUtils: SnowflakeColumnUtils,
    private val flushLimit: Int = DEFAULT_FLUSH_LIMIT,
) {

    @VisibleForTesting internal var csvFilePath: Path? = null

    @VisibleForTesting internal var recordCount = 0

    @VisibleForTesting internal var csvWriter: CsvWriter? = null

    private val csvWriterBuilder =
        CsvWriter.builder()
            .fieldSeparator(CSV_FIELD_SEPARATOR)
            .quoteCharacter(CSV_QUOTE_CHARACTER)
            .lineDelimiter(CSV_LINE_DELIMITER)
            .quoteStrategy(QuoteStrategies.REQUIRED)

    private val snowflakeRecordFormatter: SnowflakeRecordFormatter =
        when (snowflakeConfiguration.legacyRawTablesOnly) {
            true -> SnowflakeRawRecordFormatter(columns, snowflakeColumnUtils)
            else -> SnowflakeSchemaRecordFormatter(columns, snowflakeColumnUtils)
        }

    fun accumulate(recordFields: Map<String, AirbyteValue>) {
        if (csvFilePath == null) {
            val csvFile = createCsvFile()
            csvFilePath = csvFile.toPath()
            csvWriter = csvWriterBuilder.build(GZIPOutputStream(csvFile.outputStream()))
        }

        writeToCsvFile(recordFields)
    }

    suspend fun flush() {
        csvFilePath?.let { filePath ->
            try {
                // Flush and close the CSV write to ensure that any pending writes are written
                // to the file AND that any proper end of file markers are written by the close
                csvWriter?.flush()
                csvWriter?.close()
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
                throw e
            } finally {
                filePath.deleteIfExists()
                csvWriter = null
                csvFilePath = null
                recordCount = 0
            }
        }
            ?: logger.warn { "CSV file path is not set: nothing to upload to staging." }
    }

    private fun createCsvFile(): File {
        val csvFile = File.createTempFile("snowflake", ".csv.gz")
        csvFile.deleteOnExit()
        return csvFile
    }

    private fun writeToCsvFile(record: Map<String, AirbyteValue>) {
        csvWriter?.let {
            it.writeRecord(snowflakeRecordFormatter.format(record).map { col -> col.toString() })
            recordCount++
            if ((recordCount % flushLimit) == 0) {
                it.flush()
            }
        }
    }
}
